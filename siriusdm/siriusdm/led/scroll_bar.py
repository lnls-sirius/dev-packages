import time
from pydm.PyQt.QtGui import QLabel, QApplication, QColor, QPalette, QWidget, QScrollBar
from pydm.PyQt.QtCore import Qt, pyqtSignal, pyqtSlot, pyqtProperty, QState, QStateMachine, QPropertyAnimation, QByteArray
from pydm.widgets.channel import PyDMChannel

class PyDMScrollBar(QScrollBar):

    value_changed_signal = pyqtSignal([int],[float],[str])
    connected_signal = pyqtSignal()
    disconnected_signal = pyqtSignal()

    def __init__(self, orientation, parent=None, channel=None):
        super(PyDMScrollBar, self).__init__(orientation, parent)

        self._connected = False
        self._channels = None
        self.channel = channel
        self._channeltype = None

        self.valueChanged.connect(self.value_changed)


    @pyqtSlot(bool)
    def connectionStateChanged(self, connected):
        self._connected = connected
        if connected:
            #print("Connected")
            self.connected_signal.emit()
        else:
            self.disconnected_signal.emit()

    @pyqtSlot(float)
    def receiveValue(self, value):
        #print("Scroll Bar Received Value {}".format(value))
        self._channeltype = type(value)
        self.setValue(value)

    @pyqtSlot()
    def value_changed(self):
        ''' Emits a value changed signal '''
        if self._connected:
            #print("Scroll Bar Emitting {}".format(self.value()))
            self.value_changed_signal[self._channeltype].emit(self._channeltype(self.value()))

    @pyqtSlot(int)
    def receiveLowerLimit(self, value):
        self.setMinimum(value)
    @pyqtSlot(int)
    def receiveUpperLimit(self, value):
        self.setMaximum(value)

    def channels(self):
        if self._channels is None:
            self._channels = [PyDMChannel(  address=self.channel,
                                            connection_slot=self.connectionStateChanged,
                                            value_slot=self.receiveValue,
                                            value_signal=self.value_changed_signal,
                                            lower_limit_slot=self.receiveLowerLimit,
                                            upper_limit_slot=self.receiveUpperLimit)]
        return self._channels
