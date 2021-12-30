from abc import ABC, abstractmethod
from cpu import CPU


# base class for all schedulers
class Scheduler(ABC):
    def __init__(self, n_cpus, processes):
        self._cpus = [CPU(idx + 1) for idx in range(n_cpus)]

        self._blocked_processes = processes
        self._ready_processes = []

        self._time = 0
        self._logger = ''

        # elapsed times between the timestamp the process got ready and the timestamp it finished
        self._delta_times = []

    # returns the current cpu allocation for each cpu as tuple of (timestamp, cpu.id, process.id)
    @property
    def last_allocation(self):
        return [(self._time - 1, cpu.id, cpu.current_process.id) for cpu in self._cpus if cpu.has_process]

    @property
    def logger(self):
        return self._logger

    @property
    def avg_delta_time(self):
        return '{:4.2f}'.format(sum(self._delta_times) / len(self._delta_times))

    # runs the complete simulation until all processes are finished
    def run_until_finished(self):
        while self.step():
            pass

    # represents one clock-cycle
    def step(self):
        # one clock-cycle consists of the following 3 steps
        # 1. move processes, that got ready at the current time, from the blocked-list to the ready-list
        self._ready_processes.extend([process for process in self._blocked_processes
                                      if process.ready_time <= self._time])
        self._blocked_processes = [blocked_process for blocked_process in self._blocked_processes
                                   if blocked_process not in self._ready_processes]

        # 2. update process-allocation
        self._update_process_allocation()

        # 3. execute all allocated processes on their corresponding cpus
        for cpu in self._cpus:
            if cpu.has_process:
                cpu.execute_process()

        # if there are no more ready, blocked or allocated processes we are finished
        if len(self._ready_processes) + len(self._blocked_processes) + len(
                [None for cpu in self._cpus if cpu.has_process]) == 0:
            self._log('Finished all processes')
            self._log(f'Average delta time was {self.avg_delta_time}')
            return False

        self._time += 1
        return True

    def _log(self, text):
        self._logger += ' [TIME = ' + '{:2.0f}'.format(self._time) + '] ' + text + '\n'

    def _allocate_process(self, cpu, process):
        self._ready_processes.remove(process)
        cpu.allocate_process(process)
        self._log(f'Allocated process {process.id} to CPU #{cpu.id}')

    def _deallocate_process(self, cpu):
        self._log(f'Deallocated process {cpu.current_process.id} from CPU #{cpu.id}')
        self._ready_processes.append(cpu.current_process)
        cpu.deallocate_process()

    def _deallocate_finished_process(self, cpu):
        self._log(f'Finished process {cpu.current_process.id}')
        self._delta_times.append(self._time - cpu.current_process.ready_time)
        cpu.deallocate_process()

    # updates the cpu allocation (different for nonpreemtive and preemptive schedulers)
    # will be implemented by "NonPreemptiveScheduler" and "PreemptiveScheduler"
    @abstractmethod
    def _update_process_allocation(self):
        pass

    # sorts the processes based on the scheduler-strategy
    # will be implemented by the schedulers
    @staticmethod
    @abstractmethod
    def _sort_processes(process):
        pass


# base class for all nonpreemptive schedulers
class NonPreemptiveScheduler(Scheduler, ABC):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

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
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    def _update_process_allocation(self):
        # currently allocated processes
        allocated_processes = [cpu.current_process for cpu in self._cpus if
                               cpu.has_process and not cpu.has_finished_process]

        # get processes that need to be allocated in the next cycle base on the scheduling strategy
        all_processes = allocated_processes + self._ready_processes
        all_processes.sort(key=self._sort_processes)
        next_processes = all_processes[:min(len(self._cpus), len(all_processes))]

        # next processes that are not allocated yet
        not_allocated_processes = set(next_processes) - set(allocated_processes)

        for cpu in self._cpus:
            if cpu.has_finished_process:
                self._deallocate_finished_process(cpu)

            # if there are ready process available
            if self._ready_processes:
                # if a cpu has a process but that process is not meant to run in the next clock cycle
                if cpu.has_process and cpu.current_process not in next_processes:
                    self._deallocate_process(cpu)

                # if a cpu is free we can allocate any process
                if not cpu.has_process:
                    self._allocate_process(cpu, not_allocated_processes.pop())


# class for nonpreemptive "first come first serve"-schedulers
class NpFcfsScheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # no sorting needed
        return 0


# class for nonpreemptive "shortest job first"-schedulers
class NpSjfScheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by execution time
        return process.exec_time


# class for nonpreemptive "earliest deadline first"-schedulers
class NpEdfScheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by deadline
        return process.deadline


# class for nonpreemptive "least laxity first"-schedulers
class NpLlfScheduler(NonPreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by laxity
        # we do not need to consider the current timestamp here because it would be the same for every process
        # since this is preemptive we do not need to consider the program counter either
        return process.deadline - process.ready_time - process.exec_time


# class for preemptive "shortest job first"-schedulers
class PSjfScheduler(PreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by remaining execution time
        return process.exec_time - process.program_counter


# class for preemptive "earliest deadline first"-schedulers
class PEdfScheduler(PreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by deadline
        return process.deadline


# class for preemptive "least laxity first"-schedulers
class PLlfScheduler(PreemptiveScheduler):
    def __init__(self, n_cpus, processes):
        super().__init__(n_cpus, processes)

    @staticmethod
    def _sort_processes(process):
        # sort by laxity
        # we do not need to consider the current timestamp here because it would be the same for every process
        return process.deadline - process.ready_time - process.exec_time + process.program_counter


# class for preemptive "round robin"-schedulers
# this scheduler has only one cpu to work with
class PRrScheduler(PreemptiveScheduler):
    def __init__(self, processes, quantum):
        super().__init__(1, processes)
        self._quantum = quantum
        self._quantum_counter = 0

    # since the "round robin"-scheduler is mainly different from the other preemptive schedulers, we override this
    # function and implement the "round robin"-schedulers own logic here
    def _update_process_allocation(self):
        cpu = self._cpus[0]

        if cpu.has_finished_process:
            self._deallocate_finished_process(cpu)

        # if there are ready process available
        if self._ready_processes:
            # if the current process had the cpu for quantum clock cycles
            if self._quantum_counter >= self._quantum and cpu.has_process:
                self._deallocate_process(cpu)

            # if the cpu has no process
            if not cpu.has_process:
                self._quantum_counter = 0
                self._allocate_process(cpu, self._ready_processes[0])

        self._quantum_counter += 1

    @staticmethod
    def _sort_processes(process):
        # since we override _update_process_allocation() and we do not use this function there, there is no need to
        # properly implement this function
        pass
