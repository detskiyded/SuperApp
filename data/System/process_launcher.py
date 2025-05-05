# process_launcher.py
import sys
from PyQt5.QtWidgets import QApplication
from child_process import ChildWindow

def run_child_window(queue):
    app = QApplication(sys.argv)
    window = ChildWindow(queue)
    window.show()
    sys.exit(app.exec_())
