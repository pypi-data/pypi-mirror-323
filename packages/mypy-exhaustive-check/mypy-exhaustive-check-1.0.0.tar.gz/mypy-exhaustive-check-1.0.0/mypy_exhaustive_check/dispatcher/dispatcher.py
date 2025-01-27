from collections.abc import Callable
from typing import Union

from mypy.plugin import FunctionContext, Plugin
from mypy.types import Instance, Type

from mypy_exhaustive_check.plugins import CHECK_TYPE_TO_PLUGIN, BasePlugin


class PluginDispatcher(Plugin):
    def get_function_hook(
        self,
        fullname: str,  # noqa: ARG002 # pylint: disable=unused-argument
    ) -> Callable[[FunctionContext], Union[Type, Instance]]:
        return self

    def __call__(self, ctx: FunctionContext) -> Union[Type, Instance]:
        compatible_plugins = list[type[BasePlugin]]()

        for plugin in CHECK_TYPE_TO_PLUGIN.values():
            if not plugin.is_context_compatible(ctx):
                continue
            compatible_plugins.append(plugin)

        for plugin in compatible_plugins:
            plugin(self.options)(ctx)  # type: ignore

        return ctx.default_return_type
