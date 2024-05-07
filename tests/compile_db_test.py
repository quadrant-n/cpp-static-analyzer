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

@pytest.fixture
def path_converter():
    return {
        '/Users/nus/test': '/home/test',
        '/Users/nus/build': '/home/build'
    }

@pytest.fixture
def empty_path_converter():
    return {}

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
            f'Argument-{ii}: {cmd_entry.arguments[ii]} != \
            {args_entry.arguments[ii]}'

    assert cmd_entry.input_path == args_entry.input_path, 'Wrong input file.'
    assert cmd_entry.output_path == args_entry.output_path, 'Wrong output file.'

def test_path_converter(compile_commands_json, path_converter):
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

    for ii in range(len(results)):
        assert results[ii] == path_conversion_results[ii], \
            f'Argument-{ii} must be {path_conversion_results[ii]}'

def test_empty_path_converter(compile_commands_json, empty_path_converter):
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

    for ii in range(len(results)):
        assert results[ii] == path_conversion_results[ii], \
            f'Argument-{ii} must be unchanged.'
