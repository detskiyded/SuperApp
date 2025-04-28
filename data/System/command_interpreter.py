from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
import subprocess
import os

class CommandInterpreter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Командный интерпретатор")
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)

        # Создаём шрифт
        console_font = QFont("Courier New")
        console_font.setStyleHint(QFont.Monospace)
        console_font.setPointSize(10)

        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.execute_command)

        # Применяем шрифт к полям
        self.output_area.setFont(console_font)
        self.input_field.setFont(console_font)

        layout.addWidget(self.output_area)
        layout.addWidget(self.input_field)
        self.setLayout(layout)

        # ВАЖНО: начальная папка будет папкой data/
        self.default_start_path = os.path.abspath(os.path.join(os.getcwd(), "data"))
        self.current_path = self.default_start_path

        self.show_help_message()

    def show_help_message(self):
        help_text = (
            "Доступные команды:\n"
            "  ping [адрес]       - Пинговать сервер\n"
            "  ipconfig           - Показать IP настройки\n"
            "  traceroute [адрес] - Маршрут до сервера\n"
            "  nslookup [домен]   - Узнать IP сайта\n"
            "  whoami             - Текущий пользователь\n"
            "  ls                 - Список файлов\n"
            "  cd [путь]          - Сменить папку\n"
            "  mkdir [имя]        - Создать папку\n"
            "  rmdir [имя]        - Удалить папку\n"
            "  cat [файл]         - Показать содержимое файла\n"
        )
        self.output_area.append(help_text)

    def execute_command(self):
        command_text = self.input_field.text().strip()
        self.input_field.clear()

        if not command_text:
            return

        self.output_area.append(f"{self.current_path} > {command_text}")


        if command_text.startswith("ping"):
            self.run_system_command(["ping", "-c", "4"] + command_text.split()[1:])
        elif command_text == "ipconfig":
            self.run_system_command(["ip", "a"])
        elif command_text.startswith("traceroute"):
            self.run_system_command(["traceroute"] + command_text.split()[1:])
        elif command_text.startswith("nslookup"):
            self.run_system_command(["nslookup"] + command_text.split()[1:])
        elif command_text == "whoami":
            self.run_system_command(["whoami"])
        elif command_text == "ls":
            self.run_system_command(["ls", self.current_path])
        elif command_text.startswith("cd"):
            parts = command_text.split(maxsplit=1)
            if len(parts) > 1:
                new_path = parts[1]
                if new_path == "/":  # Особая обработка команды cd /
                    self.current_path = self.default_start_path
                else:
                    new_path = os.path.abspath(os.path.join(self.current_path, new_path))
                    if os.path.isdir(new_path):
                        self.current_path = new_path
                        self.output_area.append(f"Текущая папка изменена на: {self.current_path}")
                    else:
                        self.output_area.append("Папка не найдена.")
            else:
                self.output_area.append("Не указан путь.")
        elif command_text.startswith("mkdir"):
            parts = command_text.split(maxsplit=1)
            if len(parts) > 1:
                path = os.path.join(self.current_path, parts[1])
                try:
                    os.mkdir(path)
                    self.output_area.append(f"Создана папка: {path}")
                except Exception as e:
                    self.output_area.append(f"Ошибка создания папки: {e}")
        elif command_text.startswith("rmdir"):
            parts = command_text.split(maxsplit=1)
            if len(parts) > 1:
                path = os.path.join(self.current_path, parts[1])
                try:
                    os.rmdir(path)
                    self.output_area.append(f"Удалена папка: {path}")
                except Exception as e:
                    self.output_area.append(f"Ошибка удаления папки: {e}")
        elif command_text.startswith("cat"):
            parts = command_text.split(maxsplit=1)
            if len(parts) > 1:
                path = os.path.join(self.current_path, parts[1])
                self.run_system_command(["cat", path])
        else:
            self.output_area.append("Неизвестная команда.")

    def run_system_command(self, command_list):
        try:
            output = subprocess.check_output(command_list, stderr=subprocess.STDOUT).decode("utf-8")
            self.output_area.append(output)
        except subprocess.CalledProcessError as e:
            self.output_area.append(f"Ошибка выполнения команды:\n{e.output.decode('utf-8')}")
