from abc import ABC, abstractclassmethod, abstractmethod, abstractstaticmethod


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

    def _unset_finished_process(self, cpu):
        self._log(f'Finished process {cpu.current_process.id}')
        cpu.unset_process()
        self._finish_times.append(self._time)

    def _set_process(self, cpu, process):
        self._ready_processes.remove(process)
        cpu.set_process(process)
        self._log(f'Allocated process {process.id} to CPU #{cpu.id}')

    def avg_time(self):
        return sum(self._finish_times) / len(self._finish_times)
    
    # represents one cpu cycle
    def step(self):
        # 1. move processes, that got ready at the current time, from the blocked-list to the ready-list
        self._ready_processes.extend([p for p in self._blocked_processes if p.ready_time <= self._time])
        self._blocked_processes = [blocked_p for blocked_p in self._blocked_processes if blocked_p not in self._ready_processes]

        # 2. update cpu-allocation
        self._update_cpu_allocation()

    	# 3. execute processes on all allocated cpus
        for cpu in self._cpus:
            if cpu.has_process:
                cpu.execute_process(self._time)

        # if there are no more ready, blocked or allocated processes we are finished
        if len(self._ready_processes) + len(self._blocked_processes) + len([None for cpu in self._cpus if cpu.has_process]) == 0:
            self._log(f'Average ready time was {self.avg_time()}')
            return False
        
        self._time += 1
        return True

    # updates the cpu allocation (different for nonpreemtive and preemptive schedulers)
    @abstractmethod
    def _update_cpu_allocation(self):
        pass

    # sorts the processes based on the scheduler-strategy
    @abstractstaticmethod
    def _sort_processes(process):
        pass


# base class for all nonpreemptive schedulers
class NonPreemptiveScheduler(Scheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    def _update_cpu_allocation(self):
        self._ready_processes.sort(key=self._sort_processes)
        
        for cpu in self._cpus:
            # if a cpus process has finished
            if cpu.has_finished_process:
                self._unset_finished_process(cpu)

            # if a cpu has no process and there are ready processes available
            if self._ready_processes and not cpu.has_process:
                cpu.set_process(self._ready_processes.pop(0))


# base class for all nonpreemptive schedulers
class PreemptiveScheduler(Scheduler):
    def __init__(self, cpu, processes):
        super().__init__(cpu, processes)

    def _update_cpu_allocation(self):
        # currently allocated processes
        allocated_processes = [cpu.current_process for cpu in self._cpus if cpu.has_process and not cpu.has_finished_process]

        # the best choice of all available processes
        candidates = allocated_processes + self._ready_processes
        candidates.sort(key=self._sort_processes)
        candidates = candidates[:min(len(self._cpus), len(candidates))]

        # processes, that need to be allocated
        not_allocated_candidates = set(candidates) - set(allocated_processes)      

        for cpu in self._cpus:
            # if a cpu has a finished process
            if cpu.has_finished_process:
                self._unset_finished_process(cpu)

            # if there are ready process
            if self._ready_processes:
                # if a cpu has a process and that prcess is not the best choice
                if cpu.has_process and cpu.current_process not in candidates:
                    self._ready_processes.append(cpu.current_process)
                    cpu.unset()

                # if a cpu has no process
                if not cpu.has_process:
                    self._set_process(cpu, not_allocated_candidates.pop())


# class for nonpreemtive "first come first served"-schedulers
class NP_FCFS_Scheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # no sorting needed
        return 0


# class for nonpreemtive "shortest job first"-schedulers
class NP_SJF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by execution time
        return process.exec_time


# class for nonpreemtive "earliest deadline first"-schedulers
class NP_EDF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by deadline
        return process.deadline


# class for nonpreemtive "least laxity first"-schedulers
class NP_LLF_Scheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by laxity
        return process.deadline - process.ready_time - process.exec_time


# class for preemtive "shortest job first"-schedulers
class P_SJF_Scheduler(PreemptiveScheduler):
    def __init__(self, cpu, processes):
        super().__init__(cpu, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by execution time
        return process.exec_time


# class for preemtive "earliest deadline first"-schedulers
class P_EDF_Scheduler(PreemptiveScheduler):
    def __init__(self, cpu, processes):
        super().__init__(cpu, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by deadline
        return process.deadline


# class for preemtive "round robin"-schedulers
class P_RR_Scheduler(PreemptiveScheduler):
    def __init__(self, cpu, processes, quantum):
        self._quantum = quantum
        self._quantum_counter = -1
        self._current_index = -1
        self._last_process = None
        super().__init__(cpu, processes)

    def _sort_processes(self):
        pass