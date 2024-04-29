# compiledb_test.py

import pytest
import json
import compiledb as cdb

@pytest.fixture
def compile_commands_json():
    cdb_json = '''
    [
        {
            "directory": "/Users/nus/test",
            "command": "/usr/bin/c++ -I/Users/nus/test/include/. -I\\"/Users/nus/test/include/.\\" -O3 -DNDEBUG -o /Users/nus/build/test.cpp.o -c /Users/nus/test.cpp",
            "file": "/Users/nus/test.cpp",
            "output": "/Users/nus/build/test.cpp.o"
        },
        {
            "directory": "/Users/nus/test",
            "arguments": [
                "/usr/bin/c++",
                "-I/Users/nus/test/include/.",
                "-I\\"/Users/nus/test/include path/.\\"",
                "-O3",
                "-DNDEBUG",
                "-o",
                "/Users/nus/build/test.cpp.o",
                "-c",
                "/Users/nus/test.cpp"
            ],
            "file": "/Users/nus/test.cpp",
            "output": "/Users/nus/build/test.cpp.o"
        }
    ]
    '''
    return json.loads(cdb_json)

def test_command_parser(compile_commands_json):
    command_list = cdb.getCommand(compile_commands_json[0])
    assert len(command_list) == 9, 'Must find 9 commands.'

def test_argument_parser(compile_commands_json):
    argument_list = cdb.getArguments(compile_commands_json[1])
    assert len(argument_list) == 9, 'Must find 9 arguments.'
