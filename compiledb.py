import json

def loadCompileCommands(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data
