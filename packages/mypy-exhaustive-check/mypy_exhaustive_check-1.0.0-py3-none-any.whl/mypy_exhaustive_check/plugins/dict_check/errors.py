from typing import Final

from mypy.errorcodes import MISC, ErrorCode

NON_EXHAUSTIVE_ENUM_IN_DICT: Final[ErrorCode] = ErrorCode(
    "dict-not-exhaustive",
    "Keys within dictionary do not exhaustively handle all enum members.",
    "General",
    sub_code_of=MISC,
)
