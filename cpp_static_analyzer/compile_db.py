import json
import pathlib as plib

def get_next_quote(it, cc, cmd):
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
    result = cc
    try:
        cc = cmd[next(it)]
        while cc != ' ' and cc != 0:
            if cc == '"':
                sub_str, cc = get_next_quote(it, cc, cmd)
                result += sub_str
            else:
                result += cc
                cc = cmd[next(it)]
    except StopIteration:
        cc = 0
    return result, cc

def get_command(dictionary: dict):
    command_list = []
    if 'command' not in dictionary:
        return command_list

    string = dictionary['command']
    str_len = len(string)
    range_iter = iter(range(str_len))
    command = ""

    for ii in range_iter:
        curr_cc = string[ii]

        if curr_cc == '"':
            # Search for next quote.
            curr_cmd, curr_cc = get_next_quote(range_iter, curr_cc, string)
        else:
            # Search for next space.
            curr_cmd, curr_cc = get_next_space(range_iter, curr_cc, string)
        command += curr_cmd

        if curr_cc == ' ' or curr_cc == 0:
            command_list.append(command)
            command = ""

    return command_list

def get_arguments(dictionary: dict):
    if 'arguments' not in dictionary:
        return []

    return dictionary['arguments']

def load_compile_commands(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def convert_path(path: str, converter: dict):
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
    filtered_commands = []

    for command in commands:
        if command.startswith('-w') or command.startswith('-W'):
            continue
        filtered_commands.append(command)

    return filtered_commands

class Entry(object):
    directory = ''
    arguments = []
    input_path = ''
    output_path = ''

    def __init__(self, dictionary):
        if 'directory' in dictionary:
            self.directory = plib.Path(dictionary['directory']).as_posix()
        else:
            self.directory = ''

        if 'arguments' in dictionary:
            self.arguments = get_arguments(dictionary)
        elif 'command' in dictionary:
            self.arguments = get_command(dictionary)

        self.arguments = filter_warnings(self.arguments)

        if 'file' in dictionary:
            self.input_path = plib.Path(dictionary['file']).as_posix()
        else:
            self.input_path = ''

        if 'output' in dictionary:
            self.output_path = plib.Path(dictionary['output']).as_posix()
        else:
            self.output_path = ''
