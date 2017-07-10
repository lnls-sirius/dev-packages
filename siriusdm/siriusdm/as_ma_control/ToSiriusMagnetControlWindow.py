""""""
import re
from pydm.PyQt.QtGui import QPushButton
from siriuspy.search import MASearch
from .BaseMagnetControlWindow import BaseMagnetControlWindow
from .control_widget.BaseMagnetControlWidget import BaseMagnetControlWidget
from .control_widget.SlowCorrectorControlWidget import \
    TSSlowCorrectorControlWidget
from .detail_widget.MagnetDetailWidget import MagnetDetailWidget


class ToSiriusMagnetControlWindow(BaseMagnetControlWindow):
    """Biuld control window to control the BTS magnets."""

    def __init__(self, parent=None):
        """Class constructor."""
        self._magnets = [re.sub("PS-", "MA-", x)
                         for x in MASearch.get_manames([{"section": "TS"}])]
        super(ToSiriusMagnetControlWindow, self).__init__(parent)
        self.setWindowTitle('BTS Magnet Control Panel')

    def _addTabs(self):
        self.dipo_tab = MagnetDetailWidget("TS-Fam:MA-B", self)
        self.slow_tab = TSSlowCorrectorControlWidget(
            self._magnets, BaseMagnetControlWidget.HORIZONTAL, parent=self)
        # Add Tabs
        self.tabs.addTab(self.dipo_tab, "Dipoles")
        self.tabs.addTab(self.slow_tab, "Slow Correctors")
        # Make button connections
        self._connectButtons(self.slow_tab.findChildren(QPushButton))
