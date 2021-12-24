from abc import ABC, abstractmethod
from cpu import CPU
from process import Process


# base class for all schedulers
class Scheduler(ABC):
    def __init__(self, cpus, processes):
        self._cpus = cpus
        
        self._blocked_processes = processes
        self._ready_processes = []

        self._finish_times = []

        self._time = 0
        self._logger = ''

    @property
    def cpus(self):
        return self._cpus

    @property
    def logger(self):
        return self._logger

    def _log(self, text):
        self._logger += '\n [TIME = ' + "{:2.0f}".format(self._time) + '] ' + text

    # calculates the average time needed for each process to be finished
    def avg_time(self):
        return sum(self._finish_times) / len(self._finish_times)
    
    def step(self):
        # 1.) move processes, that got ready at the current time, from thre blocked-list to the ready-list
        self._ready_processes.extend([p for p in self._blocked_processes if p.ready_time <= self._time])
        self._blocked_processes = [blocked_p for blocked_p in self._blocked_processes if blocked_p not in self._ready_processes]
        # 2.) allocate processes to the cpus
        self._update_cpu_allocation()
    	# 3.) execute all allocated processes
        for cpu in self._cpus:
            if cpu.has_process:
                cpu.execute_process(self._time)

        if len(self._ready_processes) + len(self._blocked_processes) + len([None for cpu in self._cpus if cpu.has_process]) == 0:
            self._log(f'Average ready time was {self.avg_time()}...')
            return False
        
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
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    def _update_cpu_allocation(self):
        for cpu in self._cpus:
            # if a cpus process has finished
            if cpu.has_finished_process:
                self._log(f'Finished process {cpu.current_process.id}')
                cpu.unset_process()
                self._finish_times.append(self._time)

            # if a cpu has no process and there are ready processes available
            if not cpu.has_process and self._ready_processes:
                next_p = self._select_next_process()
                self._ready_processes.remove(next_p)
                cpu.set_process(next_p)
                self._log(f'Allocated process {next_p.id} to CPU #{cpu.id}')


# base class for all nonpreemptive schedulers
# this kind of schedulers have always just one processor available
class PreemptiveScheduler(Scheduler):
    def __init__(self, processes):
        super().__init__(1, processes)

    def _update_cpu_allocation(self):
        cpu = self._cpus[0]

        # if the cpus process has finished
        if cpu.has_finished_process:
            self._log(f'Finished process {cpu.current_process.id}')
            cpu.unset_process()
            self._finish_times.append(self._time)

        # if the cpu is allocated with an unfinished process
        elif cpu.has_process:
            #logging and maybe check if switch is necesseray
            self._ready_processes.append(cpu.current_process)


        # check if better process available
        cpu.unset_process()

        # if there are ready processes
        if self._ready_processes:
            #maybe in function
            next_p = self._select_next_process()
            self._ready_processes.remove(next_p)
            cpu.set_process(next_p)
            self._log(f'Allocated process {next_p.id} to CPU #{cpu.id}')


# class for nonpreemtive "first come first served"-schedulers
class NP_FCFS_Scheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    def _select_next_process(self):
        # just select the first process in the ready-list since the ready-list is in the order of the arrival of the processes
        return self._ready_processes[0]


# class for nonpreemtive "shortest job first"-schedulers
class NP_SJF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_processes, key=lambda p: p.exec_time)


# class for nonpreemtive "earliest deadline first"-schedulers
class NP_EDF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_processes, key=lambda p: p.deadline)


# class for nonpreemtive "least laxity first"-schedulers
class NP_LLF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest laxity
        return min(self._ready_processes, key=lambda p: p.deadline - p.ready_time - p.exec_time)


# class for preemtive "shortest job first"-schedulers
class P_SJF_Scheduler(PreemptiveScheduler):
    def __init__(self, processes):
        super().__init__(processes)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_processes, key=lambda p: p.exec_time)


# class for preemtive "earliest deadline first"-schedulers
class P_EDF_Scheduler(PreemptiveScheduler):
    def __init__(self, processes):
        super().__init__(processes)

    def _select_next_process(self):
        # select the process from the ready-list, that has the lowest execution time
        return min(self._ready_processes, key=lambda p: p.deadline)


# class for preemtive "round robin"-schedulers
# needs to be initialzied with an quantum
class P_RR_Scheduler(PreemptiveScheduler):
    def __init__(self, processes, quantum):
        self._quantum = quantum
        self._quantum_counter = -1
        self._current_index = -1
        self._last_process = None
        super().__init__(processes)

    def _select_next_process(self):
        pass