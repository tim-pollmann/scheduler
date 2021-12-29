import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QGridLayout, QFormLayout, QSpinBox, QWidget, QVBoxLayout, QLayout, QLabel,
                             QComboBox, QPushButton, QCheckBox, QSizePolicy)
from process import Process
from scheduler import (NpFcfsScheduler, NpSjfScheduler, NpEdfScheduler, NpLlfScheduler, PSjfScheduler, PEdfScheduler,
                       PRrScheduler)

MAX_CPUS = 4
MAX_SIM_TIME = 100
MAX_QUANTUM = 10
LINE_WIDTH = 0.2
PROCESS_COLORS = [
    'red', 'blue', 'green', 'yellow', 'magenta', 'grey', 'cyan', 'chocolate', 'blueviolet', 'brown', 'darkred',
    'salmon', 'gold', 'khaki', 'hotpink', 'limegreen', 'lightblue', 'navy', 'olive', 'orange', 'lightgray', 'darkgreen'
]

STRATEGIES = [
    'First Come First Serve (nonpreemptive)', 'Shortest Job First (nonpreemptive)',
    'Earliest Deadline First (nonpreemptive)', 'Least Laxity First (nonpreemptive)', 'Shortest Job First (preemptive)',
    'Earliest Deadline First (preemptive)', 'Round Robin (preemptive)'
]

DEFAULT_VALUES = [
    # example 1 for FCFS, SJF, RR
    (0, 22, 0), (0, 2, 0), (0, 3, 0), (0, 5, 0), (0, 8, 0),
    # example 2 for FCFS, SJF, RR
    (0, 22, 0), (0, 2, 0), (4, 3, 0), (4, 5, 0), (4, 8, 0),
    # example 3 for FCFS, SJF, RR
    (0, 15, 0), (0, 7, 0), (0, 1, 0), (0, 4, 0), (0, 8, 0),
    # example 1 for EDF, LLF
    (0, 4, 9), (0, 5, 9), (0, 8, 10),
    # example 2 for EDF, LLF
    (0, 4, 5), (0, 1, 7), (0, 2, 7), (0, 5, 13),
]


class MainWindow(QMainWindow):
    def __init__(self, set_default_values_for_exercise_1=False):
        super().__init__()
        self._ui = {}
        self._init_mpl()
        self._init_qt(set_default_values_for_exercise_1)

        self._scheduler = None
        self._graph_data = []

    def _init_sim_button_clicked(self):
        n_cpus = (self._ui['n_cpus_selection'].value())

        processes = [Process(idx + 1, ready_time_box.value(), exec_time_box.value(), deadline_box.value())
                     for idx, (checkbox, ready_time_box, exec_time_box, deadline_box)
                     in enumerate(self._ui['process_selection'])
                     if checkbox.isChecked()]

        if processes:
            match self._ui['strategy_selection'].currentIndex():
                case 0:
                    self._scheduler = NpFcfsScheduler(n_cpus, processes)
                case 1:
                    self._scheduler = NpSjfScheduler(n_cpus, processes)
                case 2:
                    self._scheduler = NpEdfScheduler(n_cpus, processes)
                case 3:
                    self._scheduler = NpLlfScheduler(n_cpus, processes)
                case 4:
                    self._scheduler = PSjfScheduler(n_cpus, processes)
                case 5:
                    self._scheduler = PEdfScheduler(n_cpus, processes)
                case 6:
                    self._scheduler = PRrScheduler(processes, self._ui['quantum_selection'].value())

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
            self._update_graph()

        self._update_logger()

        self._ui['next_step_button'].setEnabled(False)
        self._ui['run_sim_button'].setEnabled(False)

    def _reset_sim_button_clicked(self):
        self._ui['init_sim_button'].setEnabled(True)
        self._ui['next_step_button'].setEnabled(False)
        self._ui['run_sim_button'].setEnabled(False)
        self._ui['reset_sim_button'].setEnabled(False)

        self._scheduler = None

        self._update_graph()
        self._update_logger()

    def _update_logger(self):
        print( self._ui['logger'].size())
        if self._scheduler is not None:
            self._ui['logger'].setText(self._scheduler.logger)
        else:
            self._ui['logger'].setText('')

    def _update_graph(self):
        if self._scheduler is not None:
            for timestamp, cid, pid in self._scheduler.last_allocation:
                self._graph_data.append(
                    self._ui['graph_axes'].add_patch(Rectangle((timestamp, cid - LINE_WIDTH / 2), 1, LINE_WIDTH,
                                                               facecolor=PROCESS_COLORS[pid - 1])))
        else:
            for item in self._graph_data:
                item.remove()

            self._graph_data = []

        self._ui['graph_canvas'].draw_idle()

    # init the matplotlib-graph
    def _init_mpl(self):
        fig = Figure(facecolor='lightgray')
        self._ui['graph_canvas'] = FigureCanvasQTAgg(fig)
        self._ui['graph_axes'] = fig.add_subplot()

        self._ui['graph_axes'].xaxis.set_label_position('top')
        self._ui['graph_axes'].set_xlabel('Time', fontsize=16)
        self._ui['graph_axes'].set_ylabel('CPUs', fontsize=16)

        self._ui['graph_axes'].set_xlim(0, MAX_SIM_TIME)
        self._ui['graph_axes'].set_ylim(0.5, MAX_CPUS + 0.5)

        self._ui['graph_axes'].xaxis.tick_top()
        self._ui['graph_axes'].set_xticks(np.arange(0, MAX_SIM_TIME + 1, 5))
        self._ui['graph_axes'].set_xticks(np.arange(0, MAX_SIM_TIME + 1, 1), minor=True)
        self._ui['graph_axes'].set_yticks(np.arange(1, MAX_CPUS + 1, 1))
        self._ui['graph_axes'].tick_params(labelsize=14)

        self._ui['graph_axes'].grid(axis='x', which='major', alpha=0.7)
        self._ui['graph_axes'].grid(axis='x', which='minor', alpha=0.35)

    # init the qt-ui
    # not the most elegant solution but it does its job :)
    def _init_qt(self, set_default_values_for_exercise_1):
        def create_spinbox(min_value, max_value):
            spinbox = QSpinBox()
            spinbox.setRange(min_value, max_value)
            spinbox.setStyleSheet('background-color : white;')
            return spinbox

        def create_button(text, onclick, enabled=True):
            button = QPushButton(text)
            button.clicked.connect(onclick)
            button.setEnabled(enabled)
            return button

        def create_sub_layout(row, column, rowspan=1, columnspan=1, header_text=None, sub_items=[]):
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop)
            widget = QWidget()
            widget.setStyleSheet('background-color : lightgray;')
            widget.setLayout(layout)
            if header_text is not None:
                header = QLabel(header_text)
                header.setStyleSheet('font-weight : bold; font-size : 25px; alignment : center;')
                header.setAlignment(Qt.AlignHCenter)
                layout.addWidget(header, 0)
            for sub_item in sub_items:
                if isinstance(sub_item, QWidget):
                    layout.addWidget(sub_item)
                elif isinstance(sub_item, QLayout):
                    layout.addLayout(sub_item)
            main_layout.addWidget(widget, row, column, rowspan, columnspan)

        # window config
        main_layout = QGridLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('Scheduler & Process Simulator')
        self.setWindowIcon(QIcon('../resources/app_icon.png'))

        # graph at the top
        self._ui['graph_canvas'].setMinimumSize(800, 500)
        create_sub_layout(0, 0, columnspan=3, sub_items=[self._ui['graph_canvas']])

        # logger at the bottom left
        self._ui['logger'] = QLabel('')
        self._ui['logger'].setMinimumWidth(450)
        self._ui['logger'].setStyleSheet('font-size : 20px;')
        create_sub_layout(1, 0, header_text='LOGGER', sub_items=[self._ui['logger']])

        # process selection at the bottom center
        process_layout = QGridLayout()
        process_layout.addWidget(QLabel('PID'), 1, 1, Qt.AlignBottom)
        process_layout.addWidget(QLabel('Ready Time'), 1, 2, Qt.AlignBottom)
        process_layout.addWidget(QLabel('Execution Time'), 1, 3, Qt.AlignBottom)
        process_layout.addWidget(QLabel('Deadline'), 1, 4, Qt.AlignBottom)
        process_layout.addWidget(QLabel(''), 1, 5, Qt.AlignBottom)
        self._ui['process_selection'] = []
        for idx in range(len(PROCESS_COLORS)):
            grid_row = idx + 2
            checkbox = QCheckBox()
            process_layout.addWidget(checkbox, grid_row, 0, Qt.AlignmentFlag.AlignRight)
            label = QLabel(str(idx + 1))
            label.setStyleSheet(f'background-color : {PROCESS_COLORS[idx]};')
            process_layout.addWidget(label, grid_row, 1)
            ready_time_spinbox = create_spinbox(0, MAX_SIM_TIME // 2)
            process_layout.addWidget(ready_time_spinbox, grid_row, 2)
            exec_time_spinbox = create_spinbox(1, MAX_SIM_TIME // 2)
            process_layout.addWidget(exec_time_spinbox, grid_row, 3)
            deadline_spinbox = create_spinbox(1, MAX_SIM_TIME)
            process_layout.addWidget(deadline_spinbox, grid_row, 4)
            if set_default_values_for_exercise_1 and idx < len(DEFAULT_VALUES):
                ready_time_spinbox.setValue(DEFAULT_VALUES[idx][0])
                exec_time_spinbox.setValue(DEFAULT_VALUES[idx][1])
                deadline_spinbox.setValue(DEFAULT_VALUES[idx][2])
            self._ui['process_selection'].append((checkbox, ready_time_spinbox, exec_time_spinbox, deadline_spinbox))
        create_sub_layout(1, 1, header_text='PROCESSES', sub_items=[process_layout])

        # scheduler configuration at the bottom right
        configuration_layout = QFormLayout()
        self._ui['strategy_selection'] = QComboBox()
        self._ui['strategy_selection'].addItems(STRATEGIES)
        self._ui['strategy_selection'].setStyleSheet('background-color : white; selection-color : black;')
        configuration_layout.addRow(QLabel('Scheduler-Strategy'), self._ui['strategy_selection'])
        self._ui['n_cpus_selection'] = create_spinbox(1, MAX_CPUS)
        configuration_layout.addRow(QLabel('Number of CPUs (except "Round Robin"-Schedulers")'),
                                    self._ui['n_cpus_selection'])
        self._ui['quantum_selection'] = create_spinbox(1, MAX_QUANTUM)
        configuration_layout.addRow(QLabel('Quantum (only "Round Robin"-Schedulers")'), self._ui['quantum_selection'])
        self._ui['init_sim_button'] = create_button('Initialize Simulation', self._init_sim_button_clicked)
        self._ui['next_step_button'] = create_button('Do Next Simulation Step', self._next_step_button_clicked, False)
        self._ui['run_sim_button'] = create_button('Run Complete Simulation', self._run_sim_button_clicked, False)
        self._ui['reset_sim_button'] = create_button('Reset Simulation', self._reset_sim_button_clicked, False)
        create_sub_layout(1, 2, header_text='SCHEDULER CONFIGURATION', sub_items=[configuration_layout,
                                                                                  self._ui['init_sim_button'],
                                                                                  self._ui['next_step_button'],
                                                                                  self._ui['run_sim_button'],
                                                                                  self._ui['reset_sim_button']])

        self.showMaximized()
