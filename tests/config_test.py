"""Test cases for config file."""

import os
import pytest
import yaml
import cpp_static_analyzer.config as cfg


@pytest.fixture(name='yaml_config')
def fixture_yaml_config():
    """Simple yaml config."""
    yaml_string = '''
    compile_commands: tests/compile_commands.json
    clang-tidy:
      executable_path: ~/.local/bin/clang-tidy
    path_converters:
      /Users/nus/test: /test
      /Users/nus/build: /build
    '''
    return yaml.safe_load(yaml_string)


@pytest.fixture(name='yaml_empty_config')
def fixture_yaml_empty_config():
    """An empty config."""
    yaml_string = '''
    compile_commands: ''
    clang: {}
    clang-tidy: {}
    path_converters: {}
    '''
    return yaml.safe_load(yaml_string)


@pytest.fixture(name='file_in_nested_directory')
def fixture_file_in_nested_directory():
    """File in nested directory."""
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/deep/nested/directory/for/testing.txt')


@pytest.fixture(name='nested_directory')
def fixture_nested_directory():
    """Nested directory."""
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/deep/nested/directory/for/')


@pytest.fixture(name='directory_not_exist')
def fixture_directory_not_exist():
    """Unexisting directory."""
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/not_exist')


@pytest.fixture(name='config_exist')
def fixture_config_exist():
    """Config file exists."""
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/deep/.cpp-static-analyzer')


def config_yml_file_path():
    """Helper functions to fetch config file."""
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/deep/.cpp-static-analyzer')


def test_search_for_config(nested_directory):
    """Finding config.yml on dested directory."""
    config_path = \
        cfg.Config.search_for_config_file(nested_directory)
    config_yml_path = config_yml_file_path()
    assert config_path == config_yml_path, 'Must find config.yml.'


def test_search_for_config_using_file(file_in_nested_directory):
    """Find config.yml when using file."""
    config_path = \
        cfg.Config.search_for_config_file(file_in_nested_directory)
    config_yml_path = config_yml_file_path()
    assert config_path == config_yml_path, 'Must find config.yml.'


def test_search_for_config_not_exist(directory_not_exist):
    """Search for non-existed directory."""
    config_path = \
        cfg.Config.search_for_config_file(directory_not_exist)
    assert config_path == '', 'Must be an empty string.'


def test_search_for_config_exist(config_exist):
    """Search for existing config file."""
    config_path = \
        cfg.Config.search_for_config_file(config_exist)
    assert config_path != '', 'Must found .cpp-static-analyzer.'


def test_empty_config(yaml_empty_config):
    """Testing empty config file."""
    config = cfg.Config(yaml_empty_config)
    assert config.get_compile_commands() == 'compile_commands.json', \
        'Must contain empty path.'
    assert config.get_clang_executable() == 'clang', \
        'Must be path to clang executable.'
    assert not config.get_clang_additional_options(), \
        'Must have empty additional options.'
    assert config.get_clang_tidy_executable() == 'clang-tidy', \
        'Must be path to clang-tidy.'
    assert config.get_clang_tidy_config_file() == '.clang-tidy', \
        'Must be empty path string.'
    assert not config.get_clang_tidy_additional_options(), \
        'Must have empty additional options.'


def test_load_config_from_file(yaml_config):
    """Testing loading config from file."""
    config = cfg.Config(yaml_config)
    assert config.get_compile_commands() == 'tests/compile_commands.json', \
        'Must contain compile commands.'
    assert config.get_clang_executable() == 'clang', \
        'Must be path to default clang executable.'
    assert config.get_clang_tidy_executable() == '~/.local/bin/clang-tidy', \
        'Must be ~/.local/bin/clang-tidy.'
