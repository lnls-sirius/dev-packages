""""""
import re
from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, \
    QSizePolicy
from pydm.widgets.label import PyDMLabel
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.led import PyDMLed
from pydm.widgets.scrollbar import PyDMScrollBar
from .MagnetDetailWidget import MagnetDetailWidget


class DipoleDetailWidget(MagnetDetailWidget):
    """Widget that allows controlling a dipole magnet."""

    def __init__(self, magnet_name, parent=None):
        """Class constructor."""
        if re.match("(SI|BO)-Fam:MA-B\w*", magnet_name):
            self._magnet_name = magnet_name
        else:
            raise ValueError("Magnet not supported by this class!")

        self._vaca_prefix = "VAG-"
        ps_name = self._vaca_prefix + re.sub(":MA", ":PS", self._magnet_name)
        self._ps_list = [ps_name + "-1",
                         ps_name + "-2"]

        super(DipoleDetailWidget, self).__init__(self._magnet_name, parent)

    def _interlockLayout(self):
        layout = QGridLayout()
        layout.addWidget(QLabel("PS1"), 0, 0)
        layout.addWidget(QLabel("PS2"), 0, 1)
        for col, ps in enumerate(self._ps_list):
            for i in range(16):
                led = PyDMLed(self, "ca://" + ps + ":Intlk-Mon", i)
                led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
                layout.addWidget(led, i + 1, col)
                layout.addWidget(QLabel("Bit " + str(i)), i + 1, 3)
        layout.setRowStretch(17, 1)

        return layout

    def _opModeLayout(self):
        layout = QGridLayout()

        self.opmode_sp = PyDMEnumComboBox(
            self, init_channel="ca://" + self._magnet_name + ":OpMode-Sel")
        self.opmode1_rb = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":OpMode-Sts")
        self.ctrlmode1_led = PyDMLed(
            self, "ca://" + self._ps_list[0] + ":CtrlMode-Mon")
        self.ctrlmode1_label = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":CtrlMode-Mon")
        self.opmode2_rb = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":OpMode-Sts")
        self.ctrlmode2_led = PyDMLed(
            self, "ca://" + self._ps_list[1] + ":CtrlMode-Mon")
        self.ctrlmode2_label = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":CtrlMode-Mon")

        self.ctrlmode1_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.ctrlmode2_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)

        ps1_layout = QGridLayout()
        ps1_layout.addWidget(QLabel("PS1"), 0, 0, 1, 2)
        ps1_layout.addWidget(self.opmode1_rb, 1, 0, 1, 2)
        ps1_layout.addWidget(self.ctrlmode1_led, 2, 0)
        ps1_layout.addWidget(self.ctrlmode1_label, 2, 1)

        ps2_layout = QGridLayout()
        ps2_layout.addWidget(QLabel("PS2"), 0, 0, 1, 2)
        ps2_layout.addWidget(self.opmode2_rb, 1, 0, 1, 2)
        ps2_layout.addWidget(self.ctrlmode2_led, 2, 0)
        ps2_layout.addWidget(self.ctrlmode2_label, 2, 1)

        layout.addWidget(self.opmode_sp, 0, 0, 1, 2)
        layout.addLayout(ps1_layout, 1, 0)
        layout.addLayout(ps2_layout, 1, 1)

        return layout

    def _powerStateLayout(self):
        layout = QVBoxLayout()

        self.on_btn = PyDMPushButton(
            self, label="On", pressValue=1,
            init_channel="ca://" + self._magnet_name + ":PwrState-Sel")
        self.off_btn = PyDMPushButton(
            self, label="Off", pressValue=0,
            init_channel="ca://" + self._magnet_name + ":PwrState-Sel")

        self.pwrstate1_led = PyDMLed(
            self, "ca://" + self._ps_list[0] + ":PwrState-Sts")
        self.pwrstate1_label = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":PwrState-Sts")
        self.pwrstate2_led = PyDMLed(
            self, "ca://" + self._ps_list[1] + ":PwrState-Sts")
        self.pwrstate2_label = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":PwrState-Sts")

        self.pwrstate1_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.pwrstate2_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.on_btn)
        buttons_layout.addWidget(self.off_btn)
        pwrstatus_layout = QGridLayout()
        pwrstatus_layout.addWidget(QLabel("PS1"), 0, 0, 1, 2)
        pwrstatus_layout.addWidget(QLabel("PS2"), 0, 2, 1, 2)
        pwrstatus_layout.addWidget(self.pwrstate1_led, 1, 0)
        pwrstatus_layout.addWidget(self.pwrstate1_label, 1, 1)
        pwrstatus_layout.addWidget(self.pwrstate2_led, 1, 2)
        pwrstatus_layout.addWidget(self.pwrstate2_label, 1, 3)

        layout.addLayout(buttons_layout)
        layout.addLayout(pwrstatus_layout)

        return layout

    def _currentLayout(self):
        layout = QGridLayout()

        self.current_rb_label = QLabel("Readback")
        self.current_sp_label = QLabel("Setpoint")

        self.current_rb_val = PyDMLabel(
            self, "ca://" + self._magnet_name + ":Current-RB")
        # self.current_rb_val.setPrecision(3)

        self.current_sp_val = PyDMLineEdit(
            self, "ca://" + self._magnet_name + ":Current-SP")
        # self.current_sp_val.receivePrecision(3)

        self.current_sp_slider = PyDMScrollBar(
            self, Qt.Horizontal, "ca://" + self._magnet_name + ":Current-SP")
        self.current_sp_slider.setObjectName("current-sp_" + self._magnet_name)
        self.current_sp_slider.setMinimumSize(80, 15)
        self.current_sp_slider.limitsFromPV = True
        self.current_sp_slider.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        self.ps1_current_rb = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":Current-RB")
        # self.ps1_current_rb.setPrecision(3)
        self.ps1_current_rb.precFromPV = True
        self.ps2_current_rb = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":Current-RB")
        # self.ps2_current_rb.setPrecision(3)
        self.ps2_current_rb.precFromPV = True

        layout.addWidget(self.current_rb_label, 0, 0)
        layout.addWidget(self.current_rb_val, 0, 1)
        layout.addWidget(QLabel("PS1"), 0, 2)
        layout.addWidget(self.ps1_current_rb, 0, 3)
        layout.addWidget(QLabel("PS2"), 1, 2)
        layout.addWidget(self.ps2_current_rb, 1, 3)
        layout.addWidget(self.current_sp_label, 2, 0)
        layout.addWidget(self.current_sp_val, 2, 1)
        layout.addWidget(self.current_sp_slider, 3, 1)
        layout.setRowStretch(4, 1)
        layout.setColumnStretch(4, 1)

        return layout
