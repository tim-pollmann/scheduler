import sys

from PyQt5.QtWidgets import QApplication, QGridLayout, QFormLayout, QMainWindow, QSpinBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import numpy as np

from constants import MAX_CPUS, MAX_TIME, STRATEGIES, LINE_WIDTH, PROCESS_COLORS
from scheduler import NP_FCFS_Scheduler, NP_SJF_Scheduler, NP_EDF_Scheduler, NP_LLF_Scheduler, P_SJF_Scheduler, P_EDF_Scheduler, P_RR_Scheduler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._ui = {}
        self._init_mpl()
        self._init_qt()
        self._scheduler = None
        self._graph_data = []

    def _init_sim_button_clicked(self):
        n_cpus = self._ui['n_cpus_selection'].value()

        process_data = [(ready_time_box.value(), exec_time_box.value(), deadline_box.value()) 
                        for (checkbox, ready_time_box, exec_time_box, deadline_box)
                        in self._ui['process_selection']
                        if checkbox.isChecked()]
        print(process_data)

        match self._ui['strategy_selection'].currentIndex():
            case 0:
                self._scheduler = NP_FCFS_Scheduler(n_cpus, process_data)
            case 1:
                self._scheduler = NP_SJF_Scheduler(n_cpus, process_data)
            case 2:
                self._scheduler = NP_EDF_Scheduler(n_cpus, process_data)
            case 3:
                self._scheduler = NP_LLF_Scheduler(n_cpus, process_data)
            case 4:
                self._scheduler = P_SJF_Scheduler(process_data)
            case 5:
                self._scheduler = P_EDF_Scheduler(process_data)
            case 6:
                quantum = 3
                self._scheduler = P_RR_Scheduler(process_data, quantum)

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
            for cpu in self._scheduler.cpus:
                for timestamp, pid in cpu.history:
                    rectangle = Rectangle((timestamp, cpu.id - LINE_WIDTH / 2), 1, LINE_WIDTH, facecolor=PROCESS_COLORS[pid - 1])
                    self._graph_data.append(self._ui['graph_axes'].add_patch(rectangle))

        self._ui['graph_canvas'].draw_idle()

    def _init_mpl(self):
        fig = Figure()
        self._ui['graph_axes'] = fig.add_subplot(111)
        self._ui['graph_axes'].set_ylabel('CPUs')
        self._ui['graph_axes'].set_xlabel('Time')
        self._ui['graph_axes'].xaxis.tick_top()
        self._ui['graph_axes'].xaxis.set_label_position('top') 
        self._ui['graph_axes'].set_xlim(0, MAX_TIME)
        self._ui['graph_axes'].set_ylim(- 0.5, MAX_CPUS - 0.5)
        self._ui['graph_axes'].xaxis.set_ticks(np.arange(0, MAX_TIME + 1, 5))
        self._ui['graph_axes'].set_xticks(np.arange(0, MAX_TIME + 1, 1), minor=True)
        self._ui['graph_axes'].yaxis.set_ticks(np.arange(0, MAX_CPUS, 1))
        self._ui['graph_axes'].grid(axis='x', which='major', alpha=0.7) 
        self._ui['graph_axes'].grid(axis='x', which='minor', alpha=0.35)
        self._ui['graph_canvas'] = Canvas(fig)

    def _init_qt(self):
        self._ui['logger'] = QLabel('')

        self._ui['strategy_selection'] = QComboBox()
        self._ui['strategy_selection'].addItems(STRATEGIES)
        
        self._ui['n_cpus_selection'] = QSpinBox()
        self._ui['n_cpus_selection'].setRange(1, 3)

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

        process_checkboxes = []
        ready_time_spinboxes = []
        exec_time_spinboxes = []
        deadline_spinboxes = []

        def create_spinbox(min, max, list):
            spinbox = QSpinBox()
            spinbox.setRange(min, max)
            list.append(spinbox)
            return spinbox

        for row in range(len(PROCESS_COLORS)):
            checkbox = QCheckBox()
            process_checkboxes.append(checkbox)
            process_layout.addWidget(checkbox, row + 1, 0)
            process_layout.addWidget(QLabel(str(row + 1)), row + 1, 1)
            process_layout.addWidget(create_spinbox(0, 49, ready_time_spinboxes), row + 1, 2)
            process_layout.addWidget(create_spinbox(1, 49, exec_time_spinboxes), row + 1, 3)
            process_layout.addWidget(create_spinbox(1, 49, deadline_spinboxes), row + 1, 4)

        self._ui['process_selection'] = zip(process_checkboxes, ready_time_spinboxes, exec_time_spinboxes, deadline_spinboxes)

        control_layout = QVBoxLayout()
        control_layout.addLayout(form_layout)
        control_layout.addLayout(process_layout)
        control_layout.addWidget(self._ui['init_sim_button'])
        control_layout.addWidget(self._ui['next_step_button'])
        control_layout.addWidget(self._ui['run_sim_button'])
        control_layout.addWidget(self._ui['reset_sim_button'])

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self._ui['logger'])
        lower_layout.addLayout(control_layout)

        central_layout = QVBoxLayout()
        central_layout.addWidget(self._ui['graph_canvas'])
        central_layout.addLayout(lower_layout)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        self.setWindowTitle('Scheduler & Process Simulator')
        self.setCentralWidget(central_widget)
        self.showMaximized()


def main():
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
