"""Defines window class to show trims of a magnet."""
import re
from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QLabel, QDialog, QGridLayout, QGroupBox, \
        QHBoxLayout, QApplication, QSizePolicy, QWidget, QDoubleValidator, \
        QPushButton
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.led import PyDMLed
from pydm.widgets.scrollbar import PyDMScrollBar
from siriuspy.search import MASearch
from .MagnetDetailWindow import MagnetDetailWindow


class MagnetTrimWindow(QDialog):
    """Allow controlling the trims of a given magnet."""

    STYLESHEET = """
    * {
        font-size: 16px;
    }
    .QGroupBox {
        width: 600px;
    }
    """
    # Widthes
    LEDW = 30
    NAMEW = 150
    BARW = 80
    VALUEW = 120

    def __init__(self, ma_name, parent=None):
        """Class constructor."""
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

        self.fam_magnet = QWidget()
        self.fam_magnet.layout = QHBoxLayout()

        # Fam Magnet
        self.fam_box = QGroupBox(self._ma)

        fam_box_layout = QHBoxLayout()
        self.fam_led = PyDMLed(self, "ca://" + self._ma + ":PwrState-Sts")
        self.fam_label = QLabel(self._ma, self)
        self.fam_current_sb = PyDMScrollBar(
            self, Qt.Horizontal, "ca://" + self._ma + ":Current-SP")
        self.fam_current_sp = PyDMLineEdit(
            self, "ca://" + self._ma + ":Current-SP")
        self.fam_current_rb = PyDMLabel(
            self, "ca://" + self._ma + ":Current-RB")
        self.fam_kl = PyDMLineEdit(self, "ca://" + self._ma + ":KL-SP")

        # Led config
        self.fam_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fam_led.setMinimumSize(
            self.LEDW, self.fam_led.minimumSize().height())
        # Label config
        self.fam_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fam_label.setMinimumSize(
            self.NAMEW, self.fam_label.minimumSize().height())
        # Scroll bar config
        self.fam_current_sb.setMinimumSize(self.BARW, 15)
        self.fam_current_sb.limitsFromPV = True
        self.fam_current_sb.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        # SP Line edit config
        self.fam_current_sp.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.fam_current_sp.setMinimumSize(
            self.VALUEW, self.fam_current_sp.minimumSize().height())
        self.fam_current_sp.setValidator(QDoubleValidator())
        self.fam_current_sp._useunits = False
        # RB label config
        self.fam_current_rb.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.fam_current_rb.setMinimumSize(
            self.VALUEW, self.fam_current_sp.minimumSize().height())
        # KL Line edit config
        self.fam_kl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.fam_kl.setMinimumSize(
            self.VALUEW, self.fam_kl.minimumSize().height())
        self.fam_kl.setValidator(QDoubleValidator())
        self.fam_kl._useunits = False

        self.fam_magnet.layout.addWidget(self.fam_led)
        self.fam_magnet.layout.addWidget(self.fam_label)
        self.fam_magnet.layout.addWidget(self.fam_current_sb)
        self.fam_magnet.layout.addWidget(self.fam_current_sp)
        self.fam_magnet.layout.addWidget(self.fam_current_rb)
        self.fam_magnet.layout.addWidget(self.fam_kl)

        self.fam_magnet.setLayout(self.fam_magnet.layout)
        fam_box_layout.addWidget(self.fam_magnet)
        self.fam_box.setLayout(fam_box_layout)

        # Trims
        trims = self._getTrims()
        print(trims)

        self.trims_group_1 = QGroupBox()
        self.trims_group_2 = QGroupBox()
        # self.scroll_area_1 = QScrollArea()
        # self.scroll_area_2 = QScrollArea()

        self.trims_group_1.setLayout(self._createGroupBoxLayout(trims[::2]))
        self.trims_group_2.setLayout(self._createGroupBoxLayout(trims[1::2]))
        # self.scroll_area_1.setWidget(self.trims_group_1)
        # self.scroll_area_2.setWidget(self.trims_group_2)

        # Widgets options and signals
        # self.ma_current_sb.setMinimumWidth(150)
        # self.ma_current_sp.receivePrecision(3)
        # self.ma_current_rb.setPrecision(3)
        # self.ma_kl.receivePrecision(3)
        # self.scroll_area_1.setMinimumWidth(
        #    self.trims_group_1.sizeHint().width() +
        #   self.scroll_area_1.verticalScrollBar().sizeHint().width())
        # self.scroll_area_2.setMinimumWidth(
        #    self.trims_group_1.sizeHint().width() + \
        #   self.scroll_area_2.verticalScrollBar().sizeHint().width())
        # self.scroll_area_1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.scroll_area_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set layout
        self.layout.addWidget(self.fam_box, 0, 0)
        self.layout.addWidget(self.trims_group_1, 1, 0)
        self.layout.addWidget(self.trims_group_2, 1, 1)
        # Set widget layout
        self.setLayout(self.layout)

    def _createGroupBoxLayout(self, magnets):
        layout = QGridLayout()

        layout.addWidget(QLabel("Setpoint [A]", self), 0, 3)
        layout.addWidget(QLabel("Readback [A]", self), 0, 4)
        layout.addWidget(QLabel("KL Trim [1/m]", self), 0, 5)
        layout.addWidget(QLabel("KL Total [1/m]", self), 0, 6)

        for i, magnet in enumerate(magnets):
            state_led = PyDMLed(self, "ca://" + magnet + ":PwrState-Sts")
            # name_label = QLabel(magnet, self)
            name_label = QPushButton(magnet, self)
            setpoint_sb = PyDMScrollBar(
                self, Qt.Horizontal, "ca://" + magnet + ":Current-SP")
            current_sp = PyDMLineEdit(self, "ca://" + magnet + ":Current-SP")
            current_rb = PyDMLabel(self, "ca://" + magnet + ":Current-Mon")
            kl_trim = PyDMLineEdit(self, "ca://" + magnet + ":KL-SP")
            kl_total = PyDMLabel(self, "ca://" + magnet + ":KL-Mon")

            # Led config
            state_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            state_led.setMinimumSize(
                self.LEDW, self.fam_led.minimumSize().height())
            # Label config
            name_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            name_label.setMinimumSize(
                150, self.fam_label.minimumSize().height())
            name_label.clicked.connect(lambda: self._openDetailWindow(magnet))
            # Scroll bar config
            setpoint_sb.setMinimumSize(80, 15)
            setpoint_sb.limitsFromPV = True
            setpoint_sb.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
            # SP Line edit config
            current_sp.setSizePolicy(
                QSizePolicy.Minimum, QSizePolicy.Fixed)
            current_sp.setMinimumSize(
                self.VALUEW, self.fam_current_sp.minimumSize().height())
            current_sp.setValidator(QDoubleValidator())
            current_sp._useunits = False
            # RB label config
            current_rb.setSizePolicy(
                QSizePolicy.Minimum, QSizePolicy.Fixed)
            current_rb.setMinimumSize(
                self.VALUEW, self.fam_current_sp.minimumSize().height())
            # KL Line edit config
            kl_trim.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            kl_trim.setMinimumSize(
                self.VALUEW, self.fam_kl.minimumSize().height())
            kl_trim.setValidator(QDoubleValidator())
            kl_trim._useunits = False
            # RB label config
            kl_total.setSizePolicy(
                QSizePolicy.Minimum, QSizePolicy.Fixed)
            kl_total.setMinimumSize(
                self.VALUEW, self.fam_current_sp.minimumSize().height())

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

    def _openDetailWindow(self, magnet):
        self._window = MagnetDetailWindow(magnet, self)
        self._window.exec_()

    def _getTrims(self):
        trims = list()
        ma_pattern = re.compile(re.sub("Fam", "\d{2}[A-Z]\d", self._ma))
        for magnet in MASearch.get_manames():
            if ma_pattern.match(magnet):
                trims.append(magnet)

        trims.sort()

        return trims

    def closeEvent(self, event):
        """Reimplement close event to close widget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)
