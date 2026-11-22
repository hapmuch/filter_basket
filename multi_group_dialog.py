from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
)


class MultiGroupDialog(QDialog):

    def __init__(
        self,
        groups,
        group_field,
        parent=None
    ):
        """
        groups: dict mapping group_value -> iterable of cell values
        All cells are checked by default.
        """
        super().__init__(parent)

        self.setWindowTitle("Select Source Values")

        layout = QVBoxLayout()

        self.list_widget = QListWidget()

        for group in sorted(groups.keys(), key=lambda v: str(v)):
            cells = groups[group]
            header = QListWidgetItem(
                f"Group ({group_field}): {group}"
            )
            header.setFlags(
                Qt.ItemFlag.ItemIsEnabled
            )
            font = header.font()
            font.setBold(True)
            header.setFont(font)
            header.setData(Qt.ItemDataRole.UserRole, None)
            self.list_widget.addItem(header)

            for cell in sorted(cells, key=lambda v: str(v)):
                item = QListWidgetItem(f"  {cell}")
                item.setFlags(
                    item.flags()
                    | Qt.ItemFlag.ItemIsUserCheckable
                )
                item.setCheckState(Qt.CheckState.Checked)
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    (str(group), str(cell))
                )
                self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        button_row = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(
            self.select_all
        )
        button_row.addWidget(select_all_btn)

        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.clicked.connect(
            self.clear_all
        )
        button_row.addWidget(clear_all_btn)

        layout.addLayout(button_row)

        add_btn = QPushButton("Add Selected")
        add_btn.setToolTip(
            "Add the checked values to the selection."
        )
        add_btn.clicked.connect(self.accept)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def _set_all(self, state):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) is None:
                continue
            item.setCheckState(state)

    def select_all(self):
        self._set_all(Qt.CheckState.Checked)

    def clear_all(self):
        self._set_all(Qt.CheckState.Unchecked)

    def selected_by_group(self):
        result = {}
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data is None:
                continue
            if item.checkState() != Qt.CheckState.Checked:
                continue
            group, cell = data
            result.setdefault(group, []).append(cell)
        return result
