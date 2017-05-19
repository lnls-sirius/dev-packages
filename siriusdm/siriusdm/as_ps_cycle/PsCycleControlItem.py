import sys, re
from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.label import PyDMLabel

#Override PyDMLabel receiveValue in order to make a label emit textChanged signal
class UpdatableLabel(PyDMLabel):
    textChanged = pyqtSignal()

    @pyqtSlot(float)
    @pyqtSlot(int)
    @pyqtSlot(str)
    def receiveValue(self, new_value):
        changed = (self.value != new_value)
        self.value = new_value
        if isinstance(new_value, str):
            self.setText(new_value)
        elif isinstance(new_value, float):
            if self.format_string:
                self.setText(self.format_string.format(new_value))
        elif self.enum_strings is not None and isinstance(new_value, int):
            self.setText(self.enum_strings[new_value])
        else:
            self.setText(str(new_value))
        if changed:
            self.textChanged.emit()
        return


class PsCycleControlItem(QWidget):

    CSS = """
        QWidget[readytocycle="2"] {
            color: red;
        }
        QWidget[readytocycle="1"] {
            color: green;
        }
        QWidget[readytocycle="0"] {
            color: #aa5909;
        }
        """

    def __init__(self, ps, parent=None):
        super(PsCycleControlItem, self).__init__(parent)

        #Elements
        self.elem_name = QLabel(ps.dev_name)
        self.elem_pwr = UpdatableLabel(self, "ca://VAG-" + ps.dev_name + ":PwrState-Sts")
        self.elem_status = UpdatableLabel(self, "ca://VAG-" + ps.dev_name + ":OpMode-Sts")
        self.elem_val= PyDMLineEdit(self, "ca://VAG-" + ps.dev_name + ":Current-RB")

        #UI properties
        self.elem_name.setProperty("readytocycle", 0)
        self.elem_name.setMaximumWidth(120)
        self.elem_name.setMinimumWidth(120)
        self.elem_pwr.setProperty("readytocycle", 0)
        self.elem_pwr.setMaximumWidth(30)
        self.elem_pwr.setMinimumWidth(30)
        self.elem_status.setProperty("readytocycle", 0)
        self.elem_status.setMinimumWidth(65)
        self.elem_status.setMaximumWidth(65)
        self.elem_val.setProperty("readytocycle", 0)
        self.elem_val.setMaximumWidth(75)
        self.elem_val.setFrame(False)
        self.elem_val.setReadOnly(True)
        self.elem_val._userformat = "{:.6}"

        #Signals
        self.elem_pwr.textChanged.connect(self.valueUpdated)
        self.elem_pwr.connected_signal.connect(self.valueUpdated)
        self.elem_pwr.disconnected_signal.connect(self.pvDisconnected)
        self.elem_status.textChanged.connect(self.valueUpdated)
        self.elem_status.connected_signal.connect(self.valueUpdated)
        self.elem_status.disconnected_signal.connect(self.pvDisconnected)
        self.elem_val.textChanged.connect(self.valueUpdated)
        self.elem_val.connected_signal.connect(self.valueUpdated)
        self.elem_val.disconnected_signal.connect(self.pvDisconnected)

        layout = QHBoxLayout()
        layout.addWidget(self.elem_name)
        layout.addWidget(self.elem_pwr)
        layout.addWidget(self.elem_status)
        layout.addWidget(self.elem_val)
        self.setLayout(layout)
        self.setStyleSheet(PsCycleControlItem.CSS)

    @pyqtSlot()
    def valueUpdated(self):

        power = (self.elem_pwr.value == 1)
        status = (self.elem_status.value == 3)
        value = (self.elem_val._value == 0.0)

        if power and status and value:
            self.elem_name.setProperty("readytocycle", 1)
        else:
            self.elem_name.setProperty("readytocycle", 0)

        if power:
            self.elem_pwr.setProperty("readytocycle", 1)
        else:
            self.elem_pwr.setProperty("readytocycle", 0)

        if status:
            self.elem_status.setProperty("readytocycle", 1)
        else:
            self.elem_status.setProperty("readytocycle", 0)

        if value:
            self.elem_val.setProperty("readytocycle", 1)
        else:
            self.elem_val.setProperty("readytocycle", 0)
        #Set stylesheet again to force widgets to be reapainted
        self.setStyleSheet(PsCycleControlItem.CSS)


    @pyqtSlot()
    def pvDisconnected(self):
        sender = self.sender()
        sender.setProperty("readytocycle", 2)
        self.elem_name.setProperty("readytocycle", 2)
        self.setStyleSheet(PsCycleControlItem.CSS)
