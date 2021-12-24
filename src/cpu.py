class CPU:
    def __init__(self, id):
        self._id = id
        self._current_process = None
        self._timestamps = []
        self._pids = []

    @property
    def id(self):
        return self._id

    @property
    def current_process(self):
        return self._current_process

    @property
    def history(self):
        return self._timestamps, self._pids

    @property
    def has_process(self):
        if self._current_process == None:
            return False
        return True

    @property
    def has_finished_process(self):
        if self.has_process and self._current_process.is_finished:
            return True
        return False

    def set_process(self, process):
        self._current_process = process

    def unset_process(self):
        self._current_process = None

    def execute_process(self, timestamp):
        self._current_process.exec_atomic_command()
        self._timestamps.append(timestamp)
        self._pids.append(self._current_process.id)
