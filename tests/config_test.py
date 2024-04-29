# config_test.py

import config as cfg
import pytest
import yaml

@pytest.fixture
def config_string():
    return '''
        Checks:
            cert: 1
            clang-analyzer: 1
            concurrency: 1
            cppcoreguidelines: 1
            google: 1
            hicpp: 1
            llvm: 1
            llvmlibc: 1
            misc: 1
            modernize: 1
            portability: 1
            readability: 1
        PathConverter:
            /Users/nus/test: /test
            /Users/nus/build: /build
    '''

def test_path_converter(config_string):
    config = yaml.safe_load(config_string)

    path_conv = cfg.getPathConverter(config)
    assert len(path_conv) == 2, 'Wrong number of paths.'

    for key, value in path_conv.items():
        if key == '/Users/nus/test':
            assert value == '/test', 'Value for {key} must be "/test"'
        elif key == '/Users/nus/build':
            assert value == '/build', 'Value for {key} must be "/build"'

def test_check_flags(config_string):
    config = yaml.safe_load(config_string)

    checks = cfg.getCheckFlags(config)
    assert len(checks) == 25, 'There must be 25 check flags.'

    org_flags = config['Checks']
    for key, value in checks.items():
        if key in org_flags:
            assert org_flags[key] == value, '{key} must be {org_flags[key]}.'
        else:
            assert value == 0, '{key} must be 0.'
