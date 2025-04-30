"""Static analyzer command manager."""

import subprocess as sproc
import threading
import os.path
import hashlib
import pickle

import cpp_static_analyzer.compile_db as cdb
import cpp_static_analyzer.config as cfg
import cpp_static_analyzer.console as con


class CommandManager:
    """Command manager object."""

    def __init__(self):
        self._commands = []
        self._command_count = 0
        self._lock = threading.Lock()
        self._current_index = 0
        self._command_hashmap = {}

    @classmethod
    def create_from_json(cls, file_path: str):
        """Create from JSON."""
        commands = cdb.Entry.load_compile_commands(file_path)
        command_manager = CommandManager()
        command_manager._set_using_commands(commands)
        if len(command_manager) == 0:
            con.error('No compile command found.')
        return command_manager

    @classmethod
    def create_from_pkl(cls, file_path: str):
        """Create from PKL file."""
        command_manager = CommandManager()
        try:
            with open(file_path, 'rb') as pkl_file_handle:
                command_hashmap = pickle.load(pkl_file_handle)
                command_manager._set_using_command_hashmap(command_hashmap)
                if len(command_manager) == 0:
                    con.error('No compile command found.')
        except OSError:
            con.error(f'Error reading data from {file_path}.')

        return command_manager

    def _set_using_commands(self, commands: list):
        self._commands = commands
        self._command_count = len(self._commands)

        self._command_hashmap = {}
        for command in self._commands:
            file_name_only = os.path.splitext(command['file'])[0]
            self._command_hashmap[file_name_only] = command

    def _set_using_command_hashmap(self, command_hashmap: dict):
        self._command_hashmap = command_hashmap
        self._commands = []
        for command in self._command_hashmap:
            self._commands.append(self._command_hashmap[command])
        self._command_count = len(self._commands)

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
        """Write to file."""
        if len(content) > 0:
            with open(file_path, 'w', encoding="utf-8") as output_file:
                print(content, file=output_file)

    def get_command_hashmap(self):
        """Get command hashmap."""
        return self._command_hashmap

    def job(self,
            config: cfg.Config,
            output_directory: str,
            error_directory: str):
        """Command executor job."""
        index = self.next_index()
        while index >= 0:
            command = self[index]

            entry, result, error = \
                CommandManager.execute_clang_tidy(command, config)

            input_path = entry.get_input_path()
            file_name = os.path.basename(input_path)
            file_id = hashlib.md5(file_name.encode('utf-8')).hexdigest()

            output_file_path = f'{output_directory}/{file_name}.{file_id}'
            error_file_path = f'{error_directory}/{file_name}.{file_id}'

            self._write_to_file(result, output_file_path)
            self._write_to_file(error, error_file_path)

            index = self.next_index()

    def export_to_pkl(self, file_path: str) -> int:
        """Export to PKL file."""
        try:
            with open(file_path, 'wb') as output_file:
                pickle.dump(self._command_hashmap, output_file,
                            protocol=pickle.HIGHEST_PROTOCOL)
        except OSError:
            con.error(f'Error writing data to {file_path}.')
            return -1

        con.trace(f'Commands has been written to {file_path}')
        return 0

    @classmethod
    def execute_clang_tidy(cls, command, config: cfg.Config) -> tuple:
        """Execute clang-tidy."""
        entry = cdb.Entry(command)

        # Compose command line for clang-tidy.
        exec_cmd = []

        exec_cmd.append(config.get_clang_tidy_executable())
        exec_cmd.append('--quiet')

        for additional_option in config.get_clang_tidy_additional_options():
            exec_cmd.append(additional_option)

        input_path = entry.get_input_path()
        path_converters = config.get_path_converters()
        conv_input_path = cdb.Entry.convert_path(input_path, path_converters)
        exec_cmd.append(f'{conv_input_path}')

        exec_cmd.append('--')

        arguments = entry.get_arguments()
        for arg in arguments:
            conv_str = cdb.Entry.convert_path(arg, path_converters)
            exec_cmd.append(conv_str)

        proc = sproc.run(exec_cmd,
                         encoding='utf-8',
                         shell=False,
                         stdout=sproc.PIPE,
                         stderr=sproc.PIPE,
                         universal_newlines=True,
                         text=True,
                         check=True)

        return entry, proc.stdout, proc.stderr
