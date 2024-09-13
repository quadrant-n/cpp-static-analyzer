# config_test.py

import cpp_static_analyzer.config as cfg
import pytest
import yaml
import os



@pytest.fixture
def yaml_config():
    yaml_string = '''
    Checks:
      - -*
      - clang-analyzer-*
      - llvm-*
      - llvmlibc-*
    Warnings:
      - -Wall
      - -Wextra
    HeaderFilterRegex: .*\/project\/.*
    PathConverter:
      /Users/nus/test: /test
      /Users/nus/build: /build
    '''
    return yaml.safe_load(yaml_string)

@pytest.fixture
def yaml_empty_config():
    yaml_string = '''
    Checks:
    Warnings:
    PathConverter:
    HeaderFilterRegex:
    '''
    return yaml.safe_load(yaml_string)

@pytest.fixture
def file_in_nested_directory():
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/deep/nested/directory/for/testing.txt')

@pytest.fixture
def nested_directory():
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/deep/nested/directory/for/')

@pytest.fixture
def directory_not_exist():
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/not_exist')



# Helper.
def config_yml_file_path():
    cwd = os.getcwd()
    return os.path.join(cwd, 'tests/deep/config.yml')



def test_path_converter(yaml_config):
    path_conv = cfg.get_path_converter(yaml_config)
    assert len(path_conv) == 2, 'Wrong number of paths.'

    for key, value in path_conv.items():
        if key == '/Users/nus/test':
            assert value == '/test', f'Value for {key} must be "/test"'
        elif key == '/Users/nus/build':
            assert value == '/build', f'Value for {key} must be "/build"'

def test_check_flags(yaml_config):
    org_checks = cfg.get_check_flags(yaml_config)
    config = cfg.Config(yaml_config)
    checks = config.checks.split(',')

    for check in checks:
        assert check in org_checks, \
            f'Check {check} is not in the list of original checks.'

def test_warnings(yaml_config):
    org_warnings = cfg.get_warnings(yaml_config)
    config = cfg.Config(yaml_config)

    for warning in config.warnings:
        assert warning in org_warnings, \
            f'Warning {warning} is not in the list of original warnings.'

def test_header_filter(yaml_config):
    config = cfg.Config(yaml_config)
    assert config.header_filter == '.*\/project\/.*', \
        'Not valid header filter.'

def test_empty_path_converter(yaml_empty_config):
    path_conv = cfg.get_path_converter(yaml_empty_config)
    assert len(path_conv) == 0, 'Path converter must be empty.'

def test_empty_check_flags(yaml_empty_config):
    config = cfg.Config(yaml_empty_config)
    checks = config.checks.split(',')
    assert len(checks) == 26, 'Must include all checks.'

def test_empty_warnings(yaml_empty_config):
    config = cfg.Config(yaml_empty_config)
    assert len(config.warnings) == 2, 'Must be default 2 warnings.'

def test_empty_header_filter(yaml_empty_config):
    config = cfg.Config(yaml_empty_config)
    assert config.header_filter == '', 'Header filter must be empty.'

def test_search_for_config(nested_directory):
    config_path = cfg.search_for_config_file(nested_directory)
    config_yml_path = config_yml_file_path()
    assert config_path == config_yml_path, 'Must find config.yml.'

def test_search_for_config_using_file(file_in_nested_directory):
    config_path = cfg.search_for_config_file(file_in_nested_directory)
    config_yml_path = config_yml_file_path()
    assert config_path == config_yml_path, 'Must find config.yml.'

def test_search_for_config_not_exist(directory_not_exist):
    config_path = cfg.search_for_config_file(directory_not_exist)
    assert config_path == '', 'Must be an empty string.'
