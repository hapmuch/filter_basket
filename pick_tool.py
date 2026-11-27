from qgis.gui import QgsMapToolIdentify, QgsRubberBand

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProject,
    QgsRectangle,
    QgsWkbTypes,
)

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox

from .sector_dialog import SectorDialog
from .feature_picker_dialog import FeaturePickerDialog
from .multi_group_dialog import MultiGroupDialog


class MRPickTool(QgsMapToolIdentify):

    DRAG_THRESHOLD_PX = 5

    def __init__(self, iface, dock):

        super().__init__(
            iface.mapCanvas()
        )

        self.iface = iface
        self.dock = dock
        self._start_pos = None
        self._rubber_band = None
        self._dragging = False

    def canvasPressEvent(self, event):

        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._start_pos = event.pos()
        self._dragging = False
        self._clear_rubber_band()

    def canvasMoveEvent(self, event):

        if self._start_pos is None:
            return

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        delta = event.pos() - self._start_pos
        if (not self._dragging and
                delta.manhattanLength() <= self.DRAG_THRESHOLD_PX):
            return

        self._dragging = True
        self._update_rubber_band(event.pos())

    def canvasReleaseEvent(self, event):

        if event.button() != Qt.MouseButton.LeftButton:
            return

        was_dragging = self._dragging
        start_pos = self._start_pos
        self._start_pos = None
        self._dragging = False
        self._clear_rubber_band()

        if was_dragging and start_pos is not None:
            self._handle_rectangle(start_pos, event.pos())
            return

        self._handle_click(event)

    def deactivate(self):

        self._clear_rubber_band()
        self._start_pos = None
        self._dragging = False
        super().deactivate()

    def _clear_rubber_band(self):

        if self._rubber_band is None:
            return

        self.canvas().scene().removeItem(
            self._rubber_band
        )
        self._rubber_band = None

    def _update_rubber_band(self, current_pos):

        start = self.toMapCoordinates(self._start_pos)
        end = self.toMapCoordinates(current_pos)
        rect = QgsRectangle(start, end)

        if self._rubber_band is None:
            self._rubber_band = QgsRubberBand(
                self.canvas(),
                QgsWkbTypes.PolygonGeometry
            )
            self._rubber_band.setColor(
                QColor(224, 123, 57, 80)
            )
            self._rubber_band.setStrokeColor(
                QColor(224, 123, 57)
            )
            self._rubber_band.setWidth(2)

        geom = QgsGeometry.fromRect(rect)
        self._rubber_band.setToGeometry(geom, None)

    def _handle_rectangle(self, start_pos, end_pos):

        layer = self.dock.get_source_layer()

        if not layer:
            return

        tower_field = (
            self.dock.tower_field_combo.currentText()
        )

        cell_field = (
            self.dock.source_cell_field_combo.currentText()
        )

        start = self.toMapCoordinates(start_pos)
        end = self.toMapCoordinates(end_pos)
        rect = QgsRectangle(start, end)

        project = QgsProject.instance()
        layer_rect = QgsRectangle(rect)
        if project is not None:
            ct = QgsCoordinateTransform(
                project.crs(),
                layer.crs(),
                project
            )
            try:
                layer_rect = ct.transformBoundingBox(rect)
            except Exception:
                layer_rect = QgsRectangle(rect)

        request = QgsFeatureRequest().setFilterRect(layer_rect)

        rect_geom = QgsGeometry.fromRect(layer_rect)
        groups = {}
        group_features = {}

        for feature in layer.getFeatures(request):
            geom = feature.geometry()
            if geom is None or geom.isEmpty():
                continue
            if not geom.intersects(rect_geom):
                continue

            group_value = str(feature[tower_field])
            cell_value = str(feature[cell_field])

            if not group_value or not cell_value:
                continue

            groups.setdefault(group_value, set()).add(cell_value)
            group_features.setdefault(group_value, {})
            group_features[group_value].setdefault(
                cell_value,
                feature
            )

        if not groups:
            return

        dlg = MultiGroupDialog(
            groups,
            tower_field
        )

        if not dlg.exec():
            return

        selected_by_group = dlg.selected_by_group()

        if not selected_by_group:
            return

        total_picked = 0
        total_visible = 0

        for group_value, selected_cells in selected_by_group.items():
            if not selected_cells:
                continue

            added = self.dock.add_cells(
                selected_cells,
                group_value,
                tower_field
            )

            if not added:
                return

            visible_cells = self.dock.selected_by_group.get(
                group_value, set()
            )
            selected_features = []
            for cell in selected_cells:
                if cell not in visible_cells:
                    continue
                total_visible += 1
                feature = group_features.get(
                    group_value, {}
                ).get(cell)
                if feature is not None:
                    selected_features.append(feature)

            total_picked += len(selected_cells)

            if selected_features:
                self.dock.highlight_features(
                    group_value,
                    selected_features
                )

        if (
            self.dock._temp_filter_is_active()
            and total_picked > 0
            and total_visible == 0
        ):
            QMessageBox.information(
                self.dock,
                "Filter Basket",
                "Selected values were added to the full list, "
                "but all are hidden by the active Preview Filter."
            )

    def _handle_click(self, event):

        layer = self.dock.get_source_layer()

        if not layer:
            return

        results = self.identify(
            event.x(),
            event.y(),
            [layer],
            QgsMapToolIdentify.IdentifyMode.TopDownAll
        )

        if not results:
            return

        features_under_cursor = [
            r.mFeature
            for r in results
        ]

        tower_field = (
            self.dock.tower_field_combo.currentText()
        )

        cell_field = (
            self.dock.source_cell_field_combo.currentText()
        )

        if len(features_under_cursor) == 1:

            feature = features_under_cursor[0]

        else:

            dlg = FeaturePickerDialog(
                features_under_cursor,
                cell_field
            )

            if not dlg.exec():
                return

            feature = dlg.selected_feature()

            if feature is None:
                return

        msc_value = str(
            feature[tower_field]
        )

        # ---------------------------------
        # Find all cells under same MSC
        # ---------------------------------

        escaped_field = tower_field.replace(
            '"',
            '""'
        )

        escaped_value = msc_value.replace(
            "'",
            "''"
        )

        expr = (
            f'"{escaped_field}" = '
            f"'{escaped_value}'"
        )

        request = QgsFeatureRequest()

        request.setFilterExpression(
            expr
        )

        cells = set()

        cell_feature_map = {}

        for f in layer.getFeatures(request):

            cell = str(
                f[cell_field]
            )

            if not cell:
                continue

            cells.add(cell)

            cell_feature_map[cell] = f

        preselected_cells = []

        for f in features_under_cursor:

            preselected_cells.append(
                str(f[cell_field])
            )

        dlg = SectorDialog(
            msc_value,
            cells,
            preselected_cells
        )

        if dlg.exec():

            selected = (
                dlg.selected_cells()
            )

            if not selected:
                return

            added = self.dock.add_cells(
                selected,
                msc_value,
                tower_field
            )

            if not added:
                return

            visible_cells = self.dock.selected_by_group.get(
                msc_value, set()
            )
            selected_features = []
            total_visible = 0

            for cell in selected:

                if cell not in visible_cells:
                    continue

                total_visible += 1

                if cell in cell_feature_map:

                    selected_features.append(
                        cell_feature_map[cell]
                    )

            if selected_features:
                self.dock.highlight_features(
                    msc_value,
                    selected_features
                )

            if (
                self.dock._temp_filter_is_active()
                and len(selected) > 0
                and total_visible == 0
            ):
                QMessageBox.information(
                    self.dock,
                    "Filter Basket",
                    "Selected values were added to the full list, "
                    "but all are hidden by the active Preview Filter."
                )
