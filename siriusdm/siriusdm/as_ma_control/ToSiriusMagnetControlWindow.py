import re
from pydm.PyQt.QtGui import QPushButton
from siriuspy.pwrsupply import psdata
from .BaseMagnetControlWindow import BaseMagnetControlWindow
from .BaseMagnetControlWidget import BaseMagnetControlWidget
from .SlowCorrectorControlWidget import TSSlowCorrectorControlWidget
from .MagnetDetailWidget import MagnetDetailWidget

class ToSiriusMagnetControlWindow(BaseMagnetControlWindow):
    def __init__(self, parent=None):
        self._magnets = [re.sub("PS-", "MA-", x) for x in psdata.get_names() if re.match("^TS", x)]
        super(ToSiriusMagnetControlWindow, self).__init__(parent)
        self.setWindowTitle('BTS Magnet Control Panel')

    def _addTabs(self):
        orientation = BaseMagnetControlWidget.VERTICAL
        self.dipo_tab = MagnetDetailWidget("TS-Fam:MA-B", self)
        self.slow_tab = TSSlowCorrectorControlWidget(self._magnets, BaseMagnetControlWidget.HORIZONTAL, parent=self)
        #Add Tabs
        self.tabs.addTab(self.dipo_tab, "Dipoles")
        self.tabs.addTab(self.slow_tab, "Slow Correctors")
        #Make button connections
        self._connectButtons(self.slow_tab.findChildren(QPushButton))
