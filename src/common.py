import sys

class Process:
    def __init__(self, ready_time, exec_time, deadline=sys.maxsize):
        self._ready_time = ready_time
        self._exec_time = exec_time
        self._deadline = deadline
        self._program_counter = 0
        self._finished_time = -1
        self._history = []

    @property
    def ready_time(self):
        return self._ready_time

    @property
    def exec_time(self):
        return self._exec_time

    @property
    def deadline(self):
        return self._deadline

    @property
    def program_counter(self):
        return self._program_counter

    @property
    def finished_time(self):
        assert self._finished_time >= 0, "tried to access the finished time of a process, that has not been finished yet"
        return self._finished_time

    @finished_time.setter
    def finished_time(self, value):
        self._finished_time = value

    @property
    def is_finished(self):
        return self._exec_time <= self._program_counter

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        self._history = value

   

    def exec_atomic_command(self):
        self._program_counter += 1


class CPU:
    def __init__(self):
        self._p = None

    @property
    def process(self):
        return self._p

    @property
    def is_allocated(self):
        if self._p == None:
            return False
        return True

    @property
    def has_finished_process(self):
        if self.is_allocated and self._p.is_finished:
            return True
        return False

    def allocate(self, process):
        self._p = process

    def unallocate(self):
        self._p = None