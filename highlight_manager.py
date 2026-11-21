from qgis.core import QgsMessageLog
from qgis.gui import QgsRubberBand

from qgis.PyQt.QtGui import QColor


class HighlightManager:

    def __init__(self, canvas):

        self.canvas = canvas

        self.rubberbands = {}

    def _remove_item(self, item):

        try:
            self.canvas.scene().removeItem(
                item
            )
        except Exception as error:

            QgsMessageLog.logMessage(
                "Could not remove highlight: "
                f"{error}",
                "Filter Basket"
            )

    def clear(self):

        for cell_map in self.rubberbands.values():

            for rb in cell_map.values():

                self._remove_item(rb)

        self.rubberbands.clear()

    def add_feature(
        self,
        msc,
        cell,
        feature
    ):

        geom = feature.geometry()

        rb = QgsRubberBand(
            self.canvas,
            geom.type()
        )

        rb.setColor(
            QColor(0, 255, 255)
        )

        rb.setWidth(3)

        rb.setToGeometry(
            geom,
            None
        )

        existing = self.rubberbands.get(
            msc,
            {}
        ).get(cell)

        if existing is not None:

            self._remove_item(existing)

        self.rubberbands.setdefault(
            msc,
            {}
        )[cell] = rb

    def remove_msc(
        self,
        msc
    ):

        if msc not in self.rubberbands:
            return

        for rb in self.rubberbands[msc].values():

            self._remove_item(rb)

        del self.rubberbands[msc]

    def remove_cell(
        self,
        cell
    ):

        for msc in list(
            self.rubberbands.keys()
        ):

            if cell not in self.rubberbands[msc]:
                continue

            rb = self.rubberbands[msc][cell]

            self._remove_item(rb)

            del self.rubberbands[msc][cell]

            if not self.rubberbands[msc]:

                del self.rubberbands[msc]