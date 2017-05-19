import re
from pydm.PyQt.QtGui import QPushButton
from siriuspy.pwrsupply import psdata
from .BaseMagnetControlWindow import BaseMagnetControlWindow
from .BaseMagnetControlWidget import BaseMagnetControlWidget
from .DipoleDetailWidget import DipoleDetailWidget
from .FamQuadrupoleControlWidget import BoFamQuadrupoleControlWidget
from .FamSextupoleControlWidget import BoFamSextupoleControlWidget
from .SlowCorrectorControlWidget import BoSlowCorrectorControlWidget
from .SkewQuadControlWidget import BoSkewQuadControlWidget

class BoosterMagnetControlWindow(BaseMagnetControlWindow):
    def __init__(self, parent=None):
        self._magnets = [re.sub("PS-", "MA-", x) for x in psdata.get_names() if re.match("^BO", x)]
        super(BoosterMagnetControlWindow, self).__init__(parent)
        self.setWindowTitle('Booster Magnet Control Panel')

    def _addTabs(self):
        orientation = BaseMagnetControlWidget.VERTICAL
        self.dipo_tab = DipoleDetailWidget("BO-Fam:MA-B", self)
        self.quad_tab = BoFamQuadrupoleControlWidget(self._magnets, orientation, parent=self)
        self.sext_tab = BoFamSextupoleControlWidget(self._magnets, orientation, parent=self)
        self.slow_tab = BoSlowCorrectorControlWidget(self._magnets, BaseMagnetControlWidget.HORIZONTAL, parent=self)
        self.skew_tab = BoSkewQuadControlWidget(self._magnets, orientation, parent=self)
        #Add Tabs
        self.tabs.addTab(self.dipo_tab, "Dipoles")
        self.tabs.addTab(self.quad_tab, "Quadrupoles")
        self.tabs.addTab(self.sext_tab, "Sextupoles")
        self.tabs.addTab(self.slow_tab, "Slow Correctors")
        self.tabs.addTab(self.skew_tab, "Skew Quad")
        #Make button connections
        self._connectButtons(self.quad_tab.findChildren(QPushButton))
        self._connectButtons(self.sext_tab.findChildren(QPushButton))
        self._connectButtons(self.slow_tab.findChildren(QPushButton))
        self._connectButtons(self.skew_tab.findChildren(QPushButton))
