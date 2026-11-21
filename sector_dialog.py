from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton
)

from qgis.PyQt.QtCore import Qt


class SectorDialog(QDialog):

    def __init__(
        self,
        msc_value,
        cells,
        preselected_cells=None,
        parent=None
    ):

        super().__init__(parent)
        if preselected_cells is None:
            preselected_cells = []

        self.setWindowTitle(
            f"Group: {msc_value}"
        )

        layout = QVBoxLayout()

        self.list_widget = QListWidget()

        for cell in sorted(cells):

            item = QListWidgetItem(cell)

            item.setFlags(
                item.flags() |
                Qt.ItemFlag.ItemIsUserCheckable
            )

            if cell in preselected_cells:

                item.setCheckState(
                    Qt.CheckState.Checked
                )

            else:

                item.setCheckState(
                    Qt.CheckState.Unchecked
                )

            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        btn = QPushButton("Add Selected")

        btn.setToolTip(
            "Add the checked values to the selection."
        )

        btn.clicked.connect(self.accept)

        layout.addWidget(btn)

        self.setLayout(layout)

    def selected_cells(self):

        result = []

        for i in range(
            self.list_widget.count()
        ):

            item = self.list_widget.item(i)

            if item.checkState() == Qt.CheckState.Checked:

                result.append(
                    item.text()
                )

        return result