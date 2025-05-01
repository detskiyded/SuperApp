import getpass

from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QIcon
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt
import os
import shutil
from logger import log_event

class FolderTreeView(QTreeWidget):
    def __init__(self, system_folder, trashbin_folder, user_folders_folder):
        super().__init__()
        self.setHeaderLabel("SuperApp")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Загрузка иконок
        icons_path = os.path.join("data", "System", "icons")
        self.folder_icon = QIcon(os.path.join(icons_path, "folder.png"))
        self.file_icon = QIcon(os.path.join(icons_path, "document.png"))
        self.trash_icon = QIcon(os.path.join(icons_path, "trashbin.png"))
        self.usb_icon = QIcon(os.path.join(icons_path, "usb.png"))

        # Drag and drop setup
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDrop)

        self.system_folder = system_folder
        self.trashbin_folder = trashbin_folder
        self.user_folders_folder = user_folders_folder
        self.data_folder = os.path.dirname(self.system_folder)

        self.populate_tree()

    def populate_tree(self):
        self.clear()

        system_item = QTreeWidgetItem([os.path.basename(self.system_folder)])
        system_item.setIcon(0, self.folder_icon)
        self.addTopLevelItem(system_item)
        self.load_folder_contents(self.system_folder, system_item)

        trashbin_item = QTreeWidgetItem([os.path.basename(self.trashbin_folder)])
        trashbin_item.setIcon(0, self.trash_icon)
        self.addTopLevelItem(trashbin_item)
        self.load_folder_contents(self.trashbin_folder, trashbin_item)

        user_folders_item = QTreeWidgetItem([os.path.basename(self.user_folders_folder)])
        user_folders_item.setIcon(0, self.folder_icon)
        self.addTopLevelItem(user_folders_item)
        self.load_folder_contents(self.user_folders_folder, user_folders_item)

        self.addTopLevelItem(system_item)
        self.addTopLevelItem(trashbin_item)
        self.addTopLevelItem(user_folders_item)

        self.load_folder_contents(self.system_folder, system_item)
        self.load_folder_contents(self.trashbin_folder, trashbin_item)
        self.load_folder_contents(self.user_folders_folder, user_folders_item)

        # Добавим всё остальное из data/
        excluded = {self.system_folder, self.trashbin_folder, self.user_folders_folder}
        for entry in os.listdir(self.data_folder):
            full_path = os.path.join(self.data_folder, entry)
            if full_path in excluded:
                continue

            if os.path.isdir(full_path):
                item = QTreeWidgetItem([entry])
                item.setIcon(0, self.folder_icon)
                self.addTopLevelItem(item)
                self.load_folder_contents(full_path, item)
            else:
                file_item = QTreeWidgetItem([entry])
                file_item.setIcon(0, self.file_icon)
                self.addTopLevelItem(file_item)

        # Теперь добавляем съёмные носители
        removable_root = QTreeWidgetItem(self, ["Съемные носители"])
        username = getpass.getuser()
        media_path = f"/media/{username}"

        if os.path.exists(media_path):
             for device in os.listdir(media_path):
                device_path = os.path.join(media_path, device)
                if os.path.isdir(device_path):
                    device_item = QTreeWidgetItem(removable_root, [device])
                    device_item.setIcon(0, self.usb_icon)
                    self.load_folder_contents(device_path, device_item)

        self.clearSelection()
        self.setCurrentItem(None)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            clicked_item = self.itemAt(event.pos())
            if clicked_item is None:
                self.clearSelection()  # Снять визуальное выделение
                self.setCurrentItem(None)  # Снять логическое выделение
        super().mousePressEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            # External drag from system
            target_item = self.itemAt(event.pos())
            target_path = self.get_item_path(target_item) if target_item else self.user_folders_folder

            if os.path.isfile(target_path):
                target_path = os.path.dirname(target_path)

            for url in event.mimeData().urls():
                src = url.toLocalFile()
                if os.path.exists(src):
                    dst = os.path.join(target_path, os.path.basename(src))
                    try:
                        if os.path.isdir(src):
                            shutil.copytree(src, dst)
                            log_event(f"Скопирована папка из внешнего источника: '{src}' в '{dst}'")
                        else:
                            shutil.copy2(src, dst)
                            log_event(f"Скопирован файл из внешнего источника: '{src}' в '{dst}'")
                    except Exception as e:
                        QMessageBox.warning(self, "Ошибка", f"Не удалось скопировать: {e}")
            self.populate_tree()

        else:
            # Internal move
            selected_items = self.selectedItems()
            target_item = self.itemAt(event.pos())
            if not target_item:
                return

            target_path = self.get_item_path(target_item)
            if os.path.isfile(target_path):
                target_path = os.path.dirname(target_path)

            for source_item in selected_items:
                source_path = self.get_item_path(source_item)

                # Запрет: нельзя перемещать из System
                if source_path.startswith(self.system_folder):
                    QMessageBox.warning(self, "Ошибка", "Нельзя перемещать файлы из папки System.")
                    continue

                # Запретить перетаскивание папки System
                if os.path.abspath(source_path) == os.path.abspath(self.system_folder):
                    QMessageBox.warning(self, "Ошибка", "Нельзя перемещать папку System.")
                    continue

                # Запрет: нельзя перемещать внутрь System
                if target_path.startswith(self.system_folder):
                    QMessageBox.warning(self, "Ошибка", "Нельзя перемещать файлы в папку System.")
                    continue

                # Защита от перемещения в саму себя
                if os.path.commonpath([os.path.abspath(source_path), os.path.abspath(target_path)]) == os.path.abspath(source_path):
                    QMessageBox.warning(self, "Ошибка", "Нельзя переместить папку саму в себя или внутрь себя.")
                    continue

                # Защита от перемещения в ту же папку
                if os.path.abspath(os.path.dirname(source_path)) == os.path.abspath(target_path):
                    continue

                # Перемещение в корзину
                if os.path.commonpath([target_path, self.trashbin_folder]) == self.trashbin_folder:
                    self.move_path_to_trash(source_path)
                    log_event(f"Перемещён элемент в корзину через Drag'n'Drop: '{source_path}'")
                    continue

                new_path = os.path.join(target_path, os.path.basename(source_path))

                try:
                    if os.path.exists(new_path):
                        QMessageBox.warning(self, "Ошибка", f"{os.path.basename(source_path)} уже существует в целевой папке.")
                        continue
                    shutil.move(source_path, new_path)
                    log_event(f"Перемещён элемент через Drag'n'Drop: {source_path} -> {new_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Ошибка при перемещении: {e}")

            self.populate_tree()

    def move_path_to_trash(self, path):
        # Защита: нельзя удалить саму папку System
        if os.path.abspath(path) == os.path.abspath(self.system_folder):
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить папку System.")
            return

        # Защита: нельзя удалить файл из System
        if path.startswith(self.system_folder):
            QMessageBox.warning(self, "Ошибка", "Нельзя удалять файлы из папки System.")
            return

        if path.startswith(self.trashbin_folder):
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить файлы из корзины.")
            return

        if path.startswith(self.user_folders_folder):
            base_folder = self.user_folders_folder
        elif path.startswith(self.data_folder):
            base_folder = self.data_folder
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить корень для перемещения.")
            return

        relative_path = os.path.relpath(path, base_folder)
        trash_path = os.path.join(self.trashbin_folder, relative_path)

        try:
            os.makedirs(os.path.dirname(trash_path), exist_ok=True)
            shutil.move(path, trash_path)
            self.populate_tree()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось переместить в корзину: {e}")
            log_event(f"Не удалось переместить в корзину: {e}")

    def load_folder_contents(self, folder_path, parent_item):
        try:
            for entry in os.listdir(folder_path):
                full_path = os.path.join(folder_path, entry)
                if os.path.isdir(full_path):
                    folder_item = QTreeWidgetItem(parent_item, [entry])
                    folder_item.setIcon(0, self.folder_icon)
                    self.load_folder_contents(full_path, folder_item)
                else:
                    file_item = QTreeWidgetItem(parent_item, [entry])
                    file_item.setIcon(0, self.file_icon)
        except Exception as e:
            print(f"Ошибка при загрузке папки: {folder_path} — {e}")

    def show_context_menu(self, position):
        selected_item = self.itemAt(position)

        menu = QMenu()

        # если клик по папке TrashBin
        if selected_item and os.path.abspath(self.get_item_path(selected_item)) == os.path.abspath(
                self.trashbin_folder):
            clear_trash_action = QAction("Очистить корзину", self)
            clear_trash_action.triggered.connect(self.clear_trash)
            menu.addAction(clear_trash_action)

        # если клик по обычному элементу
        else:
            selected_path = self.get_item_path(selected_item) if selected_item else self.data_folder

            # создание файла
            create_file_action = QAction("Создать файл", self)
            create_file_action.triggered.connect(lambda: self.create_file_in(selected_path))
            menu.addAction(create_file_action)

            # создание папки
            create_folder_action = QAction("Создать папку", self)
            create_folder_action.triggered.connect(lambda: self.create_folder_in(selected_path))
            menu.addAction(create_folder_action)

            if selected_item and os.path.abspath(selected_path) != os.path.abspath(self.system_folder):
                rename_action = QAction("Переименовать", self)
                rename_action.triggered.connect(lambda: self.rename_item(selected_item))
                menu.addAction(rename_action)

            # перемещение в корзину (если это не System)
            if selected_item and os.path.abspath(self.get_item_path(selected_item)) != os.path.abspath(
                    self.system_folder):
                move_to_trash_action = QAction("Поместить в корзину", self)
                move_to_trash_action.triggered.connect(lambda: self.move_to_trash(selected_item))
                menu.addAction(move_to_trash_action)

        menu.exec_(self.viewport().mapToGlobal(position))

    def create_file_in(self, folder_path):
        file_name, ok = QInputDialog.getText(self, "Создать файл", "Введите имя файла:")
        if ok and file_name:
            path = os.path.join(folder_path, file_name)
            try:
                with open(path, "w") as f:
                    f.write("")
                self.populate_tree()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать файл: {e}")
                log_event(f"Не удалось создать файл: {e}")
        log_event(f"Был создан файл {file_name} в пути: {folder_path}")


    def create_folder_in(self, folder_path):
        folder_name, ok = QInputDialog.getText(self, "Создать папку", "Введите имя папки:")
        if ok and folder_name:
            path = os.path.join(folder_path, folder_name)
            try:
                os.makedirs(path, exist_ok=True)
                self.populate_tree()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать папку: {e}")
                log_event(f"Не удалось создать папку: {e}")
        log_event(f"Была создана папка {folder_name} в пути: {folder_path}")

    def on_item_double_clicked(self, item, column):
        file_path = self.get_item_path(item)
        if os.path.isfile(file_path):
            self.open_file(item)

    def open_file(self, item):
        file_path = self.get_item_path(item)
        if os.path.isfile(file_path):
            os.system(f"xdg-open '{file_path}'")
        else:
            QMessageBox.warning(self, "Ошибка", "Это не файл!")

    def rename_item(self, item):
        """Переименование файла или папки."""
        if not item:
            return

        old_path = self.get_item_path(item)
        old_name = item.text(0)

        # Защита: нельзя переименовать папку System
        if os.path.abspath(old_path) == os.path.abspath(self.system_folder):
            QMessageBox.warning(self, "Ошибка", "Нельзя переименовать папку System.")
            return

        new_name, ok = QInputDialog.getText(self, "Переименовать", "Введите новое имя:")
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)

            if os.path.exists(new_path):
                QMessageBox.warning(self, "Ошибка", "Файл или папка с таким именем уже существует.")
                return

            try:
                os.rename(old_path, new_path)
                self.populate_tree()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при переименовании: {e}")
        log_event(f"Переименован элемент: {old_name} -> {new_name}")

    def move_to_trash(self, item):
        path = self.get_item_path(item)

        # Защита от перемещения самой папки System
        if os.path.abspath(path) == os.path.abspath(self.system_folder):
            QMessageBox.warning(self, "Ошибка", "Нельзя перемещать папку System.")
            return

        # Защита от удаления файлов внутри папки System
        if os.path.abspath(path).startswith(os.path.abspath(self.system_folder)):
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить файлы из папки System.")
            return

        # Получаем путь к родительской папке, чтобы избежать её добавления в корзину
        parent_path = os.path.dirname(path)

        # Если это папка, то нужно перемещать только содержимое папки, не включая родительскую
        if os.path.isdir(path):
            item_name = os.path.basename(path)  # Название папки (например, intestdir)
            # Строим путь в корзине, исключая родительскую папку
            trash_path = os.path.join(self.trashbin_folder, item_name)

            try:
                # Проверка, существует ли уже такая папка в корзине
                if os.path.exists(trash_path):
                    QMessageBox.warning(self, "Ошибка", f"Папка {item_name} уже существует в корзине.")
                    return

                # Перемещаем только папку и её содержимое
                shutil.move(path, trash_path)
                self.populate_tree()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при перемещении: {e}")
        else:
            # Для файлов просто вызываем move_path_to_trash
            self.move_path_to_trash(path)
        log_event(f"Перемещено в корзину: {path}")

    def clear_trash(self):
        for entry in os.listdir(self.trashbin_folder):
            entry_path = os.path.join(self.trashbin_folder, entry)
            try:
                if os.path.isfile(entry_path):
                    os.remove(entry_path)
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при очистке: {e}")
        self.populate_tree()
        log_event("Корзина очищена")

    def get_item_path(self, item):
        path_parts = []
        while item:
            path_parts.insert(0, item.text(0))
            item = item.parent()

        if path_parts[0] == "Съемные носители":
            username = getpass.getuser()
            return os.path.join("/media", username, *path_parts[1:])

        top_name = path_parts[0]

        if top_name == os.path.basename(self.system_folder):
            base_folder = self.system_folder
            rel_parts = path_parts[1:]
        elif top_name == os.path.basename(self.trashbin_folder):
            base_folder = self.trashbin_folder
            rel_parts = path_parts[1:]
        elif top_name == os.path.basename(self.user_folders_folder):
            base_folder = self.user_folders_folder
            rel_parts = path_parts[1:]
        else:
            # Если это элемент на уровне data/, тогда top_name — это и есть имя в data/
            base_folder = self.data_folder
            rel_parts = path_parts

        return os.path.join(base_folder, *rel_parts)

    def data_folder_from_name(self, name):
        if name == os.path.basename(self.system_folder):
            return self.system_folder
        elif name == os.path.basename(self.trashbin_folder):
            return self.trashbin_folder
        elif name == os.path.basename(self.user_folders_folder):
            return self.user_folders_folder
        else:
            # Все прочие файлы/папки считаются лежащими в data/
            return self.data_folder
