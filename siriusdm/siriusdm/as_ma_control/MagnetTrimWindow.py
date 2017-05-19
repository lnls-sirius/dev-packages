import sys
import re
from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QLabel, QDialog, QGridLayout, QGroupBox, \
        QHBoxLayout, QApplication, QScrollArea, QWidget
from pydm import PyDMApplication
from pydm.widgets.label import PyDMLabel
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.led import PyDMLed
from pydm.widgets.scrollbar import PyDMScrollBar
from siriuspy.magnet import magdata

class MagnetTrimWindow(QDialog):
    STYLESHEET = """QGroupBox {font-size: 11pt; font-weight: bold;}"""

    def __init__(self, ma_name, parent=None):
        super(MagnetTrimWindow, self).__init__(parent)

        self._ma = ma_name
        self._ps = re.sub(":MA-", ":PS-", self._ma)

        self._setupUi()
        self.setStyleSheet(self.STYLESHEET)

        self.app = QApplication.instance()
        self.app.establish_widget_connections(self)

    def _setupUi(self):
        self.setWindowTitle(self._ma + ' Trims')

        self.layout = QGridLayout()

        #Magnet
        self.ma_box = QGroupBox(self._ma)

        ma_box_layout = QHBoxLayout()
        self.ma_led = PyDMLed(self, "ca://" + self._ma + ":PwrState-Sts")
        self.ma_label = QLabel(self._ma, self)
        self.ma_current_sb = PyDMScrollBar(Qt.Horizontal, self, "ca://" + self._ma + ":Current-SP")
        self.ma_current_sp = PyDMLineEdit(self, "ca://" + self._ma + ":Current-SP")
        self.ma_current_rb = PyDMLabel(self, "ca://" + self._ma + ":Current-RB")
        self.ma_kl = PyDMLineEdit(self, "ca://" + self._ma + ":KL-SP")

        ma_box_layout.addWidget(self.ma_led)
        ma_box_layout.addWidget(self.ma_label)
        ma_box_layout.addWidget(self.ma_current_sb)
        ma_box_layout.addWidget(self.ma_current_sp)
        ma_box_layout.addWidget(self.ma_current_rb)
        ma_box_layout.addWidget(self.ma_kl)

        self.ma_box.setLayout(ma_box_layout)

        #Trims
        trims = self._getTrims()

        self.trims_group_1 = QGroupBox()
        self.trims_group_2 = QGroupBox()
        self.scroll_area_1 = QScrollArea()
        self.scroll_area_2 = QScrollArea()

        self.trims_group_1.setLayout(self._createGroupBoxLayout(trims[::2]))
        self.trims_group_2.setLayout(self._createGroupBoxLayout(trims[1::2]))
        self.scroll_area_1.setWidget(self.trims_group_1)
        self.scroll_area_2.setWidget(self.trims_group_2)

        #Widgets options and signals
        self.ma_current_sb.setMinimumWidth(150)
        self.ma_current_sp.receivePrecision(3)
        self.ma_current_rb.setPrecision(3)
        self.ma_kl.receivePrecision(3)
        self.scroll_area_1.setMinimumWidth(self.trims_group_1.sizeHint().width() + \
                self.scroll_area_1.verticalScrollBar().sizeHint().width())
        self.scroll_area_2.setMinimumWidth(self.trims_group_1.sizeHint().width() + \
                self.scroll_area_2.verticalScrollBar().sizeHint().width())
        self.scroll_area_1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #Set layout
        self.layout.addWidget(self.ma_box, 0, 0)
        self.layout.addWidget(self.scroll_area_1, 1, 0)
        self.layout.addWidget(self.scroll_area_2, 1, 1)
        #Set widget layout
        self.setLayout(self.layout)

    def _createGroupBoxLayout(self, magnets):
        layout = QGridLayout()

        layout.addWidget(QLabel("Setpoint [A]", self), 0, 3)
        layout.addWidget(QLabel("Readback [A]", self), 0, 4)
        layout.addWidget(QLabel("KL Trim [1/m]", self), 0, 5)
        layout.addWidget(QLabel("KL Total [1/m]", self), 0, 6)

        for i, magnet in enumerate(magnets):
            state_led = PyDMLed(self, "ca://" + magnet + ":PwrState-Sts")
            name_label = QLabel(magnet, self)
            setpoint_sb = PyDMScrollBar(Qt.Horizontal, self, "ca://" + magnet + ":Current-SP")
            current_sp = PyDMLineEdit(self, "ca://" + magnet + ":Current-SP")
            current_rb = PyDMLabel(self, "ca://" + magnet + ":Current-RB")
            kl_trim = PyDMLineEdit(self, "ca://" + magnet + ":KLTrim-SP")
            kl_total = PyDMLabel(self, "ca://" + magnet + ":KL-RB")

            setpoint_sb.setMinimumWidth(80)
            current_sp.setMinimumWidth(80)
            current_rb.setMinimumWidth(80)
            kl_trim.setMinimumWidth(80)
            kl_total.setMinimumWidth(80)

            layout.addWidget(state_led, i + 1, 0)
            layout.addWidget(name_label, i + 1, 1)
            layout.addWidget(setpoint_sb, i + 1, 2)
            layout.addWidget(current_sp, i + 1, 3)
            layout.addWidget(current_rb, i + 1, 4)
            layout.addWidget(kl_trim, i + 1, 5)
            layout.addWidget(kl_total, i + 1, 6)

        layout.setRowStretch(len(magnets) + 1, 1)
        layout.setColumnStretch(7, 1)

        return layout



    def _getTrims(self):
        trims = list()
        ma_pattern = re.compile(re.sub("Fam", "[0-9][0-9][A-Z][0-9]",self._ma))
        for magnet in magdata.get_magps_names():
            if ma_pattern.match(magnet):
                trims.append(magnet)

        trims.sort()

        return trims

    def closeEvent(self, event):
        self.app.close_widget_connections(self)
