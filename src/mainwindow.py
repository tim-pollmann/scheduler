from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
from common import Process
from scheduler import NP_FCFS_Scheduler, NP_SJF_Scheduler, NP_EDF_Scheduler, NP_LLF_Scheduler, P_SJF_Scheduler, P_EDF_Scheduler, P_RR_Scheduler
import time
from threading import Thread


MAX_CPUS = 3
MAX_TIME = 50
STRATEGIES = [
    'First Come First Serve (nonpreemptive)',
    'Shortest Job First (nonpreemptive)',
    'Earliest Deadline First (nonpreemptive)',
    'Least Laxity First (nonpreemptive)',
    'Shortest Job First (preemptive)',
    'Earliest Deadline First (preemptive)',
    'Round Robin (preemptive)'
    ]

LINE_THICKNESS = 15
PROCESS_VISUALIZATION = [
    pg.mkPen(color=(255, 0, 0), width=LINE_THICKNESS),
    pg.mkPen(color=(255, 255, 0), width=LINE_THICKNESS),
    pg.mkPen(color=(0, 0, 0), width=LINE_THICKNESS),
    pg.mkPen(color=(0, 255, 0), width=LINE_THICKNESS),
    pg.mkPen(color=(0, 0, 255), width=LINE_THICKNESS),
    pg.mkPen(color=(0, 255, 255), width=LINE_THICKNESS),
    pg.mkPen(color=(255, 0, 0), width=LINE_THICKNESS)
]


class MainWindow(QMainWindow):
    def __init__(self):
        # window
        super().__init__()
        self.setWindowTitle('Scheduler & Process Simulator')

        # graph
        graph_heading = QLabel('Graph')
        self._graph = pg.PlotWidget()
        self._graph.setXRange(0, MAX_TIME)
        self._graph.setYRange(0.5, MAX_CPUS + 0.5)
        self._graph.setBackground('w')
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(graph_heading, 0, Qt.AlignmentFlag.AlignTop)
        graph_layout.addWidget(self._graph)
        
        # logger
        logger_heading = QLabel('Logger')
        self._logger = QLabel('')
        self._logger.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        logger_layout = QVBoxLayout()
        logger_layout.addWidget(logger_heading, 0, Qt.AlignmentFlag.AlignTop)
        logger_layout.addWidget(self._logger)

        # options 
        options_heading = QLabel('Options')
        self._strategies_selection = QComboBox()
        self._strategies_selection.addItems(STRATEGIES)
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        run_button = QPushButton('Run')
        run_button.clicked.connect(self._run_button_clicked)
        button_layout = QHBoxLayout()
        button_layout.addWidget(close_button)
        button_layout.addWidget(run_button)
        options_layout = QVBoxLayout()
        options_layout.addWidget(options_heading, 0, Qt.AlignmentFlag.AlignTop)
        options_layout.addWidget(self._strategies_selection)
        options_layout.addLayout(button_layout)

        lower_layout = QHBoxLayout()
        lower_layout.addLayout(logger_layout)
        lower_layout.addLayout(options_layout)

        central_layout = QVBoxLayout()
        central_layout.addWidget(graph_heading)
        central_layout.addWidget(self._graph, 30)
        central_layout.addLayout(lower_layout, 70)
        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
        self.showMaximized()

        self._scheduler = None


    def _run_button_clicked(self):
        # check if animated
        self._start_scheduler()


    def _init_scheduler(self):
        ps = [Process(1, 0, 22), Process(2, 0, 2), Process(3, 0, 3), Process(4, 0, 5), Process(5, 0, 8)]
        n_cpus = 1
        quantum = 3
        match self._strategies_selection.currentIndex():
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

    def _start_scheduler(self):
        def _animate_scheduler():
            while self._scheduler.step():# and not self._stop_thread:
                self._update_logger()
                self._update_graph()
                #time.sleep(0.5)
            self._update_logger()

        # if self._current_thread.is_alive():
        #     return

        # self._init_scheduler()
        # self._current_thread = Thread(target=_animate_scheduler)
        # self._current_thread.start()
        # while self._scheduler.step():# and not self._stop_thread:
        #         self._update_logger()
        #         self._update_graph()
        #         time.sleep(0.5)
           
        # self._update_logger()

        self._init_scheduler()
        while self._scheduler.step():
            pass
        self._update_logger()
        self._update_graph()


    def _update_logger(self):
        self._logger.setText(self._scheduler.logger)

    
    def _update_graph(self):
        self._graph.clear()
        for cpu in self._scheduler.cpus:
            timestamps, pids = [entry[0] for entry in cpu.history], [entry[1] for entry in cpu.history]
            for idx, timestamp in enumerate(timestamps):
                self._graph.plot([timestamp, timestamp + 1], [cpu.id, cpu.id], pen=PROCESS_VISUALIZATION[pids[idx] - 1])
        self._graph.setXRange(0, MAX_TIME)
        self._graph.setYRange(0.5, MAX_CPUS + 0.5)

            
            


def main():
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()