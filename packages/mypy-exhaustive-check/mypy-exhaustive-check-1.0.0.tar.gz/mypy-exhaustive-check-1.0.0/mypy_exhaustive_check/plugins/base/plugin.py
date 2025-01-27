from collections.abc import Callable
from typing import Protocol, Union

from mypy.plugin import FunctionContext, Plugin
from mypy.types import Instance, Type


class BasePlugin(Protocol):
    def get_function_hook(
        self, fullname: str
    ) -> Callable[[FunctionContext], Union[Type, Instance]]: ...

    @staticmethod
    def is_context_compatible(ctx: FunctionContext) -> bool: ...

    @classmethod
    def type(cls) -> type[Plugin]: ...

    def __call__(self, ctx: FunctionContext) -> Union[Type, Instance]: ...
