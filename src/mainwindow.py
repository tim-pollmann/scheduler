import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QGridLayout, QFormLayout, QSpinBox, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QCheckBox)

from cpu import CPU
from process import Process
from scheduler import (NpFcfsScheduler, NpSjfScheduler, NpEdfScheduler, NpLlfScheduler, PSjfScheduler,
                       PEdfScheduler, PRrScheduler)

MAX_CPUS = 4
MAX_TIME = 100
LINE_WIDTH = 0.2
PROCESS_COLORS = ['red', 'blue', 'green', 'yellow', 'magenta', 'grey', 'cyan', 'chocolate', 'blueviolet', 'brown',
                  'darkred', 'salmon', 'gold', 'khaki', 'hotpink', 'limegreen', 'lightblue', 'navy', 'olive', 'orange']
STRATEGIES = ['First Come First Serve (nonpreemptive)', 'Shortest Job First (nonpreemptive)',
              'Earliest Deadline First (nonpreemptive)', 'Least Laxity First (nonpreemptive)',
              'Shortest Job First (preemptive)', 'Earliest Deadline First (preemptive)', 'Round Robin (preemptive)']


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._ui = {}
        self._init_mpl()
        self._init_qt()

        self._scheduler = None
        self._graph_data = []

    def _init_sim_button_clicked(self):
        cpus = [CPU(idx + 1) for idx in range(self._ui['n_cpus_selection'].value())]

        processes = [Process(idx + 1, ready_time_box.value(), exec_time_box.value(), deadline_box.value())
                     for idx, (checkbox, ready_time_box, exec_time_box, deadline_box)
                     in enumerate(self._ui['process_selection'])
                     if checkbox.isChecked()]

        match self._ui['strategy_selection'].currentIndex():
            case 0:
                self._scheduler = NpFcfsScheduler(cpus, processes)
            case 1:
                self._scheduler = NpSjfScheduler(cpus, processes)
            case 2:
                self._scheduler = NpEdfScheduler(cpus, processes)
            case 3:
                self._scheduler = NpLlfScheduler(cpus, processes)
            case 4:
                self._scheduler = PSjfScheduler(cpus, processes)
            case 5:
                self._scheduler = PEdfScheduler(cpus, processes)
            case 6:
                quantum = 3
                self._scheduler = PRrScheduler(cpus, processes, quantum)

        self._ui['init_sim_button'].setEnabled(False)
        self._ui['next_step_button'].setEnabled(True)
        self._ui['run_sim_button'].setEnabled(True)
        self._ui['reset_sim_button'].setEnabled(True)

    def _next_step_button_clicked(self):
        if not self._scheduler.step():
            self._ui['next_step_button'].setEnabled(False)
            self._ui['run_sim_button'].setEnabled(False)

        self._update_graph()
        self._update_logger()

    def _run_sim_button_clicked(self):
        while self._scheduler.step():
            pass

        self._ui['next_step_button'].setEnabled(False)
        self._ui['run_sim_button'].setEnabled(False)

        self._update_graph()
        self._update_logger()

    def _reset_sim_button_clicked(self):
        self._ui['init_sim_button'].setEnabled(True)
        self._ui['next_step_button'].setEnabled(False)
        self._ui['run_sim_button'].setEnabled(False)
        self._ui['reset_sim_button'].setEnabled(False)

        self._scheduler = None

        self._update_graph()
        self._update_logger()

    def _update_logger(self):
        if self._scheduler is not None:
            self._ui['logger'].setText(self._scheduler.logger)
        else:
            self._ui['logger'].setText('')

    def _update_graph(self):
        for item in self._graph_data:
            item.remove()

        self._graph_data = []

        if self._scheduler is not None:
            for timestamp, cid, pid in self._scheduler.allocation_history:
                self._graph_data.append(
                    self._ui['graph_axes'].add_patch(Rectangle((timestamp, cid - LINE_WIDTH / 2), 1, LINE_WIDTH,
                                                               facecolor=PROCESS_COLORS[pid - 1])))

        self._ui['graph_canvas'].draw_idle()

    def _init_mpl(self):
        fig = Figure()
        self._ui['graph_axes'] = fig.add_subplot(111)
        self._ui['graph_axes'].set_ylabel('CPUs')
        self._ui['graph_axes'].set_xlabel('Time')
        self._ui['graph_axes'].xaxis.tick_top()
        self._ui['graph_axes'].xaxis.set_label_position('top')
        self._ui['graph_axes'].set_xlim(0, MAX_TIME)
        self._ui['graph_axes'].set_ylim(0.5, MAX_CPUS + 0.5)
        self._ui['graph_axes'].set_xticks(np.arange(0, MAX_TIME + 1, 5))
        self._ui['graph_axes'].set_xticks(np.arange(0, MAX_TIME + 1, 1), minor=True)
        self._ui['graph_axes'].set_yticks(np.arange(1, MAX_CPUS + 1, 1))
        self._ui['graph_axes'].grid(axis='x', which='major', alpha=0.7)
        self._ui['graph_axes'].grid(axis='x', which='minor', alpha=0.35)
        self._ui['graph_canvas'] = FigureCanvasQTAgg(fig)

    def _init_qt(self):
        def create_spinbox(min_value, max_value):
            spinbox = QSpinBox()
            spinbox.setRange(min_value, max_value)
            return spinbox

        self._ui['logger'] = QLabel('')
        self._ui['logger'].setAlignment(Qt.AlignmentFlag.AlignBottom)

        self._ui['strategy_selection'] = QComboBox()
        self._ui['strategy_selection'].addItems(STRATEGIES)

        self._ui['n_cpus_selection'] = create_spinbox(1, MAX_CPUS)

        form_layout = QFormLayout()
        form_layout.addRow(QLabel('Scheduler-Strategy'), self._ui['strategy_selection'])
        form_layout.addRow(QLabel('Number of CPUs'), self._ui['n_cpus_selection'])

        self._ui['init_sim_button'] = QPushButton('Initialize Simulation')
        self._ui['init_sim_button'].clicked.connect(self._init_sim_button_clicked)
        self._ui['next_step_button'] = QPushButton('Do Next Simulation Step')
        self._ui['next_step_button'].clicked.connect(self._next_step_button_clicked)
        self._ui['next_step_button'].setEnabled(False)
        self._ui['run_sim_button'] = QPushButton('Run Complete Simulation')
        self._ui['run_sim_button'].clicked.connect(self._run_sim_button_clicked)
        self._ui['run_sim_button'].setEnabled(False)
        self._ui['reset_sim_button'] = QPushButton('Reset Simulation')
        self._ui['reset_sim_button'].clicked.connect(self._reset_sim_button_clicked)
        self._ui['reset_sim_button'].setEnabled(False)

        process_layout = QGridLayout()
        process_layout.addWidget(QLabel('PID'), 0, 1)
        process_layout.addWidget(QLabel('Ready Time'), 0, 2)
        process_layout.addWidget(QLabel('Execution Time'), 0, 3)
        process_layout.addWidget(QLabel('Deadline'), 0, 4)

        self._ui['process_selection'] = []

        for row in range(len(PROCESS_COLORS)):
            checkbox = QCheckBox()
            process_layout.addWidget(checkbox, row + 1, 0, Qt.AlignmentFlag.AlignRight)

            label = QLabel(str(row + 1))
            color = PROCESS_COLORS[row]
            label.setStyleSheet("QLabel { background-color : " + color + "; }")
            process_layout.addWidget(label, row + 1, 1)

            ready_time_spinbox = create_spinbox(0, 49)
            process_layout.addWidget(ready_time_spinbox, row + 1, 2)

            exec_time_spinbox = create_spinbox(1, 49)
            process_layout.addWidget(exec_time_spinbox, row + 1, 3)

            deadline_spinbox = create_spinbox(1, 49)
            process_layout.addWidget(deadline_spinbox, row + 1, 4)

            self._ui['process_selection'].append((checkbox, ready_time_spinbox, exec_time_spinbox, deadline_spinbox))

        control_layout = QVBoxLayout()
        control_layout.addLayout(form_layout)
        control_layout.addWidget(self._ui['init_sim_button'])
        control_layout.addWidget(self._ui['next_step_button'])
        control_layout.addWidget(self._ui['run_sim_button'])
        control_layout.addWidget(self._ui['reset_sim_button'])

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self._ui['logger'])
        lower_layout.addLayout(process_layout)
        lower_layout.addLayout(control_layout)

        central_layout = QVBoxLayout()
        central_layout.addWidget(self._ui['graph_canvas'])
        central_layout.addLayout(lower_layout)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        self.setWindowTitle('Scheduler & Process Simulator')
        self.setCentralWidget(central_widget)
        self.showMaximized()
