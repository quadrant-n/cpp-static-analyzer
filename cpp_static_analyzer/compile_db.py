"""Compile commands loader & data-base handler."""
import json
import pathlib as plib


def get_next_quote(it, cc, cmd):
    """Search for next double quotation."""
    result = cc
    try:
        cc = cmd[next(it)]
        while cc != '"':
            result += cc
            cc = cmd[next(it)]
        result += cc
        cc = cmd[next(it)]
    except StopIteration:
        cc = 0
    return result, cc


def get_next_space(it, cc, cmd):
    """Search for next space."""
    result = cc
    try:
        cc = cmd[next(it)]
        while not cc in (' ', 0):
            if cc == '"':
                sub_str, cc = get_next_quote(it, cc, cmd)
                result += sub_str
            else:
                result += cc
                cc = cmd[next(it)]
    except StopIteration:
        cc = 0
    return result, cc


def skip_whitespace(it, cc, cmd):
    """Skip whitespaces (space, line, tab)"""
    try:
        while cc in ('\n', '\t', ' '):
            cc = cmd[next(it)]
    except StopIteration:
        cc = 0
    return cc


def get_command(dictionary: dict):
    """Get command from compile_commands.json."""
    command_list = []
    if 'command' not in dictionary:
        return command_list

    string = dictionary['command']
    str_len = len(string)
    range_iter = iter(range(str_len))
    command = ''

    for ii in range_iter:
        curr_cc = string[ii]

        curr_cc = skip_whitespace(range_iter, curr_cc, string)

        if curr_cc == '"':
            # Search for next quote.
            curr_cmd, curr_cc = get_next_quote(range_iter, curr_cc, string)
        else:
            # Search for next space.
            curr_cmd, curr_cc = get_next_space(range_iter, curr_cc, string)
        command += curr_cmd

        if curr_cc in (' ', 0):
            command_list.append(command)
            command = ""

    return command_list


def get_arguments(dictionary: dict):
    """Get command arguments."""
    if 'arguments' not in dictionary:
        return []

    return dictionary['arguments']


def load_compile_commands(filename):
    """Load compile_commands.json."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def convert_path(path: str, converter: dict):
    """Convert path."""
    result = path
    for key, value in converter.items():
        index = path.find(key)
        if index >= 0:
            if index > 0:
                sub_str0 = path[0:index]
            else:
                sub_str0 = ''
            sub_str1 = path[len(key) + index:]
            result = sub_str0 + value + sub_str1
            break
    return result


def filter_warnings(commands):
    """Filter warnings."""
    filtered_commands = []

    for command in commands:
        if command.startswith('-w') or command.startswith('-W'):
            continue
        filtered_commands.append(command)

    return filtered_commands


class Entry:
    """A command entry."""

    _directory = ''
    _arguments = []
    _input_path = ''
    _output_path = ''

    def __init__(self, dictionary):
        if 'directory' in dictionary:
            self._directory = plib.Path(dictionary['directory']).as_posix()
        else:
            self._directory = ''

        if 'arguments' in dictionary:
            self._arguments = get_arguments(dictionary)
        elif 'command' in dictionary:
            self._arguments = get_command(dictionary)

        self._arguments = filter_warnings(self._arguments)

        if 'file' in dictionary:
            self._input_path = plib.Path(dictionary['file']).as_posix()
        else:
            self._input_path = ''

        if 'output' in dictionary:
            self._output_path = plib.Path(dictionary['output']).as_posix()
        else:
            self._output_path = ''

    def get_directory(self):
        """Get working diretory."""
        return self._directory

    def get_arguments(self):
        """Get command arguments."""
        return self._arguments

    def get_input_path(self):
        """Get input path."""
        return self._input_path

    def get_output_path(self):
        """Get output path."""
        return self._output_path
