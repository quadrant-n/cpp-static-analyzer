"""Static analyzer command manager."""

import subprocess as sproc
import threading
import os.path
import hashlib
import pickle
import sys

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
        con.trace(f'Using commands {file_path}.')
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
            con.trace(f'Using commands {file_path}.')
            with open(file_path, 'rb') as pkl_file_handle:
                command_hashmap = pickle.load(pkl_file_handle)
                command_manager._set_using_command_hashmap(command_hashmap)
                if len(command_manager) == 0:
                    con.error('No compile command found.')
        except OSError:
            con.error(f'Error reading data from {file_path}.')

        return command_manager

    def _set_using_commands(self, commands: list):
        """Set using commands."""
        self._commands = commands
        self._command_count = len(self._commands)

        self._command_hashmap = {}
        for command in self._commands:
            file_name_only = os.path.splitext(command['file'])[0]
            self._command_hashmap[file_name_only] = command

    def _set_using_command_hashmap(self, command_hashmap: dict):
        """Set using command hashmap."""
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
        if len(content) == 0:
            con.trace(f'No content available for writing to {file_path}')
            return

        try:
            with open(file_path, 'w', encoding="utf-8") as output_file:
                print(content, file=output_file)
        except OSError:
            con.error(f'Cannot write to {file_path}.')

    def get_command_hashmap(self):
        """Get command hashmap."""
        return self._command_hashmap

    def _get_file_name_and_id(self, entry: cdb.Entry):
        """Calculate file ID."""
        input_path = entry.get_input_path()
        file_name = os.path.basename(input_path)
        return file_name, hashlib.md5(file_name.encode('utf-8')).hexdigest()

    def _run_clang_tidy(self, entry: cdb.Entry, config: cfg.Config,
                        output_directory: str, error_directory: str):
        """Run clang-tidy."""
        completed = \
            CommandManager.execute_clang_tidy(entry, config)

        file_name, file_id = self._get_file_name_and_id(entry)

        if completed.returncode != 0:
            con.trace(f'clang-tidy returns {completed.returncode} '
                      f'when analyzing {file_name}')

        result = completed.stdout
        error = completed.stderr

        if len(result) == 0 and len(error) == 0:
            con.trace(f'No result available for {file_name}')
            return

        output_file_path = f'{output_directory}/{file_name}.{file_id}'
        error_file_path = f'{error_directory}/{file_name}.{file_id}'

        self._write_to_file(result, output_file_path)
        self._write_to_file(error, error_file_path)

    def _run_clang_static_analyzer(self, entry: cdb.Entry, config: cfg.Config,
                                   output_directory: str):
        """Run clang static analyzer."""
        completed = \
            CommandManager.execute_clang_static_analyzer(entry, config)

        result = completed.stdout
        error = completed.stderr

        file_name, file_id = self._get_file_name_and_id(entry)

        if len(result) == 0 and len(error) == 0:
            con.trace(f'No result available for {file_name}')
            return

        output_file_path = f'{output_directory}/{file_name}.clang_sa.{file_id}'

        if completed.returncode != 0:
            con.trace(f'clang-tidy returns {completed.returncode} '
                      f'when analyzing {file_name}')
        try:
            with open(output_file_path, 'w', encoding="utf-8") as output_file:
                if len(result) > 0:
                    print(result, file=output_file)
                if len(error) > 0:
                    print(error, file=output_file)
        except OSError:
            con.error(f'Cannot write to {output_file_path}.')

    def job(self, config: cfg.Config, output_directory: str,
            error_directory: str):
        """Command executor job."""
        index = self.next_index()
        while index >= 0:
            command = self[index]
            entry = cdb.Entry(command)

            if config.is_clang_tidy_enabled():
                self._run_clang_tidy(entry, config,
                                     output_directory, error_directory)

            if config.is_clang_enabled():
                self._run_clang_static_analyzer(entry, config, output_directory)

            index = self.next_index()

    def _write_to_stdout(self, content):
        """Write to stdout."""
        if len(content) > 0:
            sys.stdout.write(content)

    def _write_to_stderr(self, content):
        """Write to stderr."""
        if len(content) > 0:
            sys.stderr.write(content)

    def _analyze_with_clang_tidy(self, config: cfg.Config, entry: cdb.Entry):
        """Run clang-tidy."""
        completed = \
            CommandManager.execute_clang_tidy(entry, config)

        if completed.returncode != 0:
            con.error(f'clang-tidy returns {completed.returncode} '
                      f'when analyzing {entry.get_input_path()}')

        self._write_to_stdout(completed.stdout)
        self._write_to_stderr(completed.stderr)

    def _analyze_with_clang(self, config: cfg.Config, entry: cdb.Entry):
        """Run clang static analyzer."""
        completed = \
            CommandManager.execute_clang_static_analyzer(entry, config)

        if completed.returncode != 0:
            con.error(f'clang returns {completed.returncode} '
                      f'when analyzing {entry.get_input_path()}')

        # Clang static analyzer reports diagnostic results as errors.
        self._write_to_stdout(completed.stdout)
        self._write_to_stdout(completed.stderr)

    def analyze(self, config: cfg.Config, file_path: str):
        """Analyze single path."""
        file_name_without_ext = os.path.splitext(file_path)

        if file_name_without_ext[0] in self._command_hashmap:
            command = self._command_hashmap[file_name_without_ext[0]]
            entry = cdb.Entry(command)

            if config.is_clang_tidy_enabled():
                self._analyze_with_clang_tidy(config, entry)

            if config.is_clang_enabled():
                self._analyze_with_clang(config, entry)

            return 0

        con.error(f'No entry found for {file_path}.')
        return -1

    def _create_directory(self, file_path: str) -> int:
        """Create directory."""
        try:
            directory_name = os.path.dirname(file_path)
            os.makedirs(directory_name, exist_ok=True)
            return 0
        except OSError:
            return -1

    def export_to_pkl(self, file_path: str) -> int:
        """Export to PKL file."""
        if self._create_directory(file_path) != 0:
            con.error(f'Cannot create directories for {file_path}.')
            return -2

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
    def execute_clang_tidy(cls, entry: cdb.Entry,
                           config: cfg.Config) -> sproc.CompletedProcess:
        """Execute clang-tidy."""
        # Compose command line for clang-tidy.
        exec_cmd = []

        exec_cmd.append(config.get_clang_tidy_executable())
        exec_cmd.append('--quiet')
        exec_cmd.append(f'--config-file={config.get_clang_tidy_config_file()}')

        for additional_option in config.get_clang_tidy_additional_options():
            exec_cmd.append(additional_option)

        input_path = entry.get_input_path()
        exec_cmd.append(input_path)

        arguments = entry.get_arguments()
        if len(arguments) > 0:
            exec_cmd.append('--')
            for arg in arguments:
                exec_cmd.append(arg)

        proc = sproc.run(exec_cmd,
                         encoding='utf-8',
                         shell=False,
                         stdout=sproc.PIPE,
                         stderr=sproc.PIPE,
                         universal_newlines=True,
                         text=True,
                         check=False)

        return proc

    @classmethod
    def execute_clang_static_analyzer(
            cls,
            entry: cdb.Entry,
            config: cfg.Config) -> sproc.CompletedProcess:
        """Execute clang static analyzer."""
        # Compose command line for clang-tidy.
        exec_cmd = []

        exec_cmd.append(config.get_clang_executable())
        exec_cmd.append('--analyze')

        diag_dir = config.get_clang_diagnostic_directory()
        if diag_dir != '':
            file_name = os.path.basename(entry.get_input_path())
            exec_cmd.append('-o')
            exec_cmd.append(f'{diag_dir}/{file_name}')

        for additional_option in config.get_clang_additional_options():
            exec_cmd.append(additional_option)

        arguments = entry.get_arguments()
        skip_next = True
        for arg in arguments:
            if skip_next:
                skip_next = False
                continue

            if arg == '-o':
                skip_next = True
            else:
                exec_cmd.append(arg)

        proc = sproc.run(exec_cmd,
                         encoding='utf-8',
                         shell=False,
                         stdout=sproc.PIPE,
                         stderr=sproc.PIPE,
                         universal_newlines=True,
                         text=True,
                         check=False)

        return proc
