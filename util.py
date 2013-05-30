#encoding=utf-8
import threading


class ThreadFetcher(threading.Thread):
    def __init__(self, lock, instance):
        super(self, ThreadFetcher).__init__(name = ''.join(['thread_', instance.name]))
        lock.acquire()
        lock.release()

    def  run(self):
        pass
