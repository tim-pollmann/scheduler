import sys
import argparse
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow
from bss_exercises import exercise2, exercise3

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-2', '--exercise2', action='store_true',
                        help='set flag to see the output from exercise 2 on the command line')
    parser.add_argument('-3', '--exercise3', action='store_true',
                        help='set flag to see the output from exercise 3 on the command line')
    parser.add_argument('-q', '--quantum', help='set quantum for exercise 2 to a value between 1 an 9')
    args = parser.parse_args()

    if args.exercise2:
        exercise2(int(args.quantum) if args.quantum is not None and 0 < int(args.quantum) < 10 else 3)

    if args.exercise3:
        exercise3()

    app = QApplication([])
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())
