from pydm.PyQt.QtGui import QApplication, QDialog, QVBoxLayout
from .detail_widget.MagnetDetailWidget import MagnetDetailWidget

class MagnetDetailWindow(QDialog):
    STYLESHEET = """
        .QGroupBox {
            width: auto;
        }
    """

    def __init__(self, magnet_name, parent=None):
        super(MagnetDetailWindow, self).__init__(parent)
        self.app = QApplication.instance()

        self._ma = magnet_name

        self._setupUi()
        self.setStyleSheet(self.STYLESHEET)

        self.app.establish_widget_connections(self)

    def _setupUi(self):
        #Set window layout
        self.layout = QVBoxLayout()

        self.widget = MagnetDetailWidget(self._ma, self)
        self.layout.addWidget(self.widget)

        self.setWindowTitle(self._ma + ' Detail')
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.app.close_widget_connections(self)


if __name__ == '__main__':
    import sys
    from pydm import PyDMApplication
    app = PyDMApplication(None, sys.argv)
    window = MagnetDetailWindow("SI-Fam:MA-QFA")
    window.show()
    app.exec_()
