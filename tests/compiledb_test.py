# compiledb_test.py

import pytest
import compiledb as cbd

def test_success():
    print('Test succcess.')
    assert 'a' == 'a'

def test_failed():
    print('Test failed.')
    assert 'a' == 'b'
