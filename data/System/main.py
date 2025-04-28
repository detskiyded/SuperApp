import os
from search import SearchEngine
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QMessageBox,
    QAction, QMenuBar
)
from hotkeys import Hotkeys
from tree_view import FolderTreeView
from device_manager import RemovableDeviceManager
from logger import log_event
from command_interpreter import CommandInterpreter


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.user_folders_folder = None
        self.trashbin_folder = None
        self.system_folder = None
        self.data_folder = None

        # Создаём действия для горячих клавиш
        self.action_create_file = QAction("Создать файл", self)
        self.action_create_folder = QAction("Создать папку", self)
        self.action_move_to_trash = QAction("Поместить в корзину", self)
        self.action_rename = QAction("Переименовать", self)
        self.action_clear_trash = QAction("Очистить корзину", self)

        # Добавляем действия в окно
        self.addAction(self.action_create_file)
        self.addAction(self.action_create_folder)
        self.addAction(self.action_move_to_trash)
        self.addAction(self.action_rename)
        self.addAction(self.action_clear_trash)
        self.hotkeys = Hotkeys(self) # Подключаем хоткеи

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск файлов и папок...")
        self.search_bar.textChanged.connect(self.perform_search)
        self.search_engine = None  # Инициализация объекта поиска

        self.setFocusPolicy(Qt.StrongFocus)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Определяем пути
        self.data_folder = os.path.join(os.getcwd(), "data")
        self.system_folder = os.path.join(self.data_folder, "System")
        self.trashbin_folder = os.path.join(self.data_folder, "TrashBin")
        self.user_folders_folder = os.path.join(self.data_folder, "UserFolders")

        # Создаём необходимые папки
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.system_folder, exist_ok=True)
        os.makedirs(self.trashbin_folder, exist_ok=True)
        os.makedirs(self.user_folders_folder, exist_ok=True)

        # Поле поиска
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск файлов и папок...")
        self.search_bar.textChanged.connect(self.perform_search)
        layout.addWidget(self.search_bar, stretch=0)  # Строка поиска (очень тонкая)

        # Дерево файлов
        self.tree_view = FolderTreeView(
            system_folder=self.system_folder,
            trashbin_folder=self.trashbin_folder,
            user_folders_folder=self.user_folders_folder
        )
        layout.addWidget(self.tree_view, stretch=10)

        self.device_manager = RemovableDeviceManager()
        self.device_manager.device_added.connect(self.on_device_added)
        self.device_manager.device_removed.connect(self.on_device_removed)

        # Создаём меню
        self.menu_bar = QMenuBar(self)
        help_menu = self.menu_bar.addMenu("Помощь")
        help_action = QAction("Справка", self)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)
        layout.setMenuBar(self.menu_bar)

        utilities_menu = self.menu_bar.addMenu("Утилиты")

        # В меню "Утилиты"
        interpreter_action = QAction("Командный интерпретатор", self)
        interpreter_action.triggered.connect(self.open_command_interpreter)
        utilities_menu.addAction(interpreter_action)

        self.setLayout(layout)
        self.search_engine = SearchEngine(self.tree_view)

        # Встраиваем меню и дерево файлов
        layout.setMenuBar(self.menu_bar)
        layout.addWidget(self.tree_view)
        self.setLayout(layout)

    def perform_search(self, text):
        if self.search_engine:
            self.search_engine.search(text)

    def on_device_added(self, device_path):
        log_event(f"Подключено новое устройство: {device_path}")
        self.tree_view.populate_tree()

    def on_device_removed(self, device_path):
        log_event(f"Отключено устройство: {device_path}")
        self.tree_view.populate_tree()

    def open_command_interpreter(self):
        self.interpreter_window = CommandInterpreter()
        self.interpreter_window.show()

    def show_about_dialog(self):
        QMessageBox.information(
            self,
            "О программе",
            "Файловый менеджер на PyQt5\n"
            "Операционные системы и оболочки\n"
            "Группа: ПрИ-32\n"
            "Автор: Попков Алексей"
        )

    def show_help_dialog(self):
        help_text = (
            "<b>Горячие клавиши:</b><br><br>"
            "<b>Ctrl+N</b> — Создать новый файл<br>"
            "<b>Ctrl+Shift+N</b> — Создать новую папку<br>"
            "<b>Ctrl+D</b> — Поместить выбранный элемент в корзину<br>"
            "<b>Ctrl+R</b> — Переименовать выбранный элемент<br>"
            "<b>Ctrl+Shift+E</b> — Очистить корзину<br>"
        )
        QMessageBox.information(self, "Справка", help_text)

if __name__ == "__main__":
    app = QApplication([])

    font = QFont("Ubuntu-Sans", 18)
    app.setFont(font)

    window = MainWindow()
    window.setWindowTitle("Файловый менеджер")
    window.resize(800, 600)
    window.show()
    app.exec_()
