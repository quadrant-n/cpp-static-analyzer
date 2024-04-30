# compiledb_test.py

import pytest
import json
import compile_db as cdb

@pytest.fixture
def compile_commands_json():
    cdb_json = '''
    [
        {
            "directory": "/Users/nus/test",
            "command": "/usr/bin/c++ -I/Users/nus/test/include/. -I\\"/Users/nus/test/include path/.\\" -O3 -DNDEBUG -o /Users/nus/build/test.cpp.o -c /Users/nus/test.cpp",
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
    command_list = cdb.get_command(compile_commands_json[0])
    assert len(command_list) == 9, 'Must find 9 commands.'

def test_argument_parser(compile_commands_json):
    argument_list = cdb.get_arguments(compile_commands_json[1])
    assert len(argument_list) == 9, 'Must find 9 arguments.'

def test_entry_conversion(compile_commands_json):
    cmd_entry = cdb.Entry(compile_commands_json[0])
    args_entry = cdb.Entry(compile_commands_json[1])
    assert cmd_entry.directory == args_entry.directory, \
        'Wrong directory value.'

    assert len(cmd_entry.arguments) == len(args_entry.arguments), \
        'Wrong argument number.'
    for ii in range(len(cmd_entry.arguments)):
        assert cmd_entry.arguments[ii] == args_entry.arguments[ii], \
            'Argument-{ii}: {cmd_entry.arguments[ii]} != \
            {args_entry.arguments[ii]}'

    assert cmd_entry.input_path == args_entry.input_path, 'Wrong input file.'
    assert cmd_entry.output_path == args_entry.output_path, 'Wrong output file.'
