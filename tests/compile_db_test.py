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


@pytest.fixture(name='path_converter')
def fixture_path_converter():
    """Converting paths."""
    return {
        '/Users/nus/test': '/home/test',
        '/Users/nus/build': '/home/build'
    }


@pytest.fixture(name='empty_path_converter')
def fixture_empty_path_converter():
    """Empty path coverter, no path will be converted."""
    return {}


@pytest.fixture(name='compile_command')
def fixture_compile_command():
    """Simple compile command."""
    return ['c++',
            '-I/Users/nus/include',
            '-O3',
            '-DNDEBUG',
            '-w',
            '-Wall',
            '-Wextra',
            '-o',
            '/Users/nus/x.out',
            'x.cpp']


def test_command_parser(compile_commands_json):
    """Testing command parser."""
    command_list = cdb.get_command(compile_commands_json[0])
    assert len(command_list) == 9, 'Must find 9 commands.'


def test_argument_parser(compile_commands_json):
    """Testing argument parser."""
    argument_list = cdb.get_arguments(compile_commands_json[1])
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

    assert cmd_entry.get_input_path() == args_entry.get_input_path(), 'Wrong input file.'
    assert cmd_entry.get_output_path() == args_entry.get_output_path(), 'Wrong output file.'


def test_path_converter(compile_commands_json, path_converter):
    """Testing path converter."""
    args = compile_commands_json[1]
    arg_strs = args['arguments']
    results = []

    for arg_str in arg_strs:
        result = cdb.convert_path(arg_str, path_converter)
        results.append(result)

    path_conversion_results = [
        '/usr/bin/c++',
        '-I/home/test/include/.',
        '-I\"/home/test/include path/.\"',
        '-O3',
        '-DNDEBUG',
        '-o',
        '/home/build/test.cpp.o',
        '-c',
        '/home/test.cpp'
    ]

    assert len(results) == len(path_conversion_results), 'Wrong result count.'

    for (result, conv_result) in zip(results, path_conversion_results):
        assert result == conv_result, \
            f'Argument {conv_result} must be {result}'


def test_empty_path_converter(compile_commands_json, empty_path_converter):
    """Testing empty path converter."""
    args = compile_commands_json[1]
    arg_strs = args['arguments']
    results = []

    for arg_str in arg_strs:
        result = cdb.convert_path(arg_str, empty_path_converter)
        results.append(result)

    path_conversion_results = [
        '/usr/bin/c++',
        '-I/Users/nus/test/include/.',
        '-I\"/Users/nus/test/include path/.\"',
        '-O3',
        '-DNDEBUG',
        '-o',
        '/Users/nus/build/test.cpp.o',
        '-c',
        '/Users/nus/test.cpp'
    ]

    assert len(results) == len(path_conversion_results), 'Wrong result count.'

    for (result, conv_result) in zip(results, path_conversion_results):
        assert result == conv_result, \
            f'Argument {result} must be unchanged. Result: {conv_result}.'


def test_filter_command(compile_command):
    """Filter unnecessary commands."""
    filtered_commands = cdb.filter_warnings(compile_command)
    for filtered_command in filtered_commands:
        assert filtered_command.startswith('-w') is False, \
            f'Argument {filtered_command} must be filtered.'
        assert filtered_command.startswith('-W') is False, \
            f'Argument {filtered_command} must be filtered.'
