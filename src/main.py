import logging
from process import Process
from scheduler import SJF_Scheduler, Scheduler


logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

p1 = Process(name='P1', ready_time=0, exec_time=22, deadline=100)
p2 = Process(name='P2', ready_time=0, exec_time=2, deadline=77)
p3 = Process(name='P3', ready_time=4, exec_time=3, deadline=12)
p4 = Process(name='P4', ready_time=4, exec_time=4, deadline=28)
p5 = Process(name='P5', ready_time=5, exec_time=5, deadline=28)

scheduler = SJF_Scheduler(processes=[p1, p2, p3, p4])