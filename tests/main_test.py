"""Test cases for main function."""

import os
import pathlib
import pytest


from cpp_static_analyzer.main import create_argument_parser, run
import cpp_static_analyzer.error_codes as ec


@pytest.fixture(name='parser')
def fixture_parser():
    """Fixture for creating parser."""
    return create_argument_parser()


def test_display_help(parser):
    """Test display_help function."""
    try:
        parser.parse_args(['--help'])
    except SystemExit as e:
        assert e.code == 0, 'Expected error code 0 when displaying help.'


def setup_module(_):
    """Setup module."""
    cwd = os.getcwd()
    os.chdir(cwd + '/tests')


def test_analyze_all_files(parser):
    """Analyze single file."""
    arguments = parser.parse_args(['--output_directory',
                                   'out',
                                   '--compile_commands',
                                   'sources/compile_commands.json'])
    error_code = run(arguments)
    assert error_code == ec.ErrorCodes.SUCCESS.value, \
        'Must execute analyzer without any error.'


def test_analyze_single_file(parser):
    """Analyze single file."""
    file_path = 'sources/binary_tree.h'
    arguments = parser.parse_args(['-pkl',
                                   'sources/compile_commands.pkl',
                                   '-f',
                                   file_path])
    error_code = run(arguments)
    assert error_code == ec.ErrorCodes.SUCCESS.value, \
        'Must analyze binary_tree.h without any error.'


def test_analyze_single_file_using_full_path(parser):
    """Analyze single file."""
    file_path = pathlib.Path('sources/binary_tree.h').resolve().as_posix()
    arguments = parser.parse_args(['-pkl',
                                   'sources/compile_commands.pkl',
                                   '-f',
                                   file_path])
    error_code = run(arguments)
    assert error_code == ec.ErrorCodes.SUCCESS.value, \
        'Must analyze binary_tree.h without any error.'
