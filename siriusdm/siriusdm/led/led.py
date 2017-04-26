import sys
from pydm.PyQt.QtCore import *
from pydm.PyQt.QtGui import *

class Led(QWidget):
    RED = 0
    GREEN = 1
    YELLOW = 2
    BLUE = 3
    ORANGE = 4
    GREY = -1
    RED_LED_FILE = "red_led.png"
    GREEN_LED_FILE = "green_led.png"
    YELLOW_LED_FILE = "yellow_led.png"
    BLUE_LED_FILE = "blue_led.png"
    ORANGE_LED_FILE = "orange_led.png"
    GREY_LED_FILE = "grey_led.png"

    def __init__(self, parent=None, status=0):
        QWidget.__init__(self, parent)
        self.status = status
        self.container = QLabel(self)

        self._setPixmap()
        self._paint()
        self.setMinimumWidth(40)
        self.setMinimumHeight(40)

    def setColor(self, color):
        self.status = color
        self._setPixmap()
        self._paint()

    def setGreen(self):
        self.status = Led.GREEN
        self._setPixmap()
        self._paint()

    def setRed(self):
        self.status = Led.RED
        self._setPixmap()
        self._paint()

    def setGrey(self):
        self.status = Led.GREY
        self._setPixmap()
        self._paint()

    @pyqtSlot(bool)
    def changeStatus(self, status):
        self.status = status
        self._setPixmap()
        self._paint()

    @pyqtSlot()
    def toggle(self):
        self.status = not self.status
        self._setPixmap()
        self._paint()

    def _setPixmap(self):
        if self.status == Led.RED:
            self.img = QPixmap(Led.RED_LED_FILE)
        elif self.status == Led.GREEN:
            self.img = QPixmap(Led.GREEN_LED_FILE)
        elif self.status == Led.YELLOW:
            self.img = QPixmap(Led.YELLOW_LED_FILE)
        elif self.status == Led.BLUE:
            self.img = QPixmap(Led.BLUE_LED_FILE)
        elif self.status == Led.ORANGE:
            self.img = QPixmap(Led.ORANGE_LED_FILE)
        else:
            self.img = QPixmap(Led.GREY_LED_FILE)

        self._scale()

    def _scale(self):
        self.s_img = self.img.scaled(20, 20)

    def _paint(self):
        self.container.setPixmap(self.s_img)
        hbox = QHBoxLayout()
        hbox.addWidget(self.container)
        self.setLayout(hbox)


if __name__ == '__main__':
    app = PyDMApplication(None, sys.argv)
    led = Led()
    led.show()
    app.exec_()
