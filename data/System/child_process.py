import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import QTimer
import sys

class ChildWindow(QWidget):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.initUI()
        self.start_updating()

    def initUI(self):
        self.setWindowTitle("Child Process Window")
        self.label = QLabel("Ожидание данных...", self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def start_updating(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_queue)  # <- исправлено имя метода
        self.timer.start(500)

    def check_queue(self):
        try:
            while not self.queue.empty():
                data = self.queue.get_nowait()
                data["child_pid"] = os.getpid()
                self.label.setText(
                    f"Ширина: {data['width']}, Высота: {data['height']},\n"
                    f"PID главного окна: {data['pid']}, PID дочернего окна: {data['child_pid']},\n"
                    f"FDs: {data['fds']}"
                )
        except Exception as e:
            print(f"[Ошибка получения данных]: {e}")

def run_child_window(queue):
    app = QApplication(sys.argv)
    window = ChildWindow(queue)
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())
