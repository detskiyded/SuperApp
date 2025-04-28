import json
import os

class FileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        """Загрузка данных из файла."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return json.load(file)
        return []

    def save_data(self, data):
        """Сохранение данных в файл."""
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)