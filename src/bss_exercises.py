import itertools
from process import Process
from scheduler import NpSjfScheduler, PSjfScheduler, PRrScheduler


# for exercise 2 and exercise 3
EXEC_TIMES = [22, 2, 3, 5, 8]
# only for exercise 3
READY_TIMES = [0, 0, 4, 4, 4]


# permute the order of the process (== permute order of exec-times, since they are all 0) for "Round Robin"-Scheduler
def exercise_2(quantum=3):
    permutations = itertools.permutations(EXEC_TIMES)
    perm_to_time = {}

    for permutation in permutations:
        processes = [Process(idx + 1, 0, exec_time, 0) for idx, exec_time in enumerate(permutation)]
        scheduler = PRrScheduler(processes, quantum)

        while scheduler.step():
            pass

        perm_to_time[permutation] = scheduler.avg_delta_time

    print()
    print(f'Scheduler: Preemptive "Round Robin", Quantum: {quantum}')
    for permutation, avg_delta_time in sorted(perm_to_time.items(), key=lambda item: item[1]):
        print(f'Permutation: {permutation}, Average delta time: {avg_delta_time}')


# permute order of ready times for nonpreemptive and preemptive  "Shortest Job First"-Scheduler
def exercise_3():
    def permute(scheduler_type, scheduler_name):
        permutations = itertools.permutations(READY_TIMES)
        perm_to_time = {}

        for permutation in permutations:
            processes = [Process(idx + 1, ready_time, exec_time, 0)
                         for idx, (ready_time, exec_time)
                         in enumerate(zip(permutation, EXEC_TIMES))]

            scheduler = scheduler_type(1, processes)

            while scheduler.step():
                pass

            perm_to_time[permutation] = scheduler.avg_delta_time

        print()
        print(f'Scheduler: {scheduler_name}')
        for permutation, avg_delta_time in sorted(perm_to_time.items(), key=lambda item: item[1]):
            print(f'Permutation: {permutation}, Average delta time: {avg_delta_time}')

    permute(NpSjfScheduler, 'Nonpreemptive "Shortest Job First"')
    permute(PSjfScheduler, 'Preemptive "Shortest Job First"')
