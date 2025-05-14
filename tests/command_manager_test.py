"""Test cases for command manager."""

import os.path
import pathlib
import pytest


import cpp_static_analyzer.command_manager as cm
import cpp_static_analyzer.error_codes as ec


@pytest.fixture(name='compile_commands_json')
def fixture_compile_commands_json():
    """Fixture for compile_commands.json."""
    return 'tests/sources/compile_commands.json'


@pytest.fixture(name='file_names')
def fixture_file_names():
    """Fixture of file names in compile_commands.json."""
    return ['sources/main.cpp',
            'sources/link_list.cpp',
            'sources/binary_tree.cpp']


@pytest.fixture(name='full_paths')
def fixture_full_paths():
    """Fixture of full paths in compile_commands.json."""
    return [pathlib.Path('sources/main.cpp').resolve().as_posix(),
            pathlib.Path('sources/link_list.cpp').resolve().as_posix(),
            pathlib.Path('sources/binary_tree.cpp').resolve().as_posix()]


@pytest.fixture(name='pkl_file_name')
def fixture_pkl_file_name():
    """Fixture for pkl file name."""
    return 'tests/out/compile_commands.pkl'


@pytest.fixture(name='compile_commands_pkl')
def fixture_compile_commands_pkl():
    """Fixture for compile_commands.pkl."""
    return 'tests/sources/compile_commands.pkl'


def test_command_manager(compile_commands_json):
    """Testing command manager."""
    cmd_mgr = cm.CommandManager.create_from_json(compile_commands_json)
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
    cmd_mgr = cm.CommandManager.create_from_json(compile_commands_json)
    assert cmd_mgr.get_command_hashmap_length() == len(file_names), \
        f'Must have {len(file_names)} commands.'

    for file_name in file_names:
        file_name_only = os.path.splitext(file_name)[0]
        command = cmd_mgr.get_command(file_name_only)

        assert command is not None, f'Must include {file_name}.'

        assert 'directory' in command, 'Must have directory.'
        assert 'file' in command, 'Must have file.'
        assert 'command' in command, 'Must have command.'
        assert 'output' in command, 'Must have output.'


def test_command_hashmap_using_full_paths(compile_commands_json, full_paths):
    """Testing command hashmap using full paths."""
    cmd_mgr = cm.CommandManager.create_from_json(compile_commands_json)
    assert cmd_mgr.get_command_hashmap_length() == len(full_paths), \
        f'Must have {len(full_paths)} commands.'

    for full_path in full_paths:
        file_name_only = os.path.splitext(full_path)[0]
        command = cmd_mgr.get_command(file_name_only)

        assert command is not None, f'Must include {full_path}.'

        assert 'directory' in command, 'Must have directory.'
        assert 'file' in command, 'Must have file.'
        assert 'command' in command, 'Must have command.'
        assert 'output' in command, 'Must have output.'


def test_export_to_pickle(compile_commands_json, pkl_file_name):
    """Export data to pickle."""
    cmd_mgr = cm.CommandManager.create_from_json(compile_commands_json)
    error_code = cmd_mgr.export_to_pkl(pkl_file_name)
    assert error_code == ec.ErrorCodes.SUCCESS.value, \
        f'Error exporting to {pkl_file_name}'


def test_import_from_pickle(compile_commands_pkl, file_names):
    """Import from pickle."""
    cmd_mgr = cm.CommandManager.create_from_pkl(compile_commands_pkl)
    commands = cmd_mgr.get_commands()

    for command in commands:
        file_name = ''
        if 'file' in command:
            file_name = command['file']
        assert file_name in file_names, f'Invalid file {file_name}.'
