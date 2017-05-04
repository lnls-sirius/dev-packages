from pydm.PyQt.QtGui import QLabel, QApplication, QColor, QPalette, QWidget
from pydm.PyQt.QtCore import Qt, pyqtSignal, pyqtSlot, pyqtProperty, QState, QStateMachine, QPropertyAnimation, QByteArray
from pydm.widgets.channel import PyDMChannel
from pydm.application import PyDMApplication
from .led import Led

class PyDMLed(Led):

    connected_signal = pyqtSignal()
    disconnected_signal = pyqtSignal()

    def __init__(self, parent=None, init_channel=None, bit=None, enum_map=None):
        super(PyDMLed, self).__init__(parent, Led.GREY)
        self._value = None

        self._channel = init_channel
        if bit is not None:
            self._bit = int(bit)
            self._mask = 1 << bit
        else:
            self._bit = None
            self._mask = None

        self._enum_strings = None
        self._enum_map = enum_map

        self._connected = False


    @pyqtSlot(bool)
    def connectionStateChanged(self, connected):
        self._connected = connected
        if connected:
            self.connected_signal.emit()
        else:
            self.disconnected_signal.emit()
            self.receiveValue(0)

    @pyqtSlot(int)
    @pyqtSlot(float)
    @pyqtSlot(str)
    def receiveValue(self, value):
        if self._connected:
            if self._enum_strings is None: #PV of type integer or float
                if self._bit is None: #Led represents value of PV
                    if value and isinstance(value, str):
                        value = int(value)
                    if value:
                        self.setGreen()
                    else:
                        self.setRed()
                else: #Led represents specific bit of PV
                    value = int(value)
                    bit_val = (value & self._mask) >> self._bit
                    self.setColor(bit_val)
            else: #PV of type ENUM
                if self._enum_map is None:
                    self.setColor(value)
                else:
                    if self._enum_strings is not None and isinstance(value, int):
                        enum_name = self._enum_strings[value]
                        color = self._enum_map[enum_name]
                        self.setColor(color)

            #TODO: PV of type array
        else:
            self.setColor(-1)



    @pyqtSlot(tuple)
    def enumStringsChanged(self, enum_strings):
        if enum_strings != self._enum_strings:
            self._enum_strings = enum_strings
            self.receiveValue(self._value)

    def channels(self):
        return [PyDMChannel(address=self._channel,
                            connection_slot=self.connectionStateChanged,
                            value_slot=self.receiveValue,
                            enum_strings_slot=self.enumStringsChanged)]
