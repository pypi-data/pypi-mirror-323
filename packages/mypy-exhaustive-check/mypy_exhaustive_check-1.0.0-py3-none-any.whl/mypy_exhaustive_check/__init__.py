from mypy.plugin import Plugin

from .dispatcher import PluginDispatcher


def plugin(_: str) -> type[Plugin]:
    return PluginDispatcher


__all__ = ["PluginDispatcher", "plugin"]

__version__ = "1.0.0"
