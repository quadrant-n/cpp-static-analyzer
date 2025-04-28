"""Compile commands loader & data-base handler."""

import json
import pathlib as plib


class Entry:
    """A command entry."""

    def __init__(self, dictionary: dict):
        if 'directory' in dictionary:
            self._directory = plib.Path(dictionary['directory']).as_posix()
        else:
            self._directory = ''

        if 'arguments' in dictionary:
            self._arguments = Entry.get_arguments_from_dictionary(dictionary)
        elif 'command' in dictionary:
            self._arguments = Entry.get_command_from_dictionary(dictionary)

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

    @classmethod
    def get_quoted_string(cls, input_string: str):
        """Get quoted string."""
        result = input_string.split('\"')
        if len(result) > 1:
            remain_str = input_string.lstrip('\"')
            remain_str = remain_str.lstrip(result[1])
            remain_str = remain_str.lstrip('\"')
            result_str = f'"{result[1]}"'
            return result_str, remain_str
        return '', ''

    @classmethod
    def get_word(cls, input_string: str):
        """Get word."""
        sub_strings = input_string.split()
        if len(sub_strings) >= 1:
            quote_index = sub_strings[0].find('\"')
            if quote_index >= 0:
                commands = sub_strings[0].partition('\"')
                remain_str = input_string.lstrip(commands[0])
                result_str, remain_str = cls.get_quoted_string(remain_str)
                result = f'{commands[0]}{result_str}'
            else:
                result = sub_strings[0]
                remain_str = input_string.lstrip(sub_strings[0])
            return result, remain_str
        return '', ''

    @classmethod
    def strip_whitespaces(cls, input_string: str):
        """Skip whitespaces (space, line, tab)"""
        return input_string.strip()

    @classmethod
    def get_command_from_dictionary(cls, dictionary: dict):
        """Get command from compile_commands.json."""
        command_list: list[str] = []
        if 'command' not in dictionary:
            return command_list

        current_string = dictionary['command']
        current_string = cls.strip_whitespaces(current_string)

        while len(current_string) > 0:
            if current_string[0] == '\"':
                result, current_string = cls.get_quoted_string(current_string)
            else:
                result, current_string = cls.get_word(current_string)

            command_list.append(result)
            current_string = cls.strip_whitespaces(current_string)

        return command_list

    @classmethod
    def get_arguments_from_dictionary(cls, dictionary: dict):
        """Get command arguments."""
        if 'arguments' not in dictionary:
            return []

        return dictionary['arguments']

    @classmethod
    def load_compile_commands(cls, filename):
        """Load compile_commands.json."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    @classmethod
    def convert_path(cls, path: str, converter: dict):
        """Convert path."""
        result = path
        for key, value in converter.items():
            index = path.find(key)
            if index >= 0:
                if index > 0:
                    sub_str_0 = path[0:index]
                else:
                    sub_str_0 = ''
                sub_str_1 = path[len(key) + index:]
                result = sub_str_0 + value + sub_str_1
                break

        return result
