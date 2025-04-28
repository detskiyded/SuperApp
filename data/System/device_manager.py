from PyQt5.QtCore import QTimer, QObject, pyqtSignal
import os
import getpass
from logger import log_event

class RemovableDeviceManager(QObject):
    device_added = pyqtSignal(str)
    device_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = getpass.getuser()
        self.media_path = f"/media/{self.username}"
        self.known_devices = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_devices)
        self.timer.start(3000)  # Проверять каждые 3 секунды

    def check_devices(self):
        current_devices = set()
        if os.path.exists(self.media_path):
            for device in os.listdir(self.media_path):
                device_path = os.path.join(self.media_path, device)
                if os.path.isdir(device_path):
                    current_devices.add(device_path)

        # Новые устройства
        added_devices = current_devices - self.known_devices
        for device in added_devices:
            self.device_added.emit(device)

        # Отключенные устройства
        removed_devices = self.known_devices - current_devices
        for device in removed_devices:
            self.device_removed.emit(device)

        # Обновляем список известных устройств
        self.known_devices = current_devices
