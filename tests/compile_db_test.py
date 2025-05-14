"""Test cases for compile database operations."""

import json
import pytest
import cpp_static_analyzer.compile_db as cdb


@pytest.fixture(name='compile_commands_json')
def fixture_compile_commands_json():
    """Simple compile command."""
    cdb_json = '''
    [
        {
            "directory": "/Users/nus/test",
            "command": "/usr/bin/c++ -I/Users/nus/test/include/. \
    -I\\"/Users/nus/test/include path/.\\" -O3 -DNDEBUG \
    -o /Users/nus/build/test.cpp.o -c /Users/nus/test.cpp",
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
    """Testing command parser."""
    command_list = \
        cdb.Entry.get_command_from_dictionary(compile_commands_json[0])
    assert len(command_list) == 9, 'Must find 9 commands.'


def test_argument_parser(compile_commands_json):
    """Testing argument parser."""
    argument_list = \
        cdb.Entry.get_arguments_from_dictionary(compile_commands_json[1])
    assert len(argument_list) == 9, 'Must find 9 arguments.'


def test_entry_conversion(compile_commands_json):
    """Convert compile command to entry object."""
    cmd_entry = cdb.Entry(compile_commands_json[0])
    args_entry = cdb.Entry(compile_commands_json[1])
    assert cmd_entry.get_directory() == args_entry.get_directory(), \
        'Wrong directory value.'

    cmd_arguments = cmd_entry.get_arguments()
    entry_arguments = args_entry.get_arguments()
    assert len(cmd_arguments) == len(entry_arguments), \
        'Wrong argument number.'
    for (cmd_argument, argument) in zip(cmd_arguments, entry_arguments):
        assert cmd_argument == argument, \
            f'Argument: {cmd_argument} != {argument}'

    assert cmd_entry.get_input_path() == args_entry.get_input_path(), \
        'Wrong input file.'
    assert cmd_entry.get_output_path() == args_entry.get_output_path(), \
        'Wrong output file.'
