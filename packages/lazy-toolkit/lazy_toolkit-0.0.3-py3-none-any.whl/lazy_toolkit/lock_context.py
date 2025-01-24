from threading import Lock


class LockContext:
    def __init__(self, lock: Lock):
        self.acquired: bool = False
        self.__lock = lock

    def __enter__(self) -> 'LockContext':
        if self.__lock is not None:
            self.acquired = self.__lock.acquire(blocking=False)
        else:
            self.acquired = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            self.__lock.release()
