"""Console log handler."""

from enum import Enum
import sys


class DebugFlag(Enum):
    """Debug flags."""

    QUIET = 0
    INFO = 1
    DEBUG = 2


class _ConsoleFlags:
    """Console flags."""
    _debug_flag = DebugFlag.INFO

    @classmethod
    def set_debug_flag(cls, debug_flag: DebugFlag):
        """Set debug flag."""
        cls._debug_flag = debug_flag

    @classmethod
    def get_debug_flag(cls):
        """Get debug flag."""
        return cls._debug_flag


def set_debug(flag: DebugFlag):
    """Set debug flag."""
    _ConsoleFlags.set_debug_flag(flag)


def trace(*args, **kwargs):
    """Trace."""
    if _ConsoleFlags.get_debug_flag() in (DebugFlag.QUIET, DebugFlag.INFO):
        return
    print(*args, file=sys.stderr, **kwargs)


def error(*args, **kwargs):
    """Error message."""
    if _ConsoleFlags.get_debug_flag() == DebugFlag.QUIET:
        return
    print(*args, file=sys.stderr, **kwargs)
