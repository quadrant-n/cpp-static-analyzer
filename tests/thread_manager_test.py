import thread_manager as tm
import threading
import pytest

@pytest.fixture
def thread_manager():
    return tm.ThreadManager()

class MockJobManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._count = 0

    def job(self):
        for _ in range(10):
            self._lock.acquire()
            try:
                self._count += 1
            finally:
                self._lock.release()

def test_thread_manager(thread_manager):
    job_mgr = MockJobManager()

    thread_manager.add_thread(threading.Thread(target=MockJobManager.job, args=(job_mgr,)))
    thread_manager.add_thread(threading.Thread(target=MockJobManager.job, args=(job_mgr,)))
    thread_manager.add_thread(threading.Thread(target=MockJobManager.job, args=(job_mgr,)))

    thread_manager.start_all_threads()
    thread_manager.join_all_threads()
    thread_manager.remove_all_threads()

    assert job_mgr._count == 30, 'Must be 30.'
