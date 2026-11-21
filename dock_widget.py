from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QFrame,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QMenu,
    QScrollArea,
    QMessageBox
)

from qgis.core import (
    QgsProject,
    QgsSettings,
    QgsVectorLayer
)
from .pick_tool import MRPickTool
from .highlight_manager import HighlightManager
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtCore import (
    Qt,
    QEvent,
    QVariant
)


class MRFilterDock(QDockWidget):

    HEADER_ROLE = int(Qt.ItemDataRole.UserRole)
    GROUP_ROLE = int(Qt.ItemDataRole.UserRole) + 1

    def __init__(self, iface):

        super().__init__("Filter Basket")

        self.iface = iface

        self.settings = QgsSettings()

        self.selected_cells = set()

        self.selected_by_group = {}

        self.group_fields = {}

        self.pick_tool = None

        self.highlight_manager = HighlightManager(
            iface.mapCanvas()
        )

        self.build_ui()

        self.load_layers()

        self.restore_settings()

    # -----------------------------------------------------

    def build_ui(self):

        widget = QWidget()

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("Source Layer")
        )

        self.source_layer_combo = QComboBox()

        self.source_layer_combo.setToolTip(
            "Layer to pick features from."
        )

        layout.addWidget(
            self.source_layer_combo
        )

        layout.addWidget(
            QLabel("Target Layer")
        )

        self.mr_layer_combo = QComboBox()

        self.mr_layer_combo.setToolTip(
            "Layer to be filtered using the selected values."
        )

        layout.addWidget(
            self.mr_layer_combo
        )

        layout.addWidget(
            QLabel("Group Field")
        )

        self.tower_field_combo = QComboBox()

        self.tower_field_combo.setToolTip(
            "Source field whose value groups features together, "
            "for example a Site ID or Group id."
        )

        layout.addWidget(
            self.tower_field_combo
        )

        layout.addWidget(
            QLabel("Source Field")
        )

        self.source_cell_field_combo = QComboBox()

        self.source_cell_field_combo.setToolTip(
            "Source field that identifies each value to collect "
            "from the source layer."
        )

        layout.addWidget(
            self.source_cell_field_combo
        )

        layout.addWidget(
            QLabel("Target Field")
        )

        self.mr_cell_field_combo = QComboBox()

        self.mr_cell_field_combo.setToolTip(
            "Target field to filter on. Rows whose value matches a "
            "selected value are shown."
        )

        layout.addWidget(
            self.mr_cell_field_combo
        )

        self.activate_btn = QPushButton(
            "Activate Pick Tool"
        )

        self.activate_btn.setToolTip(
            "Click a source feature on the map to pick values. "
            "Shift-click adds the whole group, Ctrl-click removes "
            "the whole group."
        )

        layout.addWidget(
            self.activate_btn
        )

        action_row = QHBoxLayout()

        self.reload_btn = QPushButton(
            "Reload Layers"
        )

        self.reload_btn.setToolTip(
            "Refresh the layer list from the current QGIS project. "
            "Current layer and field selections are kept when "
            "possible."
        )

        action_row.addWidget(
            self.reload_btn
        )

        self.help_btn = QPushButton(
            "Help"
        )

        self.help_btn.setToolTip(
            "Show a short description of how this plugin works."
        )

        action_row.addWidget(
            self.help_btn
        )

        layout.addLayout(
            action_row
        )

        layout.addWidget(
            QLabel("Selected Target")
        )

        self.cell_list = QListWidget()

        self.cell_list.setToolTip(
            "Values used to filter the target layer, grouped by the "
            "Group Field. Press Delete or right-click a value to "
            "remove it; right-click a group header to remove the "
            "whole group."
        )

        self.cell_list.setMinimumHeight(
            100
        )

        layout.addWidget(
            self.cell_list
        )

        self.clear_btn = QPushButton(
            "Clear All"
        )

        self.clear_btn.setToolTip(
            "Clear all selected values, remove the target layer "
            "filter and delete the highlights."
        )

        layout.addWidget(
            self.clear_btn
        )

        widget.setLayout(layout)

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(True)

        scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll_area.setWidget(widget)

        self.setWidget(scroll_area)

        self.source_layer_combo.currentIndexChanged.connect(
            self.refresh_source_fields
        )

        self.mr_layer_combo.currentIndexChanged.connect(
            self.refresh_mr_fields
        )

        self.mr_layer_combo.currentIndexChanged.connect(
            self.apply_filter
        )

        self.mr_cell_field_combo.currentIndexChanged.connect(
            self.apply_filter
        )

        self.clear_btn.clicked.connect(
            self.clear_all
        )

        self.cell_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.cell_list.customContextMenuRequested.connect(
            self.show_context_menu
        )
        self.activate_btn.clicked.connect(
            self.activate_pick_tool 
        )

        self.reload_btn.clicked.connect(
            self.reload_layers
        )

        self.help_btn.clicked.connect(
            self.show_help
        )

        self.cell_list.installEventFilter(self)
        
    def activate_pick_tool(self):

        self.pick_tool = MRPickTool(
            self.iface,
            self
        )

        self.iface.mapCanvas().setMapTool(
            self.pick_tool
        )
        
    def highlight_features(
        self,
        msc,
        feature_map
    ):

        source_cell_field = (
            self.source_cell_field_combo.currentText()
        )

        for feature in feature_map:

            cell = str(
                feature[source_cell_field]
            )

            self.highlight_manager.add_feature(
                msc,
                cell,
                feature
            )

    # -----------------------------------------------------

    def load_layers(self):

        self.source_layer_combo.clear()
        self.mr_layer_combo.clear()

        for layer in QgsProject.instance().mapLayers().values():

            if not isinstance(layer, QgsVectorLayer):
                continue

            self.source_layer_combo.addItem(
                layer.name()
            )

            self.mr_layer_combo.addItem(
                layer.name()
            )

        self.refresh_source_fields()
        self.refresh_mr_fields()

    # -----------------------------------------------------

    def reload_layers(self):

        source_layer = self.source_layer_combo.currentText()
        mr_layer = self.mr_layer_combo.currentText()
        tower_field = self.tower_field_combo.currentText()
        source_cell_field = self.source_cell_field_combo.currentText()
        mr_cell_field = self.mr_cell_field_combo.currentText()

        self.load_layers()

        self.source_layer_combo.blockSignals(True)
        self.mr_layer_combo.blockSignals(True)

        idx = self.source_layer_combo.findText(
            source_layer
        )

        if idx >= 0:
            self.source_layer_combo.setCurrentIndex(idx)

        idx = self.mr_layer_combo.findText(
            mr_layer
        )

        if idx >= 0:
            self.mr_layer_combo.setCurrentIndex(idx)

        self.source_layer_combo.blockSignals(False)
        self.mr_layer_combo.blockSignals(False)

        self.refresh_source_fields()
        self.refresh_mr_fields()

        idx = self.tower_field_combo.findText(
            tower_field
        )

        if idx >= 0:
            self.tower_field_combo.setCurrentIndex(idx)

        idx = self.source_cell_field_combo.findText(
            source_cell_field
        )

        if idx >= 0:
            self.source_cell_field_combo.setCurrentIndex(idx)

        idx = self.mr_cell_field_combo.findText(
            mr_cell_field
        )

        if idx >= 0:
            self.mr_cell_field_combo.setCurrentIndex(idx)

    # -----------------------------------------------------

    def show_help(self):

        QMessageBox.information(
            self,
            "Filter Basket - Help",
            (
                "Filter a target layer using values picked from a "
                "source layer.\n\n"
                "1. Choose the Source Layer and the Target Layer.\n"
                "2. Choose the Group Field (groups source features), "
                "the Source Field (value to collect) and the Target "
                "Field (field to filter).\n"
                "3. Click 'Activate Pick Tool', then click a feature "
                "on the map and tick the values to add.\n\n"
                "Shift-click: add every value in the same group.\n"
                "Ctrl-click: remove every value in the same group.\n"
                "Right-click or Delete in the list: remove one value.\n"
                "'Clear All': reset the selection, filter and "
                "highlights.\n\n"
                "Use 'Reload Layers' after adding layers in QGIS."
            )
        )

    # -----------------------------------------------------

    def get_source_layer(self):

        name = self.source_layer_combo.currentText()

        layers = QgsProject.instance().mapLayersByName(
            name
        )

        return layers[0] if layers else None

    # -----------------------------------------------------

    def get_mr_layer(self):

        name = self.mr_layer_combo.currentText()

        layers = QgsProject.instance().mapLayersByName(
            name
        )

        return layers[0] if layers else None

    # -----------------------------------------------------

    def refresh_source_fields(self):

        self.tower_field_combo.clear()

        self.source_cell_field_combo.clear()

        layer = self.get_source_layer()

        if not layer:
            return

        for field in layer.fields():

            self.tower_field_combo.addItem(
                field.name()
            )

            self.source_cell_field_combo.addItem(
                field.name()
            )

    # -----------------------------------------------------

    def refresh_mr_fields(self):

        self.mr_cell_field_combo.clear()

        layer = self.get_mr_layer()

        if not layer:
            return

        for field in layer.fields():

            self.mr_cell_field_combo.addItem(
                field.name()
            )

    # -----------------------------------------------------

    def sync_selected_cells(self):

        self.selected_cells = set()

        for cells in self.selected_by_group.values():

            self.selected_cells.update(
                cells
            )

    # -----------------------------------------------------

    def add_cells(self, cells, group, group_field):

        cells = set(cells)

        if not cells:
            return

        group_values = self.selected_by_group.setdefault(
            group,
            set()
        )

        group_values.update(cells)

        self.group_fields[group] = group_field

        self.sync_selected_cells()

        self.refresh_cell_list()

        self.apply_filter()

    # -----------------------------------------------------

    def remove_value(self, value):

        for group in list(
            self.selected_by_group.keys()
        ):

            self.selected_by_group[group].discard(
                value
            )

            if not self.selected_by_group[group]:

                del self.selected_by_group[group]

                self.group_fields.pop(
                    group,
                    None
                )

        self.sync_selected_cells()

        self.highlight_manager.remove_cell(
            value
        )

        self.refresh_cell_list()

        self.apply_filter()

    # -----------------------------------------------------

    def remove_group(self, group):

        if group not in self.selected_by_group:
            return

        del self.selected_by_group[group]

        self.group_fields.pop(
            group,
            None
        )

        self.sync_selected_cells()

        self.remove_highlight_for_msc(
            group
        )

        self.refresh_cell_list()

        self.apply_filter()

    # -----------------------------------------------------

    def refresh_cell_list(self):

        self.cell_list.clear()

        bold_font = QFont(
            self.cell_list.font()
        )

        bold_font.setBold(True)

        for group in sorted(
            self.selected_by_group
        ):

            field_name = self.group_fields.get(
                group,
                "Group Field"
            )

            header = QListWidgetItem(
                f"Group ({field_name}): {group}"
            )

            header.setFlags(
                Qt.ItemFlag.ItemIsEnabled
            )

            header.setFont(
                bold_font
            )

            header.setData(
                self.HEADER_ROLE,
                True
            )

            header.setData(
                self.GROUP_ROLE,
                group
            )

            self.cell_list.addItem(
                header
            )

            for cell in sorted(
                self.selected_by_group[group]
            ):

                item = QListWidgetItem(
                    cell
                )

                item.setData(
                    self.GROUP_ROLE,
                    group
                )

                self.cell_list.addItem(
                    item
                )

    # -----------------------------------------------------

    def apply_filter(self):

        mr_layer = self.get_mr_layer()

        if not mr_layer:
            return

        if not self.selected_cells:

            mr_layer.setSubsetString("")

            mr_layer.triggerRepaint()

            return

        field_name = (
            self.mr_cell_field_combo.currentText()
        )

        if not field_name:

            mr_layer.setSubsetString("")

            mr_layer.triggerRepaint()

            return

        field_index = mr_layer.fields().indexFromName(
            field_name
        )

        field = (
            mr_layer.fields().field(field_index)
            if field_index >= 0
            else None
        )

        field_type = (
            field.type() if field else QVariant.String
        )

        numeric_types = (
            QVariant.Int,
            QVariant.UInt,
            QVariant.LongLong,
            QVariant.ULongLong,
            QVariant.Double
        )

        def format_value(value):

            text = str(value)

            if field_type == QVariant.Bool:

                return (
                    "TRUE"
                    if text.strip().lower() in ("true", "1")
                    else "FALSE"
                )

            if field_type in numeric_types:

                try:
                    float(text)
                except ValueError:
                    return "NULL"

                return text

            return "'" + text.replace("'", "''") + "'"

        values = ",".join(
            format_value(c)
            for c in self.selected_cells
        )

        escaped_field = field_name.replace(
            '"',
            '""'
        )

        expression = (
            f'"{escaped_field}" IN ({values})'
        )

        mr_layer.setSubsetString(
            expression
        )

        mr_layer.triggerRepaint()

    # -----------------------------------------------------

    def clear_all(self):

        self.selected_cells.clear()

        self.selected_by_group.clear()

        self.group_fields.clear()

        self.refresh_cell_list()

        self.apply_filter()

        self.highlight_manager.clear()

    # -----------------------------------------------------

    def show_context_menu(self, pos):

        item = self.cell_list.itemAt(pos)

        if not item:
            return

        is_header = bool(
            item.data(self.HEADER_ROLE)
        )

        menu = QMenu()

        if is_header:
            remove_action = menu.addAction(
                "Remove group"
            )
        else:
            remove_action = menu.addAction(
                "Remove"
            )

        action = menu.exec(
            self.cell_list.mapToGlobal(pos)
        )

        if action != remove_action:
            return

        if is_header:
            self.remove_group(
                item.data(self.GROUP_ROLE)
            )
        else:
            self.remove_value(
                item.text()
            )

    # -----------------------------------------------------

    def save_settings(self):

        self.settings.setValue(
            "MRFilter/source_layer",
            self.source_layer_combo.currentText()
        )

        self.settings.setValue(
            "MRFilter/mr_layer",
            self.mr_layer_combo.currentText()
        )

        self.settings.setValue(
            "MRFilter/tower_field",
            self.tower_field_combo.currentText()
        )

        self.settings.setValue(
            "MRFilter/source_cell_field",
            self.source_cell_field_combo.currentText()
        )

        self.settings.setValue(
            "MRFilter/mr_cell_field",
            self.mr_cell_field_combo.currentText()
        )

    # -----------------------------------------------------

    def restore_settings(self):

        source_layer = self.settings.value(
            "MRFilter/source_layer",
            ""
        )

        mr_layer = self.settings.value(
            "MRFilter/mr_layer",
            ""
        )

        tower_field = self.settings.value(
            "MRFilter/tower_field",
            ""
        )

        source_cell_field = self.settings.value(
            "MRFilter/source_cell_field",
            ""
        )

        mr_cell_field = self.settings.value(
            "MRFilter/mr_cell_field",
            ""
        )

        idx = self.source_layer_combo.findText(
            source_layer
        )

        if idx >= 0:
            self.source_layer_combo.setCurrentIndex(
                idx
            )

        idx = self.mr_layer_combo.findText(
            mr_layer
        )

        if idx >= 0:
            self.mr_layer_combo.setCurrentIndex(
                idx
            )

        self.refresh_source_fields()
        self.refresh_mr_fields()

        idx = self.tower_field_combo.findText(
            tower_field
        )

        if idx >= 0:
            self.tower_field_combo.setCurrentIndex(
                idx
            )

        idx = self.source_cell_field_combo.findText(
            source_cell_field
        )

        if idx >= 0:
            self.source_cell_field_combo.setCurrentIndex(
                idx
            )

        idx = self.mr_cell_field_combo.findText(
            mr_cell_field
        )

        if idx >= 0:
            self.mr_cell_field_combo.setCurrentIndex(
                idx
            )
    def eventFilter(self, obj, event):

        if obj == self.cell_list:

            if event.type() == QEvent.Type.KeyPress:

                if event.key() == Qt.Key.Key_Delete:

                    item = self.cell_list.currentItem()

                    if item and not item.data(
                        self.HEADER_ROLE
                    ):

                        self.remove_value(
                            item.text()
                        )

                    return True

        return super().eventFilter(
            obj,
            event
        )



    def remove_highlight_for_msc(
        self,
        msc
    ):

        self.highlight_manager.remove_msc(
            msc
        )
    # -----------------------------------------------------

    def closeEvent(self, event):

        self.save_settings()

        super().closeEvent(event)