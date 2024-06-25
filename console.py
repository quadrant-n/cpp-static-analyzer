from enum import Enum
import sys

class DebugFlag(Enum):
    Quiet = 0
    Info = 1
    Debug = 2

_debug_flag = DebugFlag.Info

def set_debug(flag: DebugFlag):
    _debug_flag = flag

def trace(*args, **kwargs):
    if _debug_flag == DebugFlag.Quiet or _debug_flag == DebugFlag.Info:
        return
    print(*args, file=sys.stderr, **kwargs)

def error(*args, **kwargs):
    if _debug_flag == DebugFlag.Quiet:
        return
    print(*args, file=sys.stderr, **kwargs)

def out(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)
