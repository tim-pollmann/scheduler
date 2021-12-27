class Process:
    def __init__(self, id, ready_time, exec_time, deadline):
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
    def is_finished(self):
        return self._exec_time <= self._program_counter

    def exec_atomic_command(self):
        self._program_counter += 1
