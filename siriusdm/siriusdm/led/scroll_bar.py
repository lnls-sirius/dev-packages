import time, math
from pydm.PyQt.QtGui import QAbstractSlider, QScrollBar, QAction, QMenu, QInputDialog
from pydm.PyQt.QtCore import Qt, pyqtSignal, pyqtSlot, pyqtProperty
from pydm.widgets.channel import PyDMChannel

class PyDMScrollBar(QScrollBar):

    value_changed_signal = pyqtSignal([int],[float],[str])
    connected_signal = pyqtSignal()
    disconnected_signal = pyqtSignal()

    def __init__(self, orientation, parent=None, channel=None, scale=1000):
        super(PyDMScrollBar, self).__init__(orientation, parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setInvertedControls(False)

        self.decimal = 0.0
        self._scale = scale
        self._connected = False
        self._channels = None
        self.channel = channel
        self._channeltype = None

        self.setSingleStep(self._scale)
        self.setPageStep(self._scale * 10)

        self.valueChanged.connect(self.value_changed)


    @pyqtSlot()
    def changeStep(self):
        d, okPressed = QInputDialog.getDouble(self, "Get double","Value:", self.singleStep()/self._scale, 0.1, 5, 1)
        if okPressed:
            self.setSingleStep(self._scale * d)

    @pyqtSlot(bool)
    def connectionStateChanged(self, connected):
        self._connected = connected
        if connected:
            #print("Connected")
            self.connected_signal.emit()
        else:
            self.disconnected_signal.emit()

    @pyqtSlot(float)
    @pyqtSlot(int)
    @pyqtSlot(str)
    def receiveValue(self, value):
        self._channeltype = type(value)

        scaled_v = value * self._scale
        new_value = int(value * self._scale)
        diff = scaled_v - new_value
        self.decimal = diff/self._scale

        self.setValue(new_value)

    @pyqtSlot()
    def value_changed(self):
        ''' Emits a value changed signal '''
        if self._connected:
            if self.value() == self.minimum():
                self.value_changed_signal[self._channeltype].emit(self._channeltype(self.minimum()/self._scale))
            elif self.value() == self.maximum():
                self.value_changed_signal[self._channeltype].emit(self._channeltype(self.maximum()/self._scale))
            else:
                self.value_changed_signal[self._channeltype].emit(self._channeltype(self.value()/self._scale + self.decimal))


    @pyqtSlot(float)
    def receiveLowerLimit(self, value):
        self.setMinimum(value * self._scale)
    @pyqtSlot(float)
    def receiveUpperLimit(self, value):
        self.setMaximum(value * self._scale)


    def channels(self):
        if self._channels is None:
            self._channels = [PyDMChannel(  address=self.channel,
                                            connection_slot=self.connectionStateChanged,
                                            value_slot=self.receiveValue,
                                            value_signal=self.value_changed_signal,
                                            lower_disp_limit_slot=self.receiveLowerLimit,
                                            upper_disp_limit_slot=self.receiveUpperLimit)]
        return self._channels
