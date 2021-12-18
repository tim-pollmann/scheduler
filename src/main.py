import logging
from process import Process
from scheduler import FCFS_Scheduler, SJF_Scheduler, LLF_Scheduler


logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

p1 = Process(name='P1', ready_time=0, exec_time=22)
p2 = Process(name='P2', ready_time=0, exec_time=2)
p3 = Process(name='P3', ready_time=0, exec_time=3)
p4 = Process(name='P4', ready_time=0, exec_time=5)
p5 = Process(name='P5', ready_time=0, exec_time=8)

scheduler = FCFS_Scheduler(processes=[p1, p2, p3, p4, p5])
scheduler.start()
logging.info(f'Average ready time of the FCFS-Scheduler was {scheduler.avg_ready_time()}.')

scheduler = SJF_Scheduler(processes=[p1, p2, p3, p4, p5])
scheduler.start()
logging.info(f'Average ready time of the SJF-Scheduler was {scheduler.avg_ready_time()}.')

p1 = Process(name='P1', ready_time=0, exec_time=8, deadline=10)
p2 = Process(name='P2', ready_time=0, exec_time=5, deadline=9)
p3 = Process(name='P3', ready_time=0, exec_time=4, deadline=9)

scheduler = LLF_Scheduler(processes=[p1, p2, p3])
scheduler.start()
logging.info(f'Average ready time of the LLF-Scheduler was {scheduler.avg_ready_time()}.')