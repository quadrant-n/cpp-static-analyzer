"""Test cases for command manager,"""
import cpp_static_analyzer.command_manager as cm


def test_command_manager():
    """Testing command manager."""
    cmd_mgr = cm.CommandManager('tests/compile_commands.json')
    assert len(cmd_mgr) == 3, 'Must have four commands.'

    ii = cmd_mgr.next_index()
    assert ii == 0, 'Must be 0.'

    ii = cmd_mgr.next_index()
    assert ii == 1, 'Must be 1.'

    ii = cmd_mgr.next_index()
    assert ii == 2, 'Must be 2.'

    ii = cmd_mgr.next_index()
    assert ii == -1, 'Must be -1.'
