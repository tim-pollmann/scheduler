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
    parser.add_argument('-1', '--exercise_1', action='store_true', help='execute exercise 1 on the commandline')
    parser.add_argument('-2', '--exercise_2', action='store_true', help='execute exercise 2 on the commandline')
    parser.add_argument('-3', '--exercise_3', action='store_true', help='execute exercise 3 on the commandline')
    parser.add_argument('-l', '--logger', action='store_true', help='show logger output when executing exercise 1')
    parser.add_argument('-q', '--quantum', help='set quantum of the "Round Robin"-schedulers from exercise 1 and 2')
    parser.add_argument('-s', '--sorted', action='store_true', help='print result of exercise 2 and 3 sorted by the '
                                                                    'average delta time')
    parser.add_argument('-b', '--bss_examples', action='store_true', help='set some default values in the simulator')
    args = parser.parse_args()

    if args.exercise_1 or args.exercise_2:
        if args.quantum is None:
            parser.error('-1/--exercise_1 and/ or -2/--exercise_2 requires -q/--quantum to be specified')

        quantum = int(args.quantum)
        if not 0 < quantum:
            parser.error('quantum must be minimum 1')

    if args.exercise_1:
        exercise_1(quantum, args.logger)

    if args.exercise_2:
        exercise_2(quantum, args.sorted)

    if args.exercise_3:
        exercise_3(args.sorted)

    if not args.exercise_1 and not args.exercise_2 and not args.exercise_3:
        app = QApplication([])
        app.setStyle('Fusion')
        mainwindow = MainWindow(args.bss_examples)
        mainwindow.show()
        app.exec()

    sys.exit(0)
