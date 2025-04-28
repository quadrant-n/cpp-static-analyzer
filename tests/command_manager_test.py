"""Test cases for command manager,"""

import pytest
import os.path
import cpp_static_analyzer.command_manager as cm


@pytest.fixture(name='compile_commands_json')
def fixture_compile_commands_json():
    """Fixture for compile_commands.json."""
    return 'tests/compile_commands.json'


@pytest.fixture(name='file_names')
def fixture_file_names():
    """Fixture of file names in compile_commands.json."""
    return ['/home/llama.cpp/ggml.c',
            '/home/llama.cpp/ggml-alloc.c',
            '/home/llama.cpp/ggml-backend.c']


def test_command_manager(compile_commands_json):
    """Testing command manager."""
    cmd_mgr = cm.CommandManager(compile_commands_json)
    assert len(cmd_mgr) == 3, 'Must have four commands.'

    ii = cmd_mgr.next_index()
    assert ii == 0, 'Must be 0.'

    ii = cmd_mgr.next_index()
    assert ii == 1, 'Must be 1.'

    ii = cmd_mgr.next_index()
    assert ii == 2, 'Must be 2.'

    ii = cmd_mgr.next_index()
    assert ii == -1, 'Must be -1.'


def test_command_hashmap(compile_commands_json, file_names):
    """Testing command hashmap."""
    cmd_mgr = cm.CommandManager(compile_commands_json)
    command_hashmap = cmd_mgr.get_command_hashmap()
    assert len(command_hashmap) == len(file_names), 'Must have four commands.'

    for file_name in file_names:
        file_name_only = os.path.splitext(file_name)[0]
        assert file_name_only in command_hashmap, f'Must include {file_name}.'

        command = command_hashmap[file_name_only]
        assert 'directory' in command, 'Must have directory.'
        assert 'file' in command, 'Must have file.'
        assert 'output' in command, 'Must have output.'
        assert 'command' in command, 'Must have command.'
