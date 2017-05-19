from pydm.PyQt.QtCore import QThread, pyqtSignal
from pydm.PyQt.QtGui import QDialog

class PrepareCycleThread(QThread):
    taskUpdated = pyqtSignal(int)
    taskFinished = pyqtSignal(int)

    def __init__(self, cycle, parent=None):
        super(PrepareCycleThread, self).__init__(parent)
        self.cycle = cycle

    def run(self):
        i = 1
        for name, ps in self.cycle.power_supplies.items():
            self.cycle.preparePsToCycle(name, ps)
            self.taskUpdated.emit(i)
            i += 1

        #Connectes with dialog
        if len(self.cycle.failed_ps()) > 0:
            self.taskFinished.emit(QDialog.Rejected)
        else:
            self.taskFinished.emit(QDialog.Accepted)
