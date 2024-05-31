# config_test.py

import config as cfg
import pytest
import yaml

@pytest.fixture
def config_string():
    return '''
    Checks:
      - -*
      - clang-analyzer-*
      - llvm-*
      - llvmlibc-*
    Warnings:
      - -Wall
      - -Wextra
    PathConverter:
      /Users/nus/test: /test
      /Users/nus/build: /build
    '''

@pytest.fixture
def empty_config_string():
    return '''
    Checks:
    Warnings:
    PathConverter:
    '''

def test_path_converter(config_string):
    config = yaml.safe_load(config_string)

    path_conv = cfg.get_path_converter(config)
    assert len(path_conv) == 2, 'Wrong number of paths.'

    for key, value in path_conv.items():
        if key == '/Users/nus/test':
            assert value == '/test', f'Value for {key} must be "/test"'
        elif key == '/Users/nus/build':
            assert value == '/build', f'Value for {key} must be "/build"'

def test_check_flags(config_string):
    config_yaml = yaml.safe_load(config_string)

    org_checks = cfg.get_check_flags(config_yaml)
    config = cfg.Config(config_yaml)
    checks = config.checks.split(',')
    for check in checks:
        assert check in org_checks, \
            f'Check {check} is not in the list of original checks.'

def test_warnings(config_string):
    config_yaml = yaml.safe_load(config_string)

    org_warnings = cfg.get_warnings(config_yaml)
    config = cfg.Config(config_yaml)
    warnings = config.warnings.split(' ')

    for warning in warnings:
        assert warning in org_warnings, \
            f'Warning {warning} is not in the list of original warnings.'

def test_empty_path_converter(empty_config_string):
    config = yaml.safe_load(empty_config_string)
    path_conv = cfg.get_path_converter(config)
    assert len(path_conv) == 0, 'Path converter must be empty.'

def test_empty_check_flags(empty_config_string):
    config_yaml = yaml.safe_load(empty_config_string)
    config = cfg.Config(config_yaml)
    checks = config.checks.split(',')
    assert len(checks) == 26, 'Must include all checks.'

def test_empty_warnings(empty_config_string):
    config_yaml = yaml.safe_load(empty_config_string)
    config = cfg.Config(config_yaml)
    warnings = config.warnings.split(' ')
    assert len(warnings) == 2, 'Must be default 2 warnings.'
