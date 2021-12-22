import logging
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, RadioButtons, TextBox
from scheduler import NP_FCFS_Scheduler, NP_SJF_Scheduler, NP_EDF_Scheduler, NP_LLF_Scheduler, P_SJF_Scheduler, P_EDF_Scheduler, P_RR_Scheduler
from common import Process
import time
import numpy as np
from threading import Thread


STRATEGIES = [
    'First Come First Serve (nonpreemptive)',
    'Shortest Job First (nonpreemptive)',
    'Earliest Deadline First (nonpreemptive)',
    'Least Laxity First (nonpreemptive)',
    'Shortest Job First (preemptive)',
    'Earliest Deadline First (preemptive)',
    'Round Robin (preemptive)'
    ]
    
PROCESS_FORMATS = ['bo', 'go', 'ro', 'co', 'mo', 'yo', 'ko', 'wo']

GRAPH_FORMAT = [
    ['graph', 'graph', 'graph', 'logger'],
    ['graph', 'graph', 'graph', 'logger'],
    ['table', 'strategy', 'strategy', 'start_animated'],
    ['table', 'strategy', 'strategy',  'start']]

MAX_CPUS = 3
MAX_TIME = 50


class Visualizer:
    def __init__(self):
        self._fig, axd = plt.subplot_mosaic(GRAPH_FORMAT)
        self._fig.canvas.manager.window.showMaximized()
        self._fig.canvas.mpl_connect('close_event', lambda _: setattr(self, '_stop_thread', 'True'))
        self._fig.canvas.manager.set_window_title('CPU & Process Simulation')

        self._graph_ax = axd['graph']
        self._graph_ax.set_ylabel('CPUs')
        self._graph_ax.set_xlabel('Time')
        self._graph_ax.xaxis.tick_top()
        self._graph_ax.xaxis.set_label_position('top') 
        self._graph_ax.set_xlim(- 0.5, MAX_TIME + 0.5)
        self._graph_ax.set_ylim(- 0.5, MAX_CPUS - 0.5)
        self._graph_ax.xaxis.set_ticks(np.arange(0, MAX_TIME + 0.5, 5))
        self._graph_ax.yaxis.set_ticks(np.arange(0, MAX_CPUS, 1))
        self._graph_ax.set_title('CPU ALLOCATION')
        self._graph_data = []

        self._log_ax = axd['logger']
        # self._graph_data.append(self._log_ax.text(0, 0, '', fontsize=10, verticalalignment='bottom'))
        self._log_ax.xaxis.set_ticks([])
        self._log_ax.yaxis.set_ticks([])
        self._log_ax.set_title('LOGGER')
        self._text_box = TextBox(self._log_ax, '')
        self._text_box.set_val('') 

        self._start_button = Button(axd['start'], 'Start')
        self._start_button.on_clicked(self._start_scheduler)

        self._start_animated_button = Button(axd['start_animated'], 'Start animated')
        self._start_animated_button.on_clicked(self._start_scheduler_animated)

        self._strategy_selection = RadioButtons(axd['strategy'], STRATEGIES)

        self._scheduler = None

        self._current_thread = Thread(target=lambda: logging.debug('Thread initialized'))
        self._current_thread.start()
        self._stop_thread = False

        plt.show()

    def _redraw_graph(self):
        for _ in range(len(self._graph_data)):
            item = self._graph_data.pop(0)
            item.remove()
            del item

        for p_idx, p in enumerate(self._scheduler.all_processes):
            time_values, cpu_values = [entry[0] for entry in p.history], [entry[1] for entry in p.history]
            new_data = self._graph_ax.plot(time_values, cpu_values, PROCESS_FORMATS[p_idx], label=f'Process {p_idx}')[0]
            self._graph_data.append(new_data)

        # self._graph_data.append(self._log_ax.text(0, 0, self._scheduler.logger, fontsize=8, verticalalignment='bottom'))
        self._text_box.set_val(self._scheduler.logger)
        self._graph_ax.legend(loc='upper right')
        self._fig.canvas.draw_idle()

    def _init_scheduler(self):
        ps = [Process(0, 3), Process(0, 2), Process(0, 3), Process(0, 5), Process(0, 8)]
        n_cpus = 2
        quantum = 3
        match STRATEGIES.index(self._strategy_selection.value_selected):
            case 0:
                self._scheduler = NP_FCFS_Scheduler(ps, n_cpus)
            case 1:
                self._scheduler = NP_SJF_Scheduler(ps, n_cpus)
            case 2:
                self._scheduler = NP_EDF_Scheduler(ps, n_cpus)
            case 3:
                self._scheduler = NP_LLF_Scheduler(ps, n_cpus)
            case 4:
                self._scheduler = P_SJF_Scheduler(ps)
            case 5:
                self._scheduler = P_EDF_Scheduler(ps)
            case 6:
                self._scheduler = P_RR_Scheduler(ps, quantum)

    def _start_scheduler(self, _):
        if self._current_thread.is_alive():
            return

        self._init_scheduler()
        while self._scheduler.step():
            pass
        self._redraw_graph()

    def _start_scheduler_animated(self, _):
        def myanimation():
            while self._scheduler.step() and not self._stop_thread:
                self._redraw_graph()
                time.sleep(0.5)
            self._redraw_graph()

        if self._current_thread.is_alive():
            return

        self._init_scheduler()
        self._current_thread = Thread(target=myanimation)
        self._current_thread.start()
        

v = Visualizer()

