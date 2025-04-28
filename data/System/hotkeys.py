from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QKeySequence

from logger import log_event


class Hotkeys:
    def __init__(self, main_window):
        self.main_window = main_window
        self.setup_hotkeys()

    def setup_hotkeys(self):
        self.main_window.action_create_file.setShortcut(QKeySequence("Ctrl+N"))
        self.main_window.action_create_file.triggered.connect(self.create_file)

        self.main_window.action_create_folder.setShortcut(QKeySequence("Ctrl+Shift+N"))
        self.main_window.action_create_folder.triggered.connect(self.create_folder)

        self.main_window.action_move_to_trash.setShortcut(QKeySequence("Ctrl+D"))
        self.main_window.action_move_to_trash.triggered.connect(self.move_to_trash)

        self.main_window.action_rename.setShortcut(QKeySequence("Ctrl+R"))
        self.main_window.action_rename.triggered.connect(self.rename_item)

        self.main_window.action_clear_trash.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self.main_window.action_clear_trash.triggered.connect(self.clear_trash)

    def create_file(self):
        log_event("Горячая клавиша: Создание файла (Ctrl+N)")
        selected_item = self.main_window.tree_view.currentItem()

        if selected_item:
            folder_path = self.main_window.tree_view.get_item_path(selected_item)
        else:
            # Явно ставим путь в data/, если ничего не выбрано
            folder_path = self.main_window.tree_view.data_folder

        self.main_window.tree_view.create_file_in(folder_path)

    def create_folder(self):
        log_event("Горячая клавиша: Создание папки (Ctrl+Shift+N)")
        selected_item = self.main_window.tree_view.currentItem()

        if selected_item:
            folder_path = self.main_window.tree_view.get_item_path(selected_item)
        else:
            folder_path = self.main_window.tree_view.data_folder

        self.main_window.tree_view.create_folder_in(folder_path)

    def move_to_trash(self):
        log_event("Горячая клавиша: Перемещение в корзину (Ctrl+D)")
        selected_item = self.main_window.tree_view.currentItem()

        if selected_item:
            self.main_window.tree_view.move_to_trash(selected_item)
        else:
            log_event("Не был выбран элемент для перемещения в корзину.")

    def rename_item(self):
        log_event("Горячая клавиша: Переименование (Ctrl+R)")
        selected_item = self.main_window.tree_view.currentItem()

        if selected_item:
            self.main_window.tree_view.rename_item(selected_item)
        else:
            print("Не был выбран элемента для переименования.")

    def clear_trash(self):
        log_event("Горячая клавиша: Очистка корзины (Ctrl+Shift+E)")
        self.main_window.tree_view.clear_trash()
