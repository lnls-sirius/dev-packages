import re
from pydm.PyQt.QtGui import QPushButton
from siriuspy.search import MASearch
from .BaseMagnetControlWindow import BaseMagnetControlWindow
from .detail_widget.DipoleDetailWidget import DipoleDetailWidget
from .control_widget.FamQuadrupoleControlWidget import SiFamQuadrupoleControlWidget
from .control_widget.FamSextupoleControlWidget import SiFamSextupoleControlWidget
from .control_widget.SlowCorrectorControlWidget import SiSlowCorrectorControlWidget
from .control_widget.FastCorrectorControlWidget import SiFastCorrectorControlWidget
from .control_widget.SkewQuadControlWidget import SiSkewQuadControlWidget

class SiriusMagnetControlWindow(BaseMagnetControlWindow):
    def __init__(self, parent=None):
        self._magnets = [re.sub("PS-", "MA-", x) for x in MASearch.get_manames([{"section": "SI"}])]
        super(SiriusMagnetControlWindow, self).__init__(parent)
        self.setWindowTitle('Sirius Magnet Control Panel')

    def _addTabs(self):
        self.dipo_tab = DipoleDetailWidget("SI-Fam:MA-B1B2", self)
        self.quad_tab = SiFamQuadrupoleControlWidget(self._magnets, parent=self)
        self.sext_tab = SiFamSextupoleControlWidget(self._magnets, parent=self)
        self.slow_tab = SiSlowCorrectorControlWidget(self._magnets, parent=self)
        self.fast_tab = SiFastCorrectorControlWidget(self._magnets, parent=self)
        self.skew_tab = SiSkewQuadControlWidget(self._magnets, parent=self)
        #Add Tabs
        self.tabs.addTab(self.dipo_tab, "Dipoles")
        self.tabs.addTab(self.quad_tab, "Quadrupoles")
        self.tabs.addTab(self.sext_tab, "Sextupoles")
        self.tabs.addTab(self.slow_tab, "Slow Correctors")
        self.tabs.addTab(self.fast_tab, "Fast Correctors")
        self.tabs.addTab(self.skew_tab, "Skew Quad")
        #Make button connections
        self._connectButtons(self.quad_tab.findChildren(QPushButton))
        self._connectButtons(self.sext_tab.findChildren(QPushButton))
        self._connectButtons(self.slow_tab.findChildren(QPushButton))
        self._connectButtons(self.fast_tab.findChildren(QPushButton))
        self._connectButtons(self.skew_tab.findChildren(QPushButton))
