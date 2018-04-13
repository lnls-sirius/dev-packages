"""Beagle Bone implementation module."""
from copy import deepcopy as _deepcopy

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.controller import IOController as _IOController
from siriuspy.pwrsupply.controller import IOControllerSim as _IOControllerSim
from siriuspy.pwrsupply.model import FBPPowerSupply as _FBPPowerSupply


class BeagleBone:
    """Responsible for handling BBB objects."""

    def __init__(self, bbbname, simulate=True):
        """Retrieve power supply."""
        self._bbbname = bbbname
        self._simulate = simulate

        if self._bbbname == 'BO-01:CO-BBB-1':
            self._psnames = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        elif self._bbbname == 'BO-01:CO-BBB-2':
            self._psnames = ['BO-03U:PS-CH', 'BO-03U:PS-CV']
        else:
            self._psnames = _PSSearch.conv_bbbname_2_psnames(bbbname)

        self._psmodel = _PSSearch.conv_psname_2_psmodel(self._psnames[0])
        self._database = _PSData(self._psnames[0]).propty_database
        if not self._simulate:
            self._pru = _PRU()
            self._controller = _IOController(self._pru, self._psmodel)
        else:
            self._pru = _PRUSim()
            self._controller = _IOControllerSim(self._pru, self._psmodel)

        self._power_supplies = self._create_power_supplies()

    def __getitem__(self, psname):
        """Return corresponding power supply object."""
        return self._power_supplies[psname]

    def __contains__(self, psname):
        """Test is psname is in psname list."""
        return psname in self._psnames

    @property
    def psnames(self):
        """Return list of power supply names."""
        return self._psnames.copy()

    @property
    def power_supplies(self):
        """Return power supplies."""
        return self._power_supplies

    @property
    def pru(self):
        """PRU object."""
        return self._pru

    def write(self, device_name, field, value):
        """BBB write."""
        if field == 'OpMode-Sel' and value == 2:  # Cycle
            # sync start
            ret = True
            for ps in self._power_supplies.values():
                ret &= ps.write(field, value)
            sync_mode = self.pru.SYNC_CYCLE
            addr = self._power_supplies[self.psnames[0]]._slave_id
            self.pru.sync_start(sync_mode, addr)
            return ret
            # set all devices to cycle?

        return self._power_supplies[device_name].write(field, value)

    def _get_bsmp_slave_IDs(self):
        # TODO: temp code. this should be deleted once PS bench tests are over.
        if self._bbbname == 'BO-01:CO-BBB-1':
            # test-bench BBB # 1
            return (1, 2)
        elif self._bbbname == 'BO-01:CO-BBB-2':
            # test-bench BBB # 2
            return (5, 6)
        else:
            return tuple(range(1, 1+len(self._psnames)))

    def _create_power_supplies(self):
        # Return dict of power supply objects
        slave_ids = self._get_bsmp_slave_IDs()
        power_supplies = dict()
        for i, psname in enumerate(self._psnames):
            # Define device controller
            if self._psmodel == 'FBP':
                db = _deepcopy(self._database)
                power_supplies[psname] = _FBPPowerSupply(
                    self._controller, slave_ids[i], psname, db)
        return power_supplies
