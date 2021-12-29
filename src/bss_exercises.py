import itertools
from process import Process
from scheduler import (NpFcfsScheduler, NpSjfScheduler, NpEdfScheduler, NpLlfScheduler, PSjfScheduler, PEdfScheduler,
                       PLlfScheduler, PRrScheduler)

BSS_EXAMPLES = [
    # example 1 for FCFS, SJF, RR
    (0, 22, 0),
    (0, 2, 0),
    (0, 3, 0),
    (0, 5, 0),
    (0, 8, 0),
    # example 2 for FCFS, SJF, RR
    (0, 22, 0),
    (0, 2, 0),
    (4, 3, 0),
    (4, 5, 0),
    (4, 8, 0),
    # example 1 for EDF, LLF
    (0, 4, 9),
    (0, 5, 9),
    (0, 8, 10),
    # example 2 for EDF, LLF
    (0, 4, 5),
    (0, 1, 7),
    (0, 2, 7),
    (0, 5, 13)
]


def exercise_1(print_logger=False):
    def run_scheduler(scheduler_type, scheduler_name, process_configs):
        scheduler = scheduler_type(1, [Process(idx + 1, ready_time, exec_time, deadline)
                                       for idx, (ready_time, exec_time, deadline)
                                       in enumerate(process_configs)])
        while scheduler.step():
            pass

        print(f'Scheduler: {scheduler_name}')
        print(f'Process configurations: {process_configs}')
        if print_logger:
            print(scheduler.logger)
        else:
            print(f'Average delta time was {scheduler.avg_delta_time}')

    def run_rr_scheduler(process_configs):
        for quantum in range(5):
            scheduler = PRrScheduler([Process(idx + 1, ready_time, exec_time, deadline)
                                      for idx, (ready_time, exec_time, deadline)
                                      in enumerate(process_configs)], quantum)
            while scheduler.step():
                pass

            print(f'Scheduler: Round Robin (preemptive), Quantum: {quantum}')
            print(f'Process configurations: {process_configs}')
            if print_logger:
                print(scheduler.logger)
            else:
                print(f'Average delta time was {scheduler.avg_delta_time}')

    run_scheduler(NpFcfsScheduler, 'First Come First Serve (nonpreemptive)', BSS_EXAMPLES[0:5])
    run_scheduler(NpFcfsScheduler, 'First Come First Serve (nonpreemptive)', BSS_EXAMPLES[5:10])
    run_scheduler(NpSjfScheduler, 'Shortest Job First (nonpreemptive)', BSS_EXAMPLES[0:5])
    run_scheduler(NpSjfScheduler, 'Shortest Job First (nonpreemptive)', BSS_EXAMPLES[5:10])
    run_scheduler(PSjfScheduler, 'Shortest Job First (preemptive)', BSS_EXAMPLES[0:5])
    run_scheduler(PSjfScheduler, 'Shortest Job First (preemptive)', BSS_EXAMPLES[5:10])
    run_scheduler(NpEdfScheduler, 'Earliest Deadline First (nonpreemptive)', BSS_EXAMPLES[10:13])
    run_scheduler(NpEdfScheduler, 'Earliest Deadline First (nonpreemptive)', BSS_EXAMPLES[13:17])
    run_scheduler(PEdfScheduler, 'Earliest Deadline First (preemptive)', BSS_EXAMPLES[10:13])
    run_scheduler(PEdfScheduler, 'Earliest Deadline First (preemptive)', BSS_EXAMPLES[13:17])
    run_scheduler(NpLlfScheduler, 'Least Laxity First (nonpreemptive)', BSS_EXAMPLES[10:13])
    run_scheduler(NpLlfScheduler, 'Least Laxity First (nonpreemptive)', BSS_EXAMPLES[13:17])
    run_scheduler(PLlfScheduler, 'Least Laxity First (preemptive)', BSS_EXAMPLES[10:13])
    run_scheduler(PLlfScheduler, 'Least Laxity First (preemptive)', BSS_EXAMPLES[13:17])
    run_rr_scheduler(BSS_EXAMPLES[0:5])
    run_rr_scheduler(BSS_EXAMPLES[5:10])


# permute the order of processes (== permute order of exec-times, since other values are all 0)
def exercise_2(quantum):
    perm_to_time = {}

    for exec_time_permutation in itertools.permutations([process_config[1] for process_config in BSS_EXAMPLES[0:5]]):
        scheduler = PRrScheduler([Process(idx + 1, 0, exec_time, 0) for idx, exec_time
                                  in enumerate(exec_time_permutation)], quantum)

        while scheduler.step():
            pass

        perm_to_time[exec_time_permutation] = scheduler.avg_delta_time

    print(f'Scheduler: Round Robin (preemptive), Quantum: {quantum}')
    for ready_time_permutation, avg_delta_time in sorted(perm_to_time.items(), key=lambda item: item[1]):
        print(f'Ready time permutation: {ready_time_permutation}, Average delta time: {avg_delta_time}')
    print()


# permute order of ready times for nonpreemptive and preemptive  "Shortest Job First"-Scheduler
def exercise_3():
    def permute(scheduler_type, scheduler_name):
        process_configs = BSS_EXAMPLES[5:10]
        ready_time_permutations = itertools.permutations([process_config[0] for process_config in process_configs])
        perm_to_time = {}

        for ready_time_permutation in ready_time_permutations:
            scheduler = scheduler_type(1, [Process(idx + 1, ready_time, exec_time, deadline)
                                           for idx, (ready_time, (_, exec_time, deadline))
                                           in enumerate(zip(ready_time_permutation, process_configs))])

            while scheduler.step():
                pass

            perm_to_time[ready_time_permutation] = scheduler.avg_delta_time

        print(f'Scheduler: {scheduler_name}')
        for ready_time_permutation, avg_delta_time in sorted(perm_to_time.items(), key=lambda item: item[1]):
            print(f'Ready time permutation: {ready_time_permutation}, Average delta time: {avg_delta_time}')
        print()

    permute(NpSjfScheduler, 'Shortest Job First (nonpreemptive)')
    permute(PSjfScheduler, 'Shortest Job First (preemptive)')
