SCHEDULERS = [
    'First Come First Serve (nonpreemptive)',
    'Shortest Job First (nonpreemptive)',
    'Earliest Deadline First (nonpreemptive)',
    'Least Laxity First (nonpreemptive)',
    'Shortest Job First (preemptive)',
    'Earliest Deadline First (preemptive)',
    'Least Laxity First (preemptive)',
    'Round Robin (preemptive)'
]

BSS_EXAMPLES = [
    # example for FCFS, SJF, RR
    (0, 22, 0),
    (0, 2, 0),
    (0, 3, 0),
    (0, 5, 0),
    (0, 8, 0),
    # example for SJF
    (0, 22, 0),
    (0, 2, 0),
    (4, 3, 0),
    (4, 5, 0),
    (4, 8, 0),
    # example for EDF, LLF
    (0, 4, 9),
    (0, 5, 9),
    (0, 8, 10),
    # example 2 for EDF
    (0, 2, 4),
    (3, 3, 14),
    (6, 3, 12),
    (5, 4, 10)
]
