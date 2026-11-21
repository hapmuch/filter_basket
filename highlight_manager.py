from qgis.gui import QgsRubberBand

from qgis.PyQt.QtGui import QColor


class HighlightManager:

    def __init__(self, canvas):

        self.canvas = canvas

        self.rubberbands = {}

    def clear(self):

        for cell_map in self.rubberbands.values():

            for rb in cell_map.values():

                try:
                    self.canvas.scene().removeItem(rb)
                except Exception:
                    pass

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

            try:
                self.canvas.scene().removeItem(existing)
            except Exception:
                pass

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

            try:
                self.canvas.scene().removeItem(rb)
            except Exception:
                pass

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

            try:
                self.canvas.scene().removeItem(rb)
            except Exception:
                pass

            del self.rubberbands[msc][cell]

            if not self.rubberbands[msc]:

                del self.rubberbands[msc]