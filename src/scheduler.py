from abc import ABC, abstractmethod, abstractstaticmethod


# base class for all schedulers
class Scheduler(ABC):
    def __init__(self, cpus, processes):
        self._cpus = cpus

        self._blocked_processes = processes
        self._ready_processes = []

        self._finish_times = []
        self._time = 0
        self._logger = ''

        # contents tuples of format (timestamp, cpu.cid, process.pid)
        self._allocation_history = []

    @property
    def allocation_history(self):
        return self._allocation_history

    @property
    def logger(self):
        return self._logger

    def avg_time(self):
        return sum(self._finish_times) / len(self._finish_times)

    # represents one cpu cycle
    def step(self):
        # 1. move processes, that got ready at the current time, from the blocked-list to the ready-list
        self._ready_processes.extend([p for p in self._blocked_processes if p.ready_time <= self._time])
        self._blocked_processes = [blocked_p for blocked_p in self._blocked_processes if
                                   blocked_p not in self._ready_processes]

        # 2. update process-allocation
        self._update_process_allocation()

        # 3. execute all allocated processes
        for cpu in self._cpus:
            if cpu.has_process:
                cpu.execute_process()

        # if there are no more ready, blocked or allocated processes we are finished
        if len(self._ready_processes) + len(self._blocked_processes) + len(
                [None for cpu in self._cpus if cpu.has_process]) == 0:
            self._log('Finished all processes')
            self._log(f'Average ready time was {self.avg_time()}')
            return False

        self._time += 1
        return True

    def _log(self, text):
        self._logger += '\n [TIME = ' + "{:2.0f}".format(self._time) + '] ' + text

    def _deallocate_finished_process(self, cpu):
        self._log(f'Finished process {cpu.current_process.pid}')
        cpu.deallocate_process()
        self._finish_times.append(self._time)

    def _allocate_process(self, cpu, process):
        self._ready_processes.remove(process)
        cpu.allocate_process(process)
        self._allocation_history.append((self._time, cpu.cid, process.pid))
        self._log(f'Allocated process {process.pid} to CPU #{cpu.cid}')

    # updates the cpu allocation (different for nonpreemtive and preemptive schedulers)
    @abstractmethod
    def _update_process_allocation(self):
        pass

    # sorts the processes based on the scheduler-strategy
    @abstractstaticmethod
    def _sort_processes(process):
        pass


# base class for all nonpreemptive schedulers
class NonPreemptiveScheduler(Scheduler, ABC):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    def _update_process_allocation(self):
        self._ready_processes.sort(key=self._sort_processes)

        for cpu in self._cpus:
            # if a cpus process has finished
            if cpu.has_finished_process:
                self._deallocate_finished_process(cpu)

            # if a cpu has no process and there are ready processes available
            if self._ready_processes and not cpu.has_process:
                self._allocate_process(cpu, self._ready_processes[0])


# base class for all nonpreemptive schedulers
class PreemptiveScheduler(Scheduler, ABC):
    def __init__(self, cpu, processes):
        super().__init__(cpu, processes)

    def _update_process_allocation(self):
        # currently allocated processes
        allocated_processes = [cpu.current_process for cpu in self._cpus if
                               cpu.has_process and not cpu.has_finished_process]

        # the best choice of all available processes
        candidates = allocated_processes + self._ready_processes
        candidates.sort(key=self._sort_processes)
        candidates = candidates[:min(len(self._cpus), len(candidates))]

        # processes, that need to be allocated
        not_allocated_candidates = set(candidates) - set(allocated_processes)

        for cpu in self._cpus:
            # if a cpu has a finished process
            if cpu.has_finished_process:
                self._deallocate_finished_process(cpu)

            # if there are ready process
            if self._ready_processes:
                # if a cpu has a process and that process is not the best choice
                if cpu.has_process and cpu.current_process not in candidates:
                    self._ready_processes.append(cpu.current_process)
                    cpu.deallocate_process()

                # if a cpu has no process
                if not cpu.has_process:
                    self._allocate_process(cpu, not_allocated_candidates.pop())


# class for nonpreemptive "first come first served"-schedulers
class NpFcfsScheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # no sorting needed
        return 0


# class for nonpreemptive "shortest job first"-schedulers
class NpSjfScheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by execution time
        return process.exec_time


# class for nonpreemptive "earliest deadline first"-schedulers
class NpEdfScheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by deadline
        return process.deadline


# class for nonpreemptive "least laxity first"-schedulers
class NpLlfScheduler(NonPreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by laxity
        return process.deadline - process.ready_time - process.exec_time


# class for preemptive "shortest job first"-schedulers
class PSjfScheduler(PreemptiveScheduler):
    def __init__(self, cpu, processes):
        super().__init__(cpu, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by execution time
        return process.exec_time


# class for preemptive "earliest deadline first"-schedulers
class PEdfScheduler(PreemptiveScheduler):
    def __init__(self, cpu, processes):
        super().__init__(cpu, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by deadline
        return process.deadline


# class for preemptive "round robin"-schedulers
class PRrScheduler(PreemptiveScheduler):
    def __init__(self, cpu, processes, quantum):
        self._quantum = quantum
        self._quantum_counter = -1
        self._current_index = -1
        self._last_process = None
        super().__init__(cpu, processes)

    @staticmethod
    def _sort_processes(self):
        pass
