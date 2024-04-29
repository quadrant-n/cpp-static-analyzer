import json

def getNextQuote(it, cc, cmd):
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

def getNextSpace(it, cc, cmd):
    result = cc
    try:
        cc = cmd[next(it)]
        while cc != ' ' and cc != 0:
            if cc == '"':
                sub_str, cc = getNextQuote(it, cc, cmd)
                result += sub_str
            else:
                result += cc
                cc = cmd[next(it)]
    except StopIteration:
        cc = 0
    return result, cc

def getCommand(dictionary: dict):
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
            curr_cmd, curr_cc = getNextQuote(range_iter, curr_cc, string)
        else:
            # Search for next space.
            curr_cmd, curr_cc = getNextSpace(range_iter, curr_cc, string)
        command += curr_cmd

        if curr_cc == ' ' or curr_cc == 0:
            command_list.append(command)
            command = ""

    return command_list

def getArguments(dictionary: dict):
    if 'arguments' not in dictionary:
        return []

    return dictionary['arguments']

def loadCompileCommands(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data
