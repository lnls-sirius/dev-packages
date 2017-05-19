from .PowerSupply import PowerSupply

class CyclePowerSupplies:

    def __init__(self):
        self._power_supplies = dict()
        self._failed_ps = set()

    @property
    def power_supplies(self):
        return self._power_supplies

    @power_supplies.setter
    def power_supplies(self, new_ps_list):
        if not isinstance(new_ps_list, list):
            raise ValueError("member 'power_supplies' must be a list")
        self._power_supplies = dict()
        for ps in new_ps_list:
            if ps not in self._power_supplies.keys():
                self._power_supplies[ps] = PowerSupply(ps)

    def failed_ps(self):
        return self._failed_ps

    def preparePsToCycle(self, name, ps):
        if not ps.write('PwrState-Sel', PowerSupply.ON):
            self._failed_ps.add(self._power_supplies[name])
            return False
        if not ps.write('OpMode-Sel', PowerSupply.SIGGEN):
            self._failed_ps.add(self._power_supplies[name])
            return False
        if not ps.write('Current-SP', 0.0):
            self._failed_ps.add(self._power_supplies[name])
            return False

        return True
