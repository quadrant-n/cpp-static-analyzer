import json

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

class Entry:
    directory = ''
    arguments = []
    input_path = ''
    output_path = ''

    def __init__(self, dictionary):
        if 'directory' in dictionary:
            self.directory = dictionary['directory']
        else:
            self.directory = ''

        if 'arguments' in dictionary:
            self.arguments = get_arguments(dictionary)
        elif 'command' in dictionary:
            self.arguments = get_command(dictionary)

        if 'file' in dictionary:
            self.input_path = dictionary['file']
        else:
            self.input_path = ''

        if 'output' in dictionary:
            self.output_path = dictionary['output']
        else:
            self.output_path = ''
