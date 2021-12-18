import logging


class Process:
    def __init__(self, name, ready_time, exec_time, deadline):
        self._name = name
        self._ready_time = ready_time
        self._exec_time = exec_time
        self._deadline = deadline
        self._program_counter = 0
        logging.debug(f'Process "{self._name}" initialized')

    @property
    def name(self):
        return self._name

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

    # returns whether this process is finished and the amount of time it used
    def run(self, allocated_time):
        for exec_time in range(allocated_time):
            self._exec_atomic_command()

            if self._program_counter >= self._exec_time:
                return True, exec_time

        return False, allocated_time

    def _exec_atomic_command(self):
        self._program_counter += 1
        logging.debug(f'Process "{self._name}" executed atomic command #{self._program_counter}')
