import re
from ..pwrsupply import psdata

class ConfigurationPvs:
    def pvs(self):
        return self._getPvs()

    @staticmethod
    def getForce(slot):
        if re.match("^[A-Z]{2}-\w{2,4}:PS-B", slot):
            return "Energy"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-Q", slot):
            return "KL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-S", slot):
            return "SL"
        elif re.match("^[A-Z]{2}-\w{2,4}:PS-(C|F)", slot):
            return "Angle"
        else:
            return "???"

    def _getPvs(self): pass

class BoForcePvs(ConfigurationPvs):
    def __init__(self):
        super(BoForcePvs, self).__init__()

    def _getPvs(self):
        pvs = dict()
        slots = psdata.get_names()
        if slots:
            for slot in slots:
                pv = slot + ":" + ConfigurationPvs.getForce(slot) + "-RB"
                if re.match("^BO-\w{2,4}:PS-(B|Q|S|C|F)", pv):
                    pvs[pv] = float

        return pvs


class SiForcePvs(ConfigurationPvs):
    def __init__(self):
        super(SiForcePvs, self).__init__()

    def _getPvs(self):
        pvs = dict()
        slots = psdata.get_names()
        if slots:
            for slot in slots:
                pv = slot + ":" + ConfigurationPvs.getForce(slot) + "-RB"
                if re.match("^SI-\w{2,4}:PS-(B|Q|S|C|F)", pv):
                    pvs[pv] = float

        return pvs
