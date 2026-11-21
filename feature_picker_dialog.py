from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QPushButton
)


class FeaturePickerDialog(QDialog):

    def __init__(
        self,
        features,
        cell_field,
        parent=None
    ):

        super().__init__(parent)

        self.features = features

        self.setWindowTitle(
            "Select Source Value"
        )

        layout = QVBoxLayout()

        self.list_widget = QListWidget()

        for feature in features:

            self.list_widget.addItem(
                str(feature[cell_field])
            )

        layout.addWidget(
            self.list_widget
        )

        btn = QPushButton("OK")

        btn.setToolTip(
            "Confirm the highlighted cell."
        )

        btn.clicked.connect(
            self.accept
        )

        layout.addWidget(btn)

        self.setLayout(layout)

    def selected_feature(self):

        row = self.list_widget.currentRow()

        if row < 0:
            return None

        return self.features[row]