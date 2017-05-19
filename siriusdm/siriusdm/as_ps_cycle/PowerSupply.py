import re, os
from epics import PV


class PowerSupply:

    #PVS
    PVS = ['Current-RB', 'Current-SP', 'PwrState-Sts', 'PwrState-Sel',
            'OpMode-Sel', 'OpMode-Sts']
    VACA_PREFIX = os.environ.get("VACA_PREFIX", default="")

    #Static Class Variables
    OFF = SLOWREF = REMOTE = DISABLED = 0
    ON = FASTREF = LOCAL = ENABLED = AUTOCORR = 1
    WAIT = WFMREF = MEASRESPMAT = 2
    SIGGEN = 3

    def __init__(self, dev_name):
        self._dev_name = dev_name
        self._pvs = dict(())

        self._force = self._getForce()

        #general pvs
        for pv in self.PVS:
            self._pvs[pv] = None
        #device specific pvs
        self._pvs[self._force] = None


    def _getForce(self):
        if re.match("^[A-Z]{2}-\w{2,4}:PS-B", self._dev_name):
            self.element = "B"
            self.force = "Energy"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-QS", self._dev_name):
            self.element = "QS"
            self.force = "KL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-Q", self._dev_name):
            self.element = "Q"
            self.force = "KL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-S", self._dev_name):
            self.element = "S"
            self.force = "SL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-C", self._dev_name):
            self.element = "C"
            self.force = "Angle"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-F", self._dev_name):
            self.element = "FC"
            self.force = "Angle"
        else:
            raise ValueError("Element '{}' not recognised".format(dev_name))

    @property
    def dev_name(self):
        return self._dev_name

    def _createChannel(self, field):
        if self._pvs[field] is None:
            pvname = self.VACA_PREFIX + self._dev_name + ":" + field
            self._pvs[field] = PV(pvname)

    def read(self, field):
        self._createChannel(field)
        return self._pvs[field].get(timeout=1.0)

    def write(self, field, value):
        self._createChannel(field)
        return self._pvs[field].put(value, timeout=3.0)

    '''
    def readCurrentSetPoint(self):
        return caget(self.dev_name + ':Current-SP')

    def setCurrentSetPoint(self, value):
        return caput(self.dev_name + ':Current-SP ', value)

    def readPowerStateStatus(self):
        return caget(self.dev_name + ':PwrState-Sts')

    def readPowerStateSelected(self):
        return caget(self.dev_name + ':PwrState-Sel')

    def setPowerStateSelected(self, value):
        return caput(self.dev_name + ':PwrState-Sel', value)

    def readOpModeStatus(self):
        return caget(self.dev_name + ':OpMode-Sts')

    def readOpModeSelected(self):
        return caget(self.dev_name + ':OpMode-Sel')

    def setOpModeSelected(self, value):
        return caput(self.dev_name + ':OpMode-Sel', value)

    def readForce(self):
        return caget(self.dev_name + ':' + self.force + '-RB')
    '''
