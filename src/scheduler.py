import logging
from common import CPU
from abc import ABC, abstractmethod


class Scheduler(ABC):
    def __init__(self, processes, n_cpus):
        self._time = 0
        self._ps = processes
        self._blocked_ps = self._ps
        self._ready_ps = []
        self._finished_ps = []
        self._cpus = [CPU() for _ in range(n_cpus)]

    def avg_ready_time(self):
        print([p.finished_time for p in self._finished_ps])
        return sum([p.finished_time for p in self._finished_ps]) / len(self._finished_ps)
    
    def start(self):
        while len(self._finished_ps) < len(self._ps):
            self._update_ready_processes()
            self._update_cpu_allocation()
            self._run_allocated_processes()
            self._time += 1

    def _update_ready_processes(self):
        ready_ps = [p for p in self._blocked_ps if p.ready_time <= self._time]
        self._ready_ps.extend(ready_ps)
        self._blocked_ps = [blocked_p for blocked_p in self._blocked_ps if blocked_p not in ready_ps]
        for p in ready_ps:
            logging.info(f'[TIME = {self._time}] Process "{self._ps.index(p) + 1}" was added to the list of ready processes')
        

    @abstractmethod
    def _update_cpu_allocation(self):
        pass

    def _run_allocated_processes(self):
        for cpu in self._cpus:
            if cpu.is_allocated:
                cpu.p.exec_atomic_command()
                logging.info(f'[TIME = {self._time}] Process "{self._ps.index(cpu.p) + 1}" running on CPU #{self._cpus.index(cpu) + 1}')


class NonPreemptiveScheduler(Scheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _update_cpu_allocation(self):
        for cpu in self._cpus:
            if cpu.is_allocated and cpu.p.is_finished:
                logging.info(f'[TIME = {self._time - 1}] Process "{self._ps.index(cpu.p) + 1}" finished')
                cpu.p.finished_time = self._time
                self._finished_ps.append(cpu.p)
                cpu._p = None
            if (not cpu.is_allocated or (cpu.is_allocated and cpu.p.is_finished)) and len(self._ready_ps) > 0:
                next_p = self._select_next_process()
                cpu.p = next_p
                self._ready_ps.remove(next_p)

    @abstractmethod
    def _select_next_process(self):
        pass


class FCFS_Scheduler(NonPreemptiveScheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        return self._ready_ps[0]


class SJF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        return min(self._ready_ps, key=lambda p: p.exec_time)


class LLF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        return min(self._ready_ps, key=lambda p: p.laxity)


class RR_Scheduler(Scheduler):
    def __init__(self, processes, quantum):
        self._quantum = quantum
        self._quantum_counter = -1
        self._current_index = -1
        super().__init__(processes, 1)

    def _update_cpu_allocation(self):
        self._quantum_counter += 1
        cpu = self._cpus[0]
        if cpu.is_allocated and cpu.p.is_finished:
            cpu.p.finished_time = self._time
            self._finished_ps.append(cpu.p)
            self._ready_ps.remove(cpu.p)
            self._quantum_counter = 0
            logging.info(f'[TIME = {self._time}] Process "{self._ps.index(cpu.p) + 1}" finished')
        elif self._quantum_counter % self._quantum == 0:
                self._quantum_counter = 0
                self._current_index += 1
        if self._current_index >= len(self._ready_ps):
            self._current_index = 0
        if len(self._ready_ps) > 0:
            cpu.p = self._ready_ps[self._current_index]
        
