import logging
import copy
from common import Process
from scheduler import NP_FCFS_Scheduler, NP_SJF_Scheduler, NP_EDF_Scheduler, NP_LLF_Scheduler, P_SJF_Scheduler, P_EDF_Scheduler, P_RR_Scheduler


NO_DEADLINE_PROCESSES = [Process(0, 22), Process(0, 2), Process(0, 3), Process(0, 5), Process(0, 8)]
EDF_PROCESSES = [Process(0, 2, 4), Process(3, 3, 14), Process(6, 3, 12), Process(5, 4, 10)]

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

# nonpreemtive schedulers
scheduler = NP_FCFS_Scheduler(processes=copy.deepcopy(NO_DEADLINE_PROCESSES), n_cpus=1)
scheduler.start()
logging.info(f'Average ready time of the nonpreemptive FCFS-Scheduler was {scheduler.avg_time()}.')

scheduler = NP_SJF_Scheduler(processes=copy.deepcopy(NO_DEADLINE_PROCESSES), n_cpus=1)
scheduler.start()
logging.info(f'Average ready time of the nonpreemptive SJF-Scheduler was {scheduler.avg_time()}.')

scheduler = NP_EDF_Scheduler(processes=copy.deepcopy(EDF_PROCESSES), n_cpus=1)
scheduler.start()
logging.info(f'Average ready time of the nonpreemptive EDF-Scheduler was {scheduler.avg_time()}.')

scheduler = NP_LLF_Scheduler(processes=[Process(0, 8, 10), Process(0, 5, 9), Process(0, 4, 9)], n_cpus=2)
scheduler.start()
logging.info(f'Average ready time of the nonpreemptive LLF-Scheduler was {scheduler.avg_time()}.')


# preemptive schedulers
scheduler = P_SJF_Scheduler(processes=copy.deepcopy(NO_DEADLINE_PROCESSES))
scheduler.start()
logging.info(f'Average ready time of the preemptive SJF-Scheduler was {scheduler.avg_time()}.')

scheduler = P_EDF_Scheduler(processes=copy.deepcopy(EDF_PROCESSES))
scheduler.start()
logging.info(f'Average ready time of the preemptive EDF-Scheduler was {scheduler.avg_time()}.')

# scheduler = P_RR_Scheduler(processes=copy.deepcopy(NO_DEADLINE_PROCESSES), quantum=3)
# scheduler.start()
# logging.info(f'Average ready time of the preemptive RR-Scheduler was {scheduler.avg_time()}.')