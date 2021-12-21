from logging import FATAL
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, RadioButtons
from scheduler import NP_EDF_Scheduler, NP_SJF_Scheduler, NP_FCFS_Scheduler
from common import Process
import time
from threading import Thread


class Visualizer:
    def __init__(self):
        self._n_cpus = 1
        self._graph_formats = ['bo', 'go', 'ro', 'co', 'mo', 'yo', 'ko', 'wo']
        self._fig, axd = plt.subplot_mosaic([['graph', 'graph', 'graph'], ['graph', 'graph', 'graph'], ['table', 'strategy', 'start_animated'],
                                            ['table', 'strategy',  'start']],
                                            figsize=(10, 5), constrained_layout=True)
        self._fig.canvas.mpl_connect('close_event', lambda _ : self._stop_current_thread())
        self._graph_ax = axd['graph']
        self._graph_data = []
        self._start_button = Button(axd['start'], 'Start')
        self._start_button.on_clicked(self._start_scheduler)
        self._start_animated_button = Button(axd['start_animated'], 'Start animated')
        self._start_animated_button.on_clicked(self._start_scheduler_animated)
        self._radioButtons = RadioButtons(axd['strategy'], ['a', 'b', 'c'])
        self._scheduler = None
        self._current_thread = None
        self._stop_thread = False
        plt.show()

    def _redraw_graph(self):
        dataLen = len(self._graph_data)
        for _ in range(dataLen):
            item = self._graph_data.pop(0)
            item.remove()
            del item
        self._graph_ax.set_ylim(- 0.5, self._n_cpus - 0.5)
        for p_idx, p in enumerate(self._scheduler.all_processes):
            time_values, cpu_values = [entry[0] for entry in p.history], [entry[1] for entry in p.history]
            new_data = self._graph_ax.plot(time_values, cpu_values, self._graph_formats[p_idx], label=f'Process {p_idx}')[0]
            self._graph_data.append(new_data)
        self._graph_ax.legend(loc='upper right')
        self._fig.canvas.draw_idle()

    def _stop_current_thread(self):
        if self._current_thread is not None and self._current_thread.is_alive():
            self._stop_thread = True
            while self._current_thread.is_alive():
                pass
            self._stop_thread = False

    def _init_scheduler(self):
        self._scheduler = NP_FCFS_Scheduler(processes=[Process(0, 3), Process(0, 2), Process(0, 3), Process(0, 5), Process(0, 8)], n_cpus=self._n_cpus)

    def _start_scheduler(self, _):
        self._stop_current_thread()
        self._init_scheduler()
        while self._scheduler.step():
            pass
        self._redraw_graph()

    def _start_scheduler_animated(self, _):
        def myanimation():
            while self._scheduler.step() and not self._stop_thread:
                self._redraw_graph()
                print("Haghga")
                time.sleep(0.5)
        self._stop_current_thread()
        self._init_scheduler()
        self._current_thread = Thread(target=myanimation)
        self._current_thread.start()
        

v = Visualizer()

