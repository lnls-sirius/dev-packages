import os
from epics import caget
from pydm.PyQt.QtCore import pyqtSignal, QThread
from pydm.PyQt.QtGui import QDialog

class LoadingThread(QThread):
    # VACA_PREFIX = os.environ.get('VACA_PREFIX', default='')
    VACA_PREFIX = ''

    taskUpdated = pyqtSignal(int)
    taskFinished = pyqtSignal(int)

    def __init__(self, name, pv_list, parent=None):
        super(LoadingThread, self).__init__(parent)
        self.name = name
        self.pv_list = pv_list
        self.parent = parent

    def run(self):
        values = dict()
        for i, pvname in enumerate(self.pv_list):
            current_pv = ':'.join(pvname['name'].split(':')[:2]) + ':Current-RB'
            force = caget(self.VACA_PREFIX + current_pv, timeout=0.3) # readForce
            if force is None:
                force = -1
            values[pvname['name']] = force
            self.taskUpdated.emit(i + 1)

        self.parent._model.loadConfiguration(self.name, values)
        self.taskFinished.emit(QDialog.Accepted)
