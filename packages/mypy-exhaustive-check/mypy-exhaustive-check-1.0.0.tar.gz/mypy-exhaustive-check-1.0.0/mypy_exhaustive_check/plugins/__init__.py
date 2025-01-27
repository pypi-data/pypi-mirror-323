from .base import BasePlugin, CheckType
from .dict_check import ExhaustiveDictPlugin

CHECK_TYPE_TO_PLUGIN: dict[CheckType, type[BasePlugin]] = {
    CheckType.DICT: ExhaustiveDictPlugin,
}

__all__ = ["CHECK_TYPE_TO_PLUGIN", "BasePlugin", "CheckType", "ExhaustiveDictPlugin"]
