from pydm.PyQt.QtCore import pyqtSlot
from pydm.PyQt.QtGui import QDialog, QLabel, QVBoxLayout, QProgressBar


class LoadingDlg(QDialog):
    def __init__(self, title,  maximum, parent=None):
        super(LoadingDlg, self).__init__(parent)
        #self.setAttribute(Qt.WA_DeleteOnClose)

        self._may_close = False

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Loading...", self))
        self.progress = QProgressBar(self)
        self.progress.setMinimum(0)
        self.progress.setMaximum(maximum)
        layout.addWidget(self.progress)

        self.setWindowTitle(title)
        self.setLayout(layout)

    @pyqtSlot(int)
    def update(self, value):
        self.progress.setValue(value)

    @pyqtSlot(int)
    def done(self, r):
        self._may_close = True
        super(LoadingDlg, self).done(r)

    def closeEvent(self, event):
        if self._may_close:
            super(LoadingDlg, self).closeEvent(event)
        else:
            event.ignore()
