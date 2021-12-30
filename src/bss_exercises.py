import itertools
import copy
from process import Process
from scheduler import (NpFcfsScheduler, NpSjfScheduler, NpEdfScheduler, NpLlfScheduler, PSjfScheduler, PEdfScheduler,
                       PRrScheduler)
from globals import SCHEDULERS, BSS_EXAMPLES


def exercise_1(quantum, print_logger):
    # helper function to run the scheduling simulation
    def run_simulation(scheduler_type, scheduler_name, n_cpus, process_configs):
        # init scheduler
        if scheduler_type == PRrScheduler:
            scheduler = PRrScheduler([Process(idx + 1, ready_time, exec_time, deadline)
                                      for idx, (ready_time, exec_time, deadline)
                                      in enumerate(process_configs)], quantum)
        else:
            scheduler = scheduler_type(n_cpus, [Process(idx + 1, ready_time, exec_time, deadline)
                                                for idx, (ready_time, exec_time, deadline)
                                                in enumerate(process_configs)])

        # run simulation until its finished
        scheduler.run_until_finished()

        # print the result
        print(f'Scheduler: {scheduler_name} with {n_cpus} {"CPU" if n_cpus == 1 else "CPUs"}')
        print(f'Process configurations: {process_configs}')
        if print_logger:
            print(scheduler.logger)
        else:
            print(f'Average delta time was {scheduler.avg_delta_time}\n')

    # examples are executed in the same order as they occur in the bss script
    run_simulation(NpFcfsScheduler, SCHEDULERS[0], 1, BSS_EXAMPLES[0:5])
    run_simulation(NpSjfScheduler, SCHEDULERS[1], 1, BSS_EXAMPLES[0:5])
    run_simulation(NpEdfScheduler, SCHEDULERS[2], 2, BSS_EXAMPLES[10:13])
    run_simulation(NpLlfScheduler, SCHEDULERS[3], 2, BSS_EXAMPLES[10:13])
    run_simulation(PRrScheduler, f'{SCHEDULERS[7]}, Quantum: {quantum},', 1, BSS_EXAMPLES[0:5])
    run_simulation(PSjfScheduler, SCHEDULERS[4], 1, BSS_EXAMPLES[5:10])
    run_simulation(NpSjfScheduler, SCHEDULERS[1], 1, BSS_EXAMPLES[5:10])
    run_simulation(PEdfScheduler, SCHEDULERS[5], 1, BSS_EXAMPLES[13:17])


# a simple helper function to print the results of exercise 2 and 3
def print_permutations(scheduler_name, perm_to_time, sort_by_avg_delta_time):
    print(f'Scheduler: {scheduler_name}')

    if sort_by_avg_delta_time:
        perm_to_time = sorted(perm_to_time.items(), key=lambda item: item[1])
    else:
        perm_to_time = list(perm_to_time.items())

    for permutation, avg_delta_time in perm_to_time:
        print(f'Permutation: {permutation}, Average delta time: {avg_delta_time}')
    print()


# in exercise 2 and 3 the results are stored in a dict "perm_to_time" to allow them to be sorted by average delta time
def exercise_2(quantum, sort_by_avg_delta_time):
    perm_to_time = {}

    # permute the order of the processes
    for permutation in itertools.permutations([Process(idx + 1, ready_time, exec_time, deadline)
                                               for idx, (ready_time, exec_time, deadline)
                                               in enumerate(BSS_EXAMPLES[5:10])]):

        # init scheduler
        scheduler = PRrScheduler(copy.deepcopy(permutation), quantum)

        # run simulation until its finished
        scheduler.run_until_finished()

        # store results in dict
        perm_to_time[tuple([(process.ready_time, process.exec_time, process.deadline)
                            for process in permutation])] = scheduler.avg_delta_time

    print_permutations(f'Round Robin (preemptive), Quantum: {quantum}', perm_to_time, sort_by_avg_delta_time)


def exercise_3(sort_by_avg_delta_time):
    def permute(scheduler_type, scheduler_name):
        perm_to_time = {}

        # permute the ready times of the processes
        for permutation in itertools.permutations([process_config[0] for process_config in BSS_EXAMPLES[5:10]]):
            # init scheduler
            scheduler = scheduler_type(1, [Process(idx + 1, ready_time, exec_time, deadline)
                                           for idx, (ready_time, (_, exec_time, deadline))
                                           in enumerate(zip(permutation, BSS_EXAMPLES[5:10]))])

            # run simulation until its finished
            scheduler.run_until_finished()
            perm_to_time[permutation] = scheduler.avg_delta_time

        # store results in dict
        print_permutations(scheduler_name, perm_to_time, sort_by_avg_delta_time)

    permute(NpSjfScheduler, 'Shortest Job First (nonpreemptive)')
    permute(PSjfScheduler, 'Shortest Job First (preemptive)')
