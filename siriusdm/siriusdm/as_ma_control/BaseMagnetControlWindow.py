#!/usr/local/bin/python3.6
import re
from pydm.PyQt.QtGui import QDialog, QTabWidget, QVBoxLayout, QPushButton, QApplication
from .MagnetDetailWindow import MagnetDetailWindow
from .MagnetTrimWindow import MagnetTrimWindow

class BaseMagnetControlWindow(QDialog):
    DETAIL = 0
    TRIM = 1

    _window = None

    def __init__(self, parent=None):
        super(BaseMagnetControlWindow, self).__init__(parent)
        self._setupUi()
        self.setStyleSheet(
        """
        QGroupBox {
            font-size:14pt;
            font-weight:bold;
        }

        QScrollBar {
            border: 1px solid black;
        }
        """)

        self.app = QApplication.instance()
        self.app.establish_widget_connections(self)


    def _setupUi(self):
        self.layout = QVBoxLayout()

        #Create Tabs
        self.tabs = QTabWidget()
        self._addTabs()

        #Set widget layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def _addTabs(self): pass

    def _connectButtons(self, buttons):
        for button in buttons:
            try:
                type_ = button.objectName().split("_")[0]
                if type_ in ["label", "trim"]:
                    button.clicked.connect(self._openWindow)
            except:
                pass

    def _openWindow(self):
        sender = self.sender()

        name_split = sender.objectName().split("_")
        type_ = name_split[0]
        ma = name_split[1]

        if ma:
            if type_ == "label":
                self._window = MagnetDetailWindow(ma, self)
            elif type_ == "trim":
                self._window = MagnetTrimWindow(ma, self)

        self._window.exec_()

    def closeEvent(self, event):
        self.app.close_widget_connections(self)


if __name__ == '__main__':
    import sys
    from pydm import PyDMApplication
    app = PyDMApplication(None, sys.argv)
    window = MagnetControlWindow()
    window.show()
    app.exec_()
