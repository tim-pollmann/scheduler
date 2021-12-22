from common import CPU
from abc import ABC, abstractmethod


# base class for all schedulers
class Scheduler(ABC):
    def __init__(self, processes, n_cpus):
        self._time = 0
        self._blocked_ps = processes
        self._ready_ps = []
        self._finished_ps = []
        self._cpus = [CPU(idx + 1) for idx in range(n_cpus)]
        self._logger = ''
        self._log(f'Initialized scheduler with {n_cpus} CPUs...')

    @property
    def cpus(self):
        return self._cpus

    @property
    def logger(self):
        return self._logger

    def _log(self, text):
        # add timestamp
        self._logger += '\n ' + text

    # calculates the average time needed for each process to be finished
    def avg_time(self):
        # some rework
        return 1334
        return sum([p.finished_time for p in self._finished_ps]) / len(self._finished_ps)
    
    def step(self):
        # while there are ready or blocked processes or processes currently running on a cpu
        if len(self._ready_ps) + len(self._blocked_ps) + len([None for cpu in self._cpus if cpu.has_process]) == 0:
            self._log(f'Average ready time was {self.avg_time()}...')
            return False
        # 1.) move processes, that got ready at the current time, from thre blocked-list to the ready-list
        self._ready_ps.extend([p for p in self._blocked_ps if p.ready_time <= self._time])
        self._blocked_ps = [blocked_p for blocked_p in self._blocked_ps if blocked_p not in self._ready_ps]
        # 2.) allocate processes to the cpus
        self._update_cpu_allocation()
    	# 3.) execute all allocated processes
        for cpu in self._cpus:
            if cpu.has_process:
                cpu.execute_process(self._time)
        
        self._time += 1
        return True

    # a method implemented by child classes that updates the cpu allocation (different for nonpreemtive and preemptive schedulers)
    @abstractmethod
    def _update_cpu_allocation(self):
        pass

    # a method implemented by child classes that returns the process to be executed based on its strategy
    @abstractmethod
    def _select_next_process(self):
        pass


# base class for all nonpreemptive schedulers
class NonPreemptiveScheduler(Scheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _update_cpu_allocation(self):
        for cpu in self._cpus:
            # if an cpus process has finished
            if cpu.has_finished_process:
                old_p = cpu.current_process
                cpu.unset_process()
                self._finished_ps.append(old_p)
                self._log(f'Finished process {old_p.id}...')
                
            # if a cpu is not allocated and there are ready processes
            if not cpu.has_process and self._ready_ps:
                next_p = self._select_next_process()
                self._ready_ps.remove(next_p)
                cpu.set_process(next_p)
                self._log(f'Allocated process {next_p.id} to CPU #{cpu.id}...')


# base class for all nonpreemptive schedulers
# this kind of schedulers have always just one processor available
class PreemptiveScheduler(Scheduler):
    def __init__(self, processes):
        super().__init__(processes, 1)

    def _update_cpu_allocation(self):
        # if the cpus process has finished
        if self._cpus[0].has_finished_process:
            self._cpus[0].process.finished_time = self._time
            self._finished_ps.append(self._cpus[0].process)
            self._log(f'Finished process {self._all_ps.index(self._cpus[0].process)}...')
        # if the cpu is allocated with an unfinished process
        elif self._cpus[0].has_process:
            self._ready_ps.append(self._cpus[0].process)
        self._cpus[0].unallocate()
        # if there are ready processes
        if self._ready_ps:
            self._cpus[0].allocate(self._select_next_process())
            self._ready_ps.remove(self._cpus[0].process)
            self._log(f'Allocated process {self._all_ps.index(self._cpus[0].process)}...')


# class for nonpreemtive "first come first served"-schedulers
class NP_FCFS_Scheduler(NonPreemptiveScheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        # just select the first process in the ready-list since the ready-list is in the order of the arrival of the processes
        return self._ready_ps[0]


# class for nonpreemtive "shortest job first"-schedulers
class NP_SJF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_ps, key=lambda p: p.exec_time)


# class for nonpreemtive "earliest deadline first"-schedulers
class NP_EDF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_ps, key=lambda p: p.deadline)


# class for nonpreemtive "least laxity first"-schedulers
class NP_LLF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, processes, n_cpus):
        super().__init__(processes, n_cpus)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest laxity
        return min(self._ready_ps, key=lambda p: p.deadline - p.ready_time - p.exec_time)


# class for preemtive "shortest job first"-schedulers
class P_SJF_Scheduler(PreemptiveScheduler):
    def __init__(self, processes):
        super().__init__(processes)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_ps, key=lambda p: p.exec_time)


# class for preemtive "earliest deadline first"-schedulers
class P_EDF_Scheduler(PreemptiveScheduler):
    def __init__(self, processes):
        super().__init__(processes)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_ps, key=lambda p: p.deadline)


# class for preemtive "round robin"-schedulers
# needs to be initialzied with an quantum
class P_RR_Scheduler(PreemptiveScheduler):
    def __init__(self, processes, quantum):
        self._quantum = quantum
        self._quantum_counter = -1
        self._current_index = -1
        self._last_process = None
        super().__init__(processes, 1)

    def _select_next_process(self):
        pass