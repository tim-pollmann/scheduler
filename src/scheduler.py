import logging
import sys
from abc import ABC, abstractmethod
from enums import ProcessStates


class Scheduler(ABC):
    def __init__(self, processes):
        self._time = 0
        self._ready_processes = []
        self._blocked_processes = []
        self._finished_processes = []

        for process in processes:
            if process.ready_time == self._time:
                self._ready_processes.append(process)
            else:
                self._blocked_processes.append(process)
        
        self._blocked_processes.sort(key=lambda p: p.ready_time)
        self._mainloop()
    
    def _mainloop(self):
        while len(self._ready_processes) + len(self._blocked_processes) > 0:
            if len(self._ready_processes) > 0:
                process, finished, used_time = self._run_next_process()

                self._time += used_time
                logging.info(f'Process "{process.name}" running')

                if finished:
                    self._ready_processes.remove(process)
                    self._finished_processes.append(process)
                    logging.info(f'Process "{process.name}" finished')

            else:
                self._time += 1

            self._update_blocked_processes()     

    def _update_blocked_processes(self):
        for blocked_process in self._blocked_processes:
            if blocked_process.ready_time > self._time:
                break

            process = self._blocked_processes.pop(0)
            self._ready_processes.append(process)
            logging.info(f'Process "{process.name} was added to the list of ready processes')

    @abstractmethod
    def _run_next_process(self):
        pass


class FCFS_Scheduler(Scheduler):
    def __init__(self, processes):
        super().__init__(processes)

    def _run_next_process(self):
        process = self._ready_processes[0]
        return [process, *process.run(sys.maxsize)]


class SJF_Scheduler(Scheduler):
    def __init__(self, processes):
        super().__init__(processes)

    def _run_next_process(self):
        process = min(self._ready_processes, key=lambda p: p.exec_time)
        return [process, *process.run(sys.maxsize)]


class LLF_Scheduler(Scheduler):
    def __init__(self, processes):
        super().__init__(processes)

    def _run_next_process(self):
        process = self._ready_processes[0]

        for process_candidate in self._ready_processes:
            if process_candidate.deadline - process_candidate.remaining_exec_time < process.deadline - process.remaining_exec_time:
                process = process_candidate

        return [process, *process.run(sys.maxsize)]
