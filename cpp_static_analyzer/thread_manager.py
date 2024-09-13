import threading
import cpp_static_analyzer.console as con

class ThreadManager:
    def __init__(self):
        self.threads = []

    def add_thread(self, thread):
        if not isinstance(thread, threading.Thread):
            con.trace('Cannot add thread.')
            con.error('Thread must be an instance of threading.Thread')
            return
        self.threads.append(thread)

    def remove_all_threads(self):
        for thread in self.threads:
            self.threads.remove(thread)
        self.threads.clear()

    def join_all_threads(self):
        for thread in self.threads:
            thread.join()

    def start_all_threads(self):
        for thread in self.threads:
            thread.start()
