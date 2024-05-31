# config_test.py

import config as cfg
import pytest
import yaml

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
