"""Console log handler."""
from enum import Enum
import sys


class DebugFlag(Enum):
    """Debug flags."""

    QUIET = 0
    INFO = 1
    DEBUG = 2


class ConsoleFlags:
    """Console flags."""
    _debug_flag = DebugFlag.INFO

    def set_debug_flag(self, debug_flag: DebugFlag):
        """Set debug flag."""
        ConsoleFlags._debug_flag = debug_flag

    def get_debug_flag(self):
        """Get debug flag."""
        return ConsoleFlags._debug_flag


def set_debug(flag: DebugFlag):
    """Set debug flag."""
    ConsoleFlags().set_debug_flag(flag)


def trace(*args, **kwargs):
    """Trace."""
    if ConsoleFlags().get_debug_flag() in (DebugFlag.QUIET, DebugFlag.INFO):
        return
    print(*args, file=sys.stderr, **kwargs)


def error(*args, **kwargs):
    """Error message."""
    if ConsoleFlags().get_debug_flag() == DebugFlag.QUIET:
        return
    print(*args, file=sys.stderr, **kwargs)


def out(*args, **kwargs):
    """Output to stdout."""
    print(*args, file=sys.stdout, **kwargs)
