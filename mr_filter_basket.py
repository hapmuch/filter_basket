import os

from qgis.PyQt.QtGui import QAction, QIcon
from qgis.PyQt.QtCore import Qt

from .dock_widget import MRFilterDock


PLUGIN_DIR = os.path.dirname(__file__)


class MRFilterBasketPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dock = None

    def initGui(self):

        self.action = QAction(
            QIcon(
                os.path.join(
                    PLUGIN_DIR,
                    "filter_basket.svg"
                )
            ),
            "Filter Basket",
            self.iface.mainWindow()
        )

        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)

        self.iface.addPluginToMenu(
            "&Filter Basket",
            self.action
        )

    def unload(self):

        if self.action:

            self.iface.removeToolBarIcon(
                self.action
            )

            self.iface.removePluginMenu(
                "&Filter Basket",
                self.action
            )

        if self.dock:

            self.dock.save_settings()

            self.dock.highlight_manager.clear()

            if self.dock.pick_tool is not None:

                self.iface.mapCanvas().unsetMapTool(
                    self.dock.pick_tool
                )

                self.dock.pick_tool = None

            self.iface.removeDockWidget(
                self.dock
            )

            self.dock = None

        self.action = None

    def run(self):

        if self.dock is None:

            self.dock = MRFilterDock(
                self.iface
            )

            self.iface.addDockWidget(
                Qt.DockWidgetArea.RightDockWidgetArea,
                self.dock
            )

        self.dock.show()