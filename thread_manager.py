import threading

class ThreadManager:
    def __init__(self):
        self.threads = []

    def add_thread(self, thread):
        if not isinstance(thread, threading.Thread):
            print('Thread must be an instance of threading.Thread')
            return
        self.threads.append(thread)

    def remove_thread(self, thread):
        if not isinstance(thread, threading.Thread):
            print('Thread must be an instance of threading.Thread')
        self.threads.remove(thread)

    def get_threads(self):
        return self.threads[:]

# Example usage:
manager = ThreadManager()

# Create threads and add them to the manager
thread1 = threading.Thread(target=print_hello)
thread2 = threading.Thread(target=print_world)
manager.add_thread(thread1)
manager.add_thread(thread2)

# Start all the threads
for thread in manager.get_threads():
    thread.start()

# Wait for all the threads to finish
for thread in manager.get_threads():
    thread.join()

def print_hello():
    for i in range(5):
        print("Hello!")

def print_world():
    for i in range(5):
        print("World!")
