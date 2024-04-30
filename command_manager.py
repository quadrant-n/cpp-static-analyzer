import compile_db as cdb
import threading

class CommandManager:
    def __init__(self, path: str):
        self._commands = cdb.load_compile_commands(path)
        self._command_count = len(self._commands)
        self._lock = threading.Lock()
        self._current_index = 0

    def next_index(self):
        self._lock.acquire()
        try:
            if self._current_index < self._command_count:
                idx = self._current_index
                self._current_index += 1
            else:
                idx = -1
        finally:
            self._lock.release()
            return idx

    def __getitem__(self, index):
        return self._commands[index]

    def __len__(self):
        return self._command_count
