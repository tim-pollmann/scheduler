import sys

class Process:
    def __init__(self, id, ready_time, exec_time, deadline=sys.maxsize):
        self._id = id
        self._ready_time = ready_time
        self._exec_time = exec_time
        self._deadline = deadline
        self._program_counter = 0

    @property
    def id(self):
        return self._id

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
    def is_finished(self):
        return self._exec_time <= self._program_counter

    def exec_atomic_command(self):
        self._program_counter += 1


class CPU:
    def __init__(self, id):
        self._id = id
        self._current_p = None
        self._history = []

    @property
    def id(self):
        return self._id

    @property
    def current_process(self):
        return self._current_p

    @property
    def history(self):
        return self._history

    @property
    def has_process(self):
        if self._current_p == None:
            return False
        return True

    @property
    def has_finished_process(self):
        if self.has_process and self._current_p.is_finished:
            return True
        return False

    def set_process(self, process):
        self._current_p = process

    def execute_process(self, timestamp):
        self._current_p.exec_atomic_command()
        self._history.append((timestamp, self._current_p.id))

    def unset_process(self):
        self._current_p = None