from PyQt5.QtWidgets import QTreeWidgetItem

class SearchEngine:
    def __init__(self, tree_view):
        self.tree_view = tree_view

    def search(self, query):
        if not query:
            # Если строка поиска пустая — показываем всё дерево
            self._show_all_items(self.tree_view.invisibleRootItem())
        else:
            # Иначе — фильтруем дерево
            self._filter_items(self.tree_view.invisibleRootItem(), query.lower())

    def _show_all_items(self, parent_item):
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child.setHidden(False)
            self._show_all_items(child)

    def _filter_items(self, parent_item, query):
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            self._filter_items(child, query)

            # Проверяем имя узла
            matches = query in child.text(0).lower()

            # Проверяем детей (если у детей есть совпадения, родителя тоже показываем)
            has_visible_children = any(not child.child(j).isHidden() for j in range(child.childCount()))

            # Если ни сам элемент, ни его дети не подходят — скрываем элемент
            child.setHidden(not (matches or has_visible_children))
