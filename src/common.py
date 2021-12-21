class Process:
    def __init__(self, ready_time, exec_time, deadline):
        self._ready_time = ready_time
        self._exec_time = exec_time
        self._deadline = deadline
        self._program_counter = 0
        self._finished_time = None

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
    def remaining_exec_time(self):
        return self._exec_time - self._program_counter

    @property
    def laxity(self):
        return self._deadline - self.remaining_exec_time

    @property
    def is_finished(self):
        return self._exec_time <= self._program_counter

    @property
    def finished_time(self):
        return self._finished_time

    @finished_time.setter
    def finished_time(self, value):
        self._finished_time = value

    def exec_atomic_command(self):
        self._program_counter += 1
        if self._program_counter >= self._exec_time:
            return True
        return False


class CPU:
    def __init__(self):
        self._p = None

    @property
    def p(self):
        return self._p

    @p.setter
    def p(self, value):
        self._p = value

    @property
    def is_allocated(self):
        if self._p == None:
            return False
        return True