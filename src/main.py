import ctypes
import argparse
import sys
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow
from bss_exercises import exercise_1, exercise_2, exercise_3


if __name__ == '__main__':
    # workaround to display custom taskbar icon
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('scheduler_and_process_simulator')

    parser = argparse.ArgumentParser()
    parser.add_argument('-1', '--exercise_1', action='store_true', help='set flag to execute exercise 1 on the command'
                                                                        'line')
    parser.add_argument('-2', '--exercise_2', action='store_true', help='set flag to execute exercise 2 on the command'
                                                                        'line')
    parser.add_argument('-3', '--exercise_3', action='store_true', help='set flag to execute exercise 3 on the command '
                                                                        'line')
    parser.add_argument('-l', '--logger', action='store_true', help='set flag to show the logger as output on the '
                                                                    'command line when executing exercise 1')
    parser.add_argument('-q', '--quantum', help='sets the quantum of the "Round Robin"-scheduler from exercise 2 to'
                                                'the specified value, min value is 1')
    parser.add_argument('-s', '--set_bss_examples', action='store_true', help='set flag to set some default values')
    args = parser.parse_args()

    if args.exercise_1:
        exercise_1(args.logger)

    if args.exercise_2:
        if args.quantum is None:
            parser.error('-2/--exercise_2 requires -q/--quantum to be specified')

        quantum = int(args.quantum)
        if not 0 < quantum:
            parser.error('quantum must be minimum 1')

        exercise_2(quantum)

    if args.exercise_3:
        exercise_3()

    if not args.exercise_1 and not args.exercise_2 and not args.exercise_3:
        app = QApplication([])
        app.setStyle('Fusion')
        mainwindow = MainWindow(args.set_bss_examples)
        mainwindow.show()
        app.exec()

    sys.exit(0)
