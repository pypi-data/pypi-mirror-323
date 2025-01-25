from inspect import Parameter, signature
from typing import Any, Optional, Union, get_args, get_origin

from toolz import pipe
from toolz.curried import map, valfilter

from ..config.constants import RecoverableToolError
from ..config.ctx import ElroyContext
from ..io.cli import CliIO
from ..system_commands import SYSTEM_COMMANDS


async def invoke_system_command(ctx: ElroyContext, msg: str) -> str:
    """
    Takes user input and executes a system command. For commands with a single non-context argument,
    executes directly with provided argument. For multi-argument commands, prompts for each argument.
    """
    io = ctx.io
    assert isinstance(io, CliIO)
    if msg.startswith("/"):
        msg = msg[1:]

    command = msg.split(" ")[0]
    input_arg = " ".join(msg.split(" ")[1:])

    func = next((f for f in SYSTEM_COMMANDS if f.__name__ == command), None)

    if not func:
        raise RecoverableToolError(f"Invalid command: {command}. Use /help for a list of valid commands")

    params = list(signature(func).parameters.values())

    # Count non-context parameters
    non_ctx_params = [p for p in params if p.annotation != ElroyContext]

    func_args = {}

    # If exactly one non-context parameter and we have input, execute directly
    if len(non_ctx_params) == 1 and input_arg:
        func_args["ctx"] = ctx
        func_args[non_ctx_params[0].name] = _get_casted_value(non_ctx_params[0], input_arg)
        return pipe(
            func_args,
            valfilter(lambda _: _ is not None and _ != ""),
            lambda _: func(**_),
        )  # type: ignore

    # Otherwise, fall back to interactive parameter collection
    input_used = False
    for param in params:
        if param.annotation == ElroyContext:
            func_args[param.name] = ctx
        elif input_arg and not input_used:
            argument = await io.prompt_user(_get_prompt_for_param(param), prefill=input_arg)
            func_args[param.name] = _get_casted_value(param, argument)
            input_used = True
        elif input_used or not input_arg:
            argument = await io.prompt_user(_get_prompt_for_param(param))
            func_args[param.name] = _get_casted_value(param, argument)

    return pipe(
        func_args,
        valfilter(lambda _: _ is not None and _ != ""),
        lambda _: func(**_),
    )  # type: ignore


def _is_optional(param: Parameter) -> bool:
    return get_origin(param.annotation) is Union and type(None) in get_args(param.annotation)


def _get_casted_value(parameter: Parameter, str_value: str) -> Optional[Any]:
    if not str_value:
        return None
    # detect if it is union
    if _is_optional(parameter):
        arg_type = get_args(parameter.annotation)[0]
    else:
        arg_type = parameter.annotation
    return arg_type(str_value)


def _get_prompt_for_param(param: Parameter) -> str:
    prompt_title = pipe(
        param.name,
        lambda x: x.split("_"),
        map(str.capitalize),
        " ".join,
    )

    if _is_optional(param):
        prompt_title += " (optional)"

    return prompt_title + ">"
