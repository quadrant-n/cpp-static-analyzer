"""Static analyzer command manager."""
import subprocess as sproc
import threading
import os.path
import hashlib

import cpp_static_analyzer.compile_db as cdb
import cpp_static_analyzer.config as cfg


def _execute_clang_tidy(command, config: cfg.Config) -> tuple:
    """Execute clang-tidy."""
    entry = cdb.Entry(command)

    # Compose command line for clang-tidy.
    exec_cmd = []

    exec_cmd.append(config.clang_tidy)
    exec_cmd.append('--quiet')

    if config.header_filter != '':
        exec_cmd.append(f'--header-filter={config.header_filter}')

    exec_cmd.append(f'--checks={config.checks}')

    for additional_option in config.additional_options:
        exec_cmd.append(additional_option)

    input_path = entry.get_input_path()
    path_converter = config.get_path_converter()
    conv_input_path = cdb.convert_path(input_path,
                                       path_converter)
    exec_cmd.append(f'{conv_input_path}')

    exec_cmd.append('--')

    arguments = entry.get_arguments()
    for arg in arguments:
        conv_str = cdb.convert_path(arg, path_converter)
        exec_cmd.append(conv_str)

    warnings = config.get_warnings()
    for warning in warnings:
        exec_cmd.append(warning)

    proc = sproc.run(exec_cmd,
                     encoding='utf-8',
                     shell=False,
                     stdout=sproc.PIPE,
                     stderr=sproc.PIPE,
                     universal_newlines=True,
                     text=True,
                     check=True)

    return entry, proc.stdout, proc.stderr


class CommandManager:
    """Command manager object."""

    _commands = []
    _command_count = 0
    _lock = threading.Lock()
    _current_index = 0

    def __init__(self, path: str):
        self._commands = cdb.load_compile_commands(path)
        self._command_count = len(self._commands)
        self._lock = threading.Lock()
        self._current_index = 0

    def next_index(self):
        """Next index."""
        if self._current_index >= self._command_count:
            return -1
        with self._lock:
            if self._current_index < self._command_count:
                idx = self._current_index
                self._current_index += 1
            else:
                idx = -1

        return idx

    def __getitem__(self, index):
        return self._commands[index]

    def __len__(self):
        return self._command_count

    def get_current_index(self):
        """Get current index."""
        return self._current_index

    def _write_to_file(self, content, file_path):
        if len(content) > 0:
            with open(file_path, 'w', encoding="utf-8") as output_file:
                print(content, file=output_file)

    def job(self,
            config: cfg.Config,
            output_directory: str,
            error_directory: str):
        """Command executor job."""
        index = self.next_index()
        while index >= 0:
            command = self[index]

            entry, result, error = _execute_clang_tidy(command, config)

            input_path = entry.get_input_path()
            file_name = os.path.basename(input_path)
            file_id = hashlib.md5(file_name.encode('utf-8')).hexdigest()

            output_file_path = f'{output_directory}/{file_name}.{file_id}'
            error_file_path = f'{error_directory}/{file_name}.{file_id}'

            self._write_to_file(result, output_file_path)
            self._write_to_file(error, error_file_path)

            index = self.next_index()
