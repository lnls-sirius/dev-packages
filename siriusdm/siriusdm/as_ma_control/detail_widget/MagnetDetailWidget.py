"""MagnetDetailWidget definition."""

import re
from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QWidget, QGroupBox, QGridLayout, QVBoxLayout, \
    QHBoxLayout, QLabel, QSizePolicy
from pydm.widgets.label import PyDMLabel
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.led import PyDMLed
from pydm.widgets.scrollbar import PyDMScrollBar
from pydm.widgets.QDoubleScrollBar import QDoubleScrollBar


class MagnetDetailWidget(QWidget):
    """Widget with control interface for a given magnet."""

    def __init__(self, magnet_name, parent=None):
        """Class constructor."""
        super(MagnetDetailWidget, self).__init__(parent)

        self._magnet_name = magnet_name
        self._ps_name = re.sub(":MA-", ":PS-", self._magnet_name)

        self._magnet_type = self._getElementType()
        if self._magnet_type == "b":
            self._metric = "Energy"
            self._metric_text = "Energy [GeV]"
        elif self._magnet_type == "q":
            self._metric = "KL"
            self._metric_text = "KL [1/m]"
        elif self._magnet_type == "s":
            self._metric = "SL"
            self._metric_text = "SL [1/m^2]"
        elif self._magnet_type in ["sc", "fc"]:
            self._metric = "Kick"
            self._metric_text = "Kick [mrad]"

        self._setupUi()

    def _setupUi(self):
        # Group boxes that compose the widget
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.opmode_box = QGroupBox("Op Mode")
        self.opmode_box.setObjectName("operation_mode")
        self.pwrstate_box = QGroupBox("Pwr State")
        self.pwrstate_box.setObjectName("power_state")
        self.current_box = QGroupBox("Current [A]")
        self.current_box.setObjectName("current")
        self.metric_box = QGroupBox(self._metric_text)
        self.metric_box.setObjectName("metric")

        # Set group boxes layouts
        self.interlock_box.setLayout(self._interlockLayout())
        self.opmode_box.setLayout(self._opModeLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.current_box.setLayout(self._currentLayout())
        self.metric_box.setLayout(self._metricLayout())

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        layout = QGridLayout()

        layout.addWidget(
            QLabel("<h1>" + self._magnet_name + "</h1>"), 0, 0, 1, 3)
        layout.addWidget(self.interlock_box, 1, 0, 3, 1)
        layout.addWidget(self.opmode_box, 1, 1)
        layout.addWidget(self.pwrstate_box, 1, 2)
        layout.addWidget(self.current_box, 2, 1, 1, 2)
        layout.addWidget(self.metric_box, 3, 1, 1, 2)
        layout.setColumnStretch(4, 1)

        return layout

    def _interlockLayout(self):
        # layout = QVBoxLayout()
        layout = QGridLayout()
        for i in range(16):
            led = PyDMLed(
                self, "ca://" + self._magnet_name + ":Intlk-Mon", i)
            led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            layout.addWidget(led, i, 0)
            layout.addWidget(QLabel("Bit " + str(i)), i, 1)
        layout.setRowStretch(17, 1)

        return layout

    def _opModeLayout(self):
        layout = QVBoxLayout()

        self.opmode_sp = PyDMEnumComboBox(
            self, "ca://" + self._magnet_name + ":OpMode-Sel")
        self.opmode_rb = PyDMLabel(
            self, "ca://" + self._magnet_name + ":OpMode-Sts")
        self.ctrlmode_led = PyDMLed(
            self, "ca://" + self._magnet_name + ":CtrlMode-Mon")
        self.ctrlmode_label = PyDMLabel(
            self, "ca://" + self._magnet_name + ":CtrlMode-Mon")

        self.ctrlmode_led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        ctrlmode_layout = QHBoxLayout()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        layout.addWidget(self.opmode_sp)
        layout.addWidget(self.opmode_rb)
        layout.addLayout(ctrlmode_layout)

        return layout

    def _powerStateLayout(self):
        layout = QVBoxLayout()

        self.on_btn = PyDMPushButton(
            self, label="On", pressValue=1,
            init_channel="ca://" + self._magnet_name + ":PwrState-Sel")
        self.off_btn = PyDMPushButton(
            self, label="Off", pressValue=0,
            init_channel="ca://" + self._magnet_name + ":PwrState-Sel")
        self.pwrstate_led = PyDMLed(
            self, "ca://" + self._magnet_name + ":PwrState-Sts")
        self.pwrstate_label = PyDMLabel(
            self, "ca://" + self._magnet_name + ":PwrState-Sts")

        self.pwrstate_led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.on_btn)
        buttons_layout.addWidget(self.off_btn)
        pwrstatus_layout = QHBoxLayout()
        pwrstatus_layout.addWidget(self.pwrstate_led)
        pwrstatus_layout.addWidget(self.pwrstate_label)

        layout.addLayout(buttons_layout)
        layout.addLayout(pwrstatus_layout)

        return layout

    def _currentLayout(self):
        layout = QGridLayout()

        self.current_rb_label = QLabel("Readback")

        self.current_sp_label = QLabel("Setpoint")

        self.current_rb_val = PyDMLabel(
            self, "ca://" + self._magnet_name + ":Current-RB")
        self.current_rb_val.precFromPV = True
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

        layout.addWidget(self.current_rb_label, 0, 0)
        layout.addWidget(self.current_rb_val, 0, 1)
        layout.addWidget(self.current_sp_label, 1, 0)
        layout.addWidget(self.current_sp_val, 1, 1)
        layout.addWidget(self.current_sp_slider, 2, 1)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(2, 1)

        return layout

    def _metricLayout(self):
        layout = QGridLayout()

        self.metric_rb_label = QLabel("Readback")
        self.metric_sp_label = QLabel("Setpoint")

        self.metric_rb_val = PyDMLabel(
            self, "ca://" + self._magnet_name + ":" + self._metric + "-RB")
        self.metric_rb_val.precFromPV = True
        # self.metric_rb_val.setPrecision(3)

        self.metric_sp_val = PyDMLineEdit(
            self, "ca://" + self._magnet_name + ":" + self._metric + "-SP")
        # self.metric_sp_val.receivePrecision(3)

        self.metric_sp_slider = PyDMScrollBar(
            self, Qt.Horizontal,
            "ca://" + self._magnet_name + ":" + self._metric + "-SP")
        self.metric_sp_slider.setObjectName("metric-sp_" + self._magnet_name)
        self.metric_sp_slider.setMinimumSize(80, 15)
        self.metric_sp_slider.limitsFromPV = True
        self.metric_sp_slider.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        layout.addWidget(self.metric_rb_label, 0, 0)
        layout.addWidget(self.metric_rb_val, 0, 1)
        layout.addWidget(self.metric_sp_label, 1, 0)
        layout.addWidget(self.metric_sp_val, 1, 1)
        layout.addWidget(self.metric_sp_slider, 2, 1)
        layout.setRowStretch(3, 1)
        layout.setColumnStretch(3, 1)

        return layout

    def _getElementType(self):
        dipole = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-B")
        quadrupole = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-Q\w+")
        sextupole = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-S\w+$")
        slow_corrector = re.compile(
            "(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-(CH|CV)(-|\w)*")
        fast_corrector = re.compile(
            "(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-(FCH|FCV)(-|\w)*")
        skew_quad = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-QS")

        if dipole.match(self._magnet_name):
            return "b"
        elif quadrupole.match(self._magnet_name) or \
                skew_quad.match(self._magnet_name):
            return "q"
        elif sextupole.match(self._magnet_name):
            return "s"
        elif slow_corrector.match(self._magnet_name):
            return "sc"
        elif fast_corrector.match(self._magnet_name):
            return "fc"
        else:
            raise ValueError("Element not defined")
