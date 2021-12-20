import logging
from common import CPU
from abc import ABC, abstractmethod


class Scheduler(ABC):
    def __init__(self, processes, n_cpus, start_time=0):
        self._time = start_time
        self._ps = processes
        self._ready_ps = [p for p in self._ps if p.ready_time <= self._time]
        self._blocked_ps = [p for p in self._ps if p not in self._ready_ps]
        self._blocked_ps.sort(key=lambda p: p.ready_time)
        self._finished_ps = []
        self._cpus = [CPU() for _ in range(n_cpus)]
        self._update_cpu_allocation()

    def avg_ready_time(self):
        return sum([(len(self._finished_ps) - idx) * finished_p.exec_time for idx, finished_p in enumerate(self._finished_ps)]) / len(self._finished_ps)
    
    def start(self):
        while len(self._finished_ps) < len(self._ps):
            for cpu in self._cpus:
                if cpu.is_allocated:
                    cpu.p.exec_atomic_command()
                    logging.info(f'[TIME = {self._time}] Process "{self._ps.index(cpu.p) + 1}" running on CPU #{self._cpus.index(cpu) + 1}')
            self._update_cpu_allocation()
            self._update_blocked_processes()  
            self._time += 1
               
    def _update_blocked_processes(self):
        n = 0
        for blocked_p in self._blocked_ps:
            if blocked_p.ready_time > self._time:
                break
            self._ready_ps.append(blocked_p)
            n += 1
            logging.info(f'[TIME = {self._time}] Process "{self._ps.index(blocked_p) + 1} was added to the list of ready processes')
        self._blocked_ps = self._blocked_ps[n:]

    def _allocate_process(self, cpu):
        next_p = self._select_next_process()
        cpu.p = next_p
        self._ready_ps.remove(next_p)

    def _update_cpu_allocation(self):
        for cpu in self._cpus:
            if cpu.is_allocated:
                if cpu.p.is_finished:
                    logging.info(f'[TIME = {self._time}] Process "{self._ps.index(cpu.p) + 1}" finished')
                    self._finished_ps.append(cpu._p)
                    cpu._p = None
                    if len(self._ready_ps) > 0:
                        self._allocate_process(cpu)
            else:
                if len(self._ready_ps) > 0:
                    self._allocate_process(cpu)

    @abstractmethod
    def _select_next_process(self):
        pass


class FCFS_Scheduler(Scheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        return self._ready_ps[0]


class SJF_Scheduler(Scheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        return min(self._ready_ps, key=lambda p: p.exec_time)


class LLF_Scheduler(Scheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        return min(self._ready_ps, key=lambda p: p.laxity)
