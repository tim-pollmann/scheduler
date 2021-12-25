from abc import ABC, abstractmethod, abstractstaticmethod


# base class for all schedulers
class Scheduler(ABC):
    def __init__(self, cpus, processes):
        self._cpus = cpus

        self._blocked_processes = processes
        self._ready_processes = []

        self._time = 0
        self._logger = ''

        # contents tuples of format (timestamp, cpu.cid, process)
        self._allocation_history = []

    @property
    def allocation_history(self):
        return self._allocation_history

    @property
    def logger(self):
        return self._logger

    def avg_delta_time(self):
        process_delta_times = {}

        # search the maximum time-interval between the ready-time and the last occurrence in the allocation history
        # for each process
        # since the last occurrence must bethe finish time, this interval represents the delta for each process
        for timestamp, _, process in self._allocation_history:
            process_delta_times[process.pid] = max(timestamp - process.ready_time + 1,
                                                   process_delta_times.get(process.pid, -1))

        return sum(process_delta_times.values()) / len(process_delta_times)

    # represents one clock-cycle
    def step(self):
        # one clock-cycle consists of the following 3 steps

        # 1. move processes, that got ready at the current time, from the blocked-list to the ready-list
        self._ready_processes.extend([p for p in self._blocked_processes if p.ready_time <= self._time])
        self._blocked_processes = [blocked_p for blocked_p in self._blocked_processes
                                   if blocked_p not in self._ready_processes]

        # 2. update process-allocation
        self._update_process_allocation()

        # 3. execute all allocated processes on their corresponding cpus
        for cpu in self._cpus:
            if cpu.has_process:
                cpu.execute_process()
                self._allocation_history.append((self._time, cpu.cid, cpu.current_process))

        # if there are no more ready, blocked or allocated processes we are finished
        if len(self._ready_processes) + len(self._blocked_processes) + len(
                [None for cpu in self._cpus if cpu.has_process]) == 0:
            self._log('Finished all processes')
            self._log(f'Average ready time was {self.avg_delta_time()}')
            return False

        self._time += 1
        return True

    def _log(self, text):
        self._logger += '\n [TIME = ' + "{:2.0f}".format(self._time) + '] ' + text

    def _deallocate_finished_process(self, cpu):
        self._log(f'Finished process {cpu.current_process.pid}')
        cpu.deallocate_process()

    def _allocate_process(self, cpu, process):
        self._ready_processes.remove(process)
        cpu.allocate_process(process)
        self._log(f'Allocated process {process.pid} to CPU #{cpu.cid}')

    # updates the cpu allocation (different for nonpreemtive and preemptive schedulers)
    # will be implemented by "NonPreemptiveScheduler" and "PreemptiveScheduler"
    @abstractmethod
    def _update_process_allocation(self):
        pass

    # sorts the processes based on the scheduler-strategy
    # will be implemented by the ultimate schedulers
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
            if cpu.has_finished_process:
                self._deallocate_finished_process(cpu)

            # if there are ready process available
            if self._ready_processes:
                # if a cpu has a process and that process is not the best choice
                if cpu.has_process and cpu.current_process not in candidates:
                    self._ready_processes.append(cpu.current_process)
                    cpu.deallocate_process()

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
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by execution time
        return process.exec_time


# class for preemptive "earliest deadline first"-schedulers
class PEdfScheduler(PreemptiveScheduler):
    def __init__(self, cpus, processes):
        super().__init__(cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by deadline
        return process.deadline


# class for preemptive "round robin"-schedulers
# this scheduler has only one cpu to work with
class PRrScheduler(PreemptiveScheduler):
    def __init__(self, cpu, processes, quantum):
        super().__init__([cpu], processes)
        self._quantum = quantum
        self._quantum_counter = 0

    # since the "round robin"-scheduler is mainly different from the other preemptive schedulers, we override this
    # function and implement the "round robin"-schedulers own logic in there
    def _update_process_allocation(self):
        cpu = self._cpus[0]

        if cpu.has_finished_process:
            self._deallocate_finished_process(cpu)

        if self._ready_processes:
            if self._quantum_counter >= self._quantum and cpu.has_process:
                self._ready_processes.append(cpu.current_process)
                cpu.deallocate_process()

            # if a cpu has no process
            if not cpu.has_process:
                self._quantum_counter = 0
                self._allocate_process(cpu, self._ready_processes[0])

        self._quantum_counter += 1

    @staticmethod
    def _sort_processes(process):
        # since we override _update_process_allocation() and we do not use this function there, there is no need to
        # properly implement this function
        pass
