import logging
from common import Process
from scheduler import FCFS_Scheduler, SJF_Scheduler, LLF_Scheduler, RR_Scheduler


logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

# scheduler = FCFS_Scheduler([Process(0, 22, 5), Process(0, 2, 5), Process(0, 3, 5), Process(0, 5, 5), Process(0, 8, 5)], 1)
# scheduler.start()
# logging.info(f'Average ready time of the FCFS-Scheduler was {scheduler.avg_ready_time()}.')

# scheduler = SJF_Scheduler([Process(0, 22, 5), Process(0, 2, 5), Process(0, 3, 5), Process(0, 5, 5), Process(0, 8, 5)], 1)
# scheduler.start()
# logging.info(f'Average ready time of the SJF-Scheduler was {scheduler.avg_ready_time()}.')

scheduler = LLF_Scheduler([Process(0, 8, 10), Process(0, 5, 9), Process(0, 4, 9)], 2)
scheduler.start()
logging.info(f'Average ready time of the LLF-Scheduler was {scheduler.avg_ready_time()}.')

scheduler = RR_Scheduler([Process(0, 22, 5), Process(0, 2, 5), Process(0, 3, 5), Process(0, 5, 5), Process(0, 8, 5)], 3)
scheduler.start()
logging.info(f'Average ready time of the RR-Scheduler was {scheduler.avg_ready_time()}.')