import logging
from collections import deque
from datetime import datetime
from functools import partial, reduce
from operator import add
from typing import List, Optional, Union

from toolz import concat, pipe
from toolz.curried import filter, map, remove

from ..config.constants import (
    ASSISTANT,
    FORMATTING_INSTRUCT,
    SYSTEM,
    SYSTEM_INSTRUCTION_LABEL,
    SYSTEM_INSTRUCTION_LABEL_END,
    TOOL,
    USER,
    inline_tool_instruct,
    tool,
)
from ..config.ctx import ElroyContext
from ..db.db_models import Goal, Memory
from ..llm.prompts import summarize_conversation
from ..repository.data_models import ContextMessage
from ..repository.embeddable import (
    add_to_current_context_by_name,
    drop_from_context_by_name,
)
from ..repository.memories.operations import formulate_memory
from ..repository.message import (
    get_context_messages,
    is_system_instruction,
    replace_context_messages,
)
from ..tools.user_preferences import get_or_create_user_preference
from ..utils.clock import get_utc_now
from ..utils.utils import datetime_to_string, logged_exec_time


def get_refreshed_system_message(ctx: ElroyContext, context_messages: List[ContextMessage]) -> ContextMessage:
    from ..llm.persona import get_persona

    user_preference = get_or_create_user_preference(ctx)

    assert isinstance(context_messages, list)
    if len(context_messages) > 0 and context_messages[0].role == SYSTEM:
        # skip existing system message if it is still in context.
        context_messages = context_messages[1:]

    if len([msg for msg in context_messages if msg.role == USER]) == 0:
        conversation_summary = None
    else:
        conversation_summary = pipe(
            context_messages,
            lambda msgs: format_context_messages(msgs, user_preference.preferred_name),
            partial(summarize_conversation, ctx.chat_model),
            lambda _: f"<conversational_summary>{_}</conversational_summary>",
            str,
        )

    return pipe(
        [
            SYSTEM_INSTRUCTION_LABEL,
            f"<persona>{get_persona(ctx)}</persona>",
            conversation_summary,
            FORMATTING_INSTRUCT,
            inline_tool_instruct(ctx.tool_registry.get_schemas()) if ctx.chat_model.inline_tool_calls else None,
            "From now on, converse as your persona.",
            SYSTEM_INSTRUCTION_LABEL_END,
        ],  # type: ignore
        remove(lambda _: _ is None),
        list,
        "\n".join,
        lambda x: ContextMessage(role=SYSTEM, content=x, chat_model=None),
    )


def format_message(message: ContextMessage, user_preferred_name: Optional[str]) -> List[str]:
    datetime_str = datetime_to_string(message.created_at)
    if message.role == SYSTEM:
        return [f"SYSTEM ({datetime_str}): {message.content}"]
    elif message.role == USER:
        user_name = user_preferred_name.upper() if user_preferred_name else "USER"

        return [f"{user_name} ({datetime_str}): {message.content}"]
    elif message.role == ASSISTANT:
        msgs = []

        if message.content:
            msgs.append(f"ELROY ({datetime_str}): {message.content}")
        if message.tool_calls:
            pipe(
                message.tool_calls,
                map(lambda x: x.function),
                map(lambda x: f"ELROY TOOL CALL REQUEST ({datetime_str}): function name: {x['name']}, arguments: {x['arguments']}"),
                list,
                msgs.extend,
            )
        if not message.content and not message.tool_calls:
            raise ValueError(f"Expected either message text or tool call: {message}")
        return msgs
    elif message.role == TOOL:
        return [f"TOOL CALL RESULT ({datetime_str}): {message.content}"]
    else:
        logging.warning(f"Cannot format message: {message}")
        return []


# passing message content is an approximation, tool calls may not be accounted for.
def count_tokens(chat_model_name: str, context_messages: Union[List[ContextMessage], ContextMessage]) -> int:
    from litellm.utils import token_counter

    if isinstance(context_messages, ContextMessage):
        context_messages = [context_messages]

    if not context_messages:
        return 0
    else:
        return pipe(
            context_messages,
            map(lambda x: {"role": x.role, "content": x.content}),
            list,
            lambda x: token_counter(chat_model_name, messages=x),
        )  # type: ignore


def is_context_refresh_needed(ctx: ElroyContext) -> bool:
    context_messages = get_context_messages(ctx)

    if sum(1 for m in context_messages if m.role == USER) == 0:
        logging.info("No user messages in context, skipping context refresh")
        return False

    token_count = pipe(
        context_messages,
        remove(lambda _: _.content is None),
        map(partial(count_tokens, ctx.chat_model.name)),
        lambda seq: reduce(add, seq, 0),
    )
    assert isinstance(token_count, int)

    if token_count > ctx.context_refresh_trigger_tokens:
        logging.info(f"Token count {token_count} exceeds threshold {ctx.context_refresh_trigger_tokens}")
        return True
    else:
        logging.info(f"Token count {token_count} does not exceed threshold {ctx.context_refresh_trigger_tokens}")
        return False


def compress_context_messages(ctx: ElroyContext, context_messages: List[ContextMessage]) -> List[ContextMessage]:
    """
    Compresses messages in the context window by summarizing old messages, while keeping new messages intact.
    """
    system_message, prev_messages = context_messages[0], context_messages[1:]

    assert is_system_instruction(system_message)
    assert not any(is_system_instruction(msg) for msg in prev_messages)

    current_token_count = count_tokens(ctx.chat_model.name, system_message)

    kept_messages = deque()

    # iterate through non-system context messages in reverse order
    # we keep the most current messages that are fresh enough to be relevant
    for msg in reversed(prev_messages):  # iterate in reverse order
        msg_created_at = msg.created_at
        assert isinstance(msg_created_at, datetime)

        candidate_message_count = count_tokens(ctx.chat_model.name, msg)

        if len(kept_messages) > 0 and kept_messages[0].role == TOOL:
            # if the last message kept was a tool call, we must keep the corresponding assistant message that came before it.
            kept_messages.appendleft(msg)
            current_token_count += candidate_message_count
            continue

        if current_token_count > ctx.context_refresh_target_tokens:
            break
        elif msg_created_at < get_utc_now() - ctx.max_in_context_message_age:
            logging.info(f"Dropping old message {msg.id}")
            continue
        else:
            kept_messages.appendleft(msg)
            current_token_count += candidate_message_count

    # Keep system message first, but reverse the rest to maintain chronological order
    return [system_message] + list(kept_messages)


def format_context_messages(context_messages: List[ContextMessage], user_preferred_name: Optional[str]) -> str:
    convo_range = pipe(
        context_messages,
        filter(lambda _: _.role == USER),
        map(lambda _: _.created_at),
        list,
        lambda l: f"Messages from {datetime_to_string(min(l))} to {datetime_to_string(max(l))}" if l else "No messages in context",
    )

    return (
        pipe(
            context_messages,
            filter(
                lambda _: _.content or _.tool_calls or _.role != ASSISTANT
            ),  # TODO: Determine why these messages are making it into context
            map(lambda msg: format_message(msg, user_preferred_name)),
            concat,
            list,
            "\n".join,
            str,
        )
        + convo_range
    )  # type: ignore


def replace_system_instruction(context_messages: List[ContextMessage], new_system_message: ContextMessage) -> List[ContextMessage]:
    """
    Note that this removes any prior system instruction messages, even if they are not in first position
    """
    return pipe(
        context_messages,
        remove(is_system_instruction),
        list,
        lambda x: [new_system_message] + x,
    )


@logged_exec_time
async def context_refresh(ctx: ElroyContext) -> None:
    from ..repository.memories.operations import create_memory
    from ..tools.user_preferences import get_user_preferred_name

    context_messages = get_context_messages(ctx)
    user_preferred_name = get_user_preferred_name(ctx)

    # We calculate an archival memory, then persist it, then use it to calculate entity facts, then persist those.
    memory_title, memory_text = await formulate_memory(ctx.chat_model, user_preferred_name, context_messages)
    create_memory(ctx, memory_title, memory_text)

    pipe(
        get_refreshed_system_message(ctx, context_messages),
        partial(replace_system_instruction, context_messages),
        partial(compress_context_messages, ctx),
        partial(replace_context_messages, ctx),
    )


@tool
def add_memory_to_current_context(ctx: ElroyContext, memory_name: str) -> str:
    """Adds memory with the given name to the current conversation context

    Args:
        context (ElroyContext): context obj
        memory_name (str): The name of the memory to add

    Returns:
        str: The result of the attempt to add the memory to current context.
    """
    return add_to_current_context_by_name(ctx, memory_name, Memory)


@tool
def add_goal_to_current_context(ctx: ElroyContext, goal_name: str) -> str:
    """Adds goal with the given name to the current conversation context

    Args:
        context (ElroyContext): context obj
        goal_name (str): The name of the goal to add

    Returns:
        str: The result of the attempt to add the goal to current context.
    """
    return add_to_current_context_by_name(ctx, goal_name, Goal)


@tool
def drop_goal_from_current_context(ctx: ElroyContext, goal_name: str) -> str:
    """Drops the goal with the given name. Does NOT delete or mark the goal completed.

    Args:
        context (ElroyContext): context obj
        goal_name (str): Name of the goal

    Returns:
        str: Information for the goal with the given name
    """
    return drop_from_context_by_name(ctx, goal_name, Goal)


@tool
def drop_memory_from_current_context(ctx: ElroyContext, memory_name: str) -> str:
    """Drops the memory with the given name. Does NOT delete the memory.

    Args:
        context (ElroyContext): context obj
        memory_name (str): Name of the memory

    Returns:
        str: Information for the memory with the given name
    """
    return drop_from_context_by_name(ctx, memory_name, Memory)
