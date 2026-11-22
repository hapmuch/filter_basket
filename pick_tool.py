from qgis.gui import QgsMapToolIdentify

from qgis.core import (
    QgsFeatureRequest
)

from qgis.PyQt.QtCore import Qt

from .sector_dialog import SectorDialog
from .feature_picker_dialog import FeaturePickerDialog


class MRPickTool(QgsMapToolIdentify):

    def __init__(self, iface, dock):

        super().__init__(
            iface.mapCanvas()
        )

        self.iface = iface
        self.dock = dock

    def canvasReleaseEvent(self, event):


        mods = event.modifiers()

        shift_pressed = bool(
            mods & Qt.KeyboardModifier.ShiftModifier
        )

        ctrl_pressed = bool(
            mods & Qt.KeyboardModifier.ControlModifier
        )

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



        if ctrl_pressed:

            self.dock.remove_group(
                msc_value
            )

            return



        if shift_pressed:

            self.dock.add_cells(
                list(cells),
                msc_value,
                tower_field
            )

            self.dock.highlight_features(
                msc_value,
                list(cell_feature_map.values())
            )

            return



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

            self.dock.add_cells(
                selected,
                msc_value,
                tower_field
            )

            selected_features = []

            for cell in selected:

                if cell in cell_feature_map:

                    selected_features.append(
                        cell_feature_map[cell]
                    )

            self.dock.highlight_features(
                msc_value,
                selected_features
            )