"""Testing thread manager."""

import threading
import pytest
import cpp_static_analyzer.thread_manager as tm


@pytest.fixture(name="thread_manager")
def fixture_thread_manager():
    """Thread manager fixture."""
    return tm.ThreadManager()


class MockJobManager:
    """Mocking simple job manager."""
    def __init__(self):
        self._lock = threading.Lock()
        self._count = 0

    def job(self):
        """Job function."""
        for _ in range(10):
            with self._lock:
                self._count += 1

    def count_equal(self, num):
        """Count checker."""
        return self._count == num


def test_thread_manager(thread_manager):
    """Testing thread manager."""
    job_mgr = MockJobManager()

    thread_manager.add_thread(threading.Thread(target=MockJobManager.job,
                                               args=(job_mgr,)))
    thread_manager.add_thread(threading.Thread(target=MockJobManager.job,
                                               args=(job_mgr,)))
    thread_manager.add_thread(threading.Thread(target=MockJobManager.job,
                                               args=(job_mgr,)))

    thread_manager.start_all_threads()
    thread_manager.join_all_threads()
    thread_manager.remove_all_threads()

    assert job_mgr.count_equal(30), 'Must be 30.'
