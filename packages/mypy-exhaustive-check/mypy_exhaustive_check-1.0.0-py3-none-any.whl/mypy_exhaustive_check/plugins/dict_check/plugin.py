from collections.abc import Callable
from typing import Union

from mypy.nodes import MemberExpr, TupleExpr
from mypy.plugin import FunctionContext, Plugin
from mypy.types import Instance, Type

from .errors import NON_EXHAUSTIVE_ENUM_IN_DICT


class ExhaustiveDictPlugin(Plugin):
    def get_function_hook(
        self,
        fullname: str,  # noqa: ARG002 # pylint: disable=unused-argument
    ) -> Callable[[FunctionContext], Union[Type, Instance]]:
        return self

    @staticmethod
    def is_context_compatible(ctx: FunctionContext) -> bool:
        number_of_args_in_dict = 2
        if (
            not isinstance(ctx.default_return_type, Instance)
            or len(ctx.default_return_type.args) != number_of_args_in_dict
        ):
            return False

        key_type, _ = ctx.default_return_type.args

        return not (not isinstance(key_type, Instance) or not key_type.type.is_enum)

    @classmethod
    def type(cls) -> type[Plugin]:
        return cls

    def __call__(self, ctx: FunctionContext) -> Union[Type, Instance]:
        if not self.is_context_compatible(ctx):
            return ctx.default_return_type

        key_type, _ = ctx.default_return_type.args  # type: ignore

        enum_members: set[str] = set(key_type.type.names)

        if not ctx.args:
            ctx.api.fail(
                f"{NON_EXHAUSTIVE_ENUM_IN_DICT.description} "
                f"Unhandled members: {', '.join(sorted(enum_members))}",
                ctx.context,
            )
            return ctx.default_return_type

        provided_keys = set[str]()
        for argument, *_ in ctx.args:
            if not isinstance(argument, TupleExpr):
                return ctx.default_return_type

            if not isinstance(argument.items[0], MemberExpr):
                return ctx.default_return_type

            provided_keys.add(argument.items[0].name)

        missing_keys = enum_members - provided_keys
        if missing_keys:
            ctx.api.fail(
                f"{NON_EXHAUSTIVE_ENUM_IN_DICT.description} "
                f"Unhandled members: {', '.join(sorted(missing_keys))}",
                ctx.context,
                code=NON_EXHAUSTIVE_ENUM_IN_DICT,
            )

        return ctx.default_return_type


def plugin(_: str) -> type[Plugin]:
    return ExhaustiveDictPlugin
