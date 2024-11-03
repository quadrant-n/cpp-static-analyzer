"""Thread manager for executing static analyzer jobs."""

import threading
import cpp_static_analyzer.console as con


class ThreadManager:
    """Thread manager instance."""

    threads = []

    def add_thread(self, thread):
        """Add a thread to manager."""
        if not isinstance(thread, threading.Thread):
            con.trace('Cannot add thread.')
            con.error('Thread must be an instance of threading.Thread')
            return
        self.threads.append(thread)

    def remove_all_threads(self):
        """Remove all registered threads."""
        for thread in self.threads:
            self.threads.remove(thread)
        self.threads.clear()

    def join_all_threads(self):
        """Join all registered threads."""
        for thread in self.threads:
            thread.join()

    def start_all_threads(self):
        """Start all registered threads."""
        for thread in self.threads:
            thread.start()
