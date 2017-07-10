import re
from pydm.PyQt.QtGui import QPushButton
from siriuspy.search import MASearch
from .BaseMagnetControlWindow import BaseMagnetControlWindow
from .control_widget.BaseMagnetControlWidget import BaseMagnetControlWidget
from .control_widget.SlowCorrectorControlWidget import TBSlowCorrectorControlWidget
from .detail_widget.MagnetDetailWidget import MagnetDetailWidget

class ToBoosterMagnetControlWindow(BaseMagnetControlWindow):
    def __init__(self, parent=None):
        self._magnets = [re.sub("PS-", "MA-", x) for x in MASearch.get_manames([{"section": "TB"}])]
        super(ToBoosterMagnetControlWindow, self).__init__(parent)
        self.setWindowTitle('LTB Magnet Control Panel')

    def _addTabs(self):
        orientation = BaseMagnetControlWidget.VERTICAL
        self.dipo_tab = MagnetDetailWidget("TB-Fam:MA-B", self)
        self.slow_tab = TBSlowCorrectorControlWidget(self._magnets, BaseMagnetControlWidget.HORIZONTAL, parent=self)
        #Add Tabs
        self.tabs.addTab(self.dipo_tab, "Dipoles")
        self.tabs.addTab(self.slow_tab, "Slow Correctors")
        #Make button connections
        self._connectButtons(self.slow_tab.findChildren(QPushButton))
