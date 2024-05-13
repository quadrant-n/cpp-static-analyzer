import compile_db as cdb
import threading
import time
import config as cfg
import subprocess as sproc
import os.path
import hashlib

class CommandManager:
    def __init__(self, path: str):
        self._commands = cdb.load_compile_commands(path)
        self._command_count = len(self._commands)
        self._lock = threading.Lock()
        self._current_index = 0

    def next_index(self):
        if self._current_index >= self._command_count:
            return -1
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

    def get_current_index(self):
        return self._current_index

    def job(command_manager, config: cfg.Config, output_directory: str):
        index = command_manager.next_index()
        while index >= 0:
            command = command_manager[index]
            entry = cdb.Entry(command)

            # Compose command line for clang-tidy.
            exec_cmd = []

            exec_cmd.append(config.clang_tidy)
            exec_cmd.append('--quiet')
            exec_cmd.append('--header-filter=*')
            exec_cmd.append(f'--checks={config.checks}')

            conv_input_path = cdb.convert_path(entry.input_path,
                                               config.path_converter)
            exec_cmd.append(f'{conv_input_path}')

            exec_cmd.append('--')

            for arg in entry.arguments:
                conv_str = cdb.convert_path(arg, config.path_converter)
                exec_cmd.append(conv_str)

            file_name = os.path.basename(entry.input_path)
            file_id = hashlib.md5(entry.input_path.encode('utf-8')).hexdigest()
            output_file_path = f'{output_directory}/{file_name}.{file_id}'


            proc = sproc.run(exec_cmd,
                             encoding='utf-8',
                             shell=True,
                             stdout=sproc.PIPE,
                             stderr=sproc.DEVNULL,
                             text=True)

            if len(proc.stdout) > 0:
                with open(output_file_path, 'w') as output_file:
                    print(proc.stdout, file=output_file)

            index = command_manager.next_index()
