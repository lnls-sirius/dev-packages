"""Beagle Bone implementation module."""
from copy import deepcopy as _deepcopy

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _cPS
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.controller import IOController as _IOController
from siriuspy.pwrsupply.controller import IOControllerSim as _IOControllerSim
from siriuspy.pwrsupply.model import FBPPowerSupply as _FBPPowerSupply


class BeagleBone:
    """BeagleBone class.

    This class implements methods to read and write process variables of power
    supplies controlled by a specific beaglebone system.
    """

    # --- public interface ---

    def __init__(self, bbbname, simulate=True):
        """Retrieve power supply."""
        self._bbbname = bbbname
        self._simulate = simulate

        # retrieve names of associated power supplies
        if self._bbbname == 'BO-01:CO-BBB-1':
            self._psnames = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        elif self._bbbname == 'BO-01:CO-BBB-2':
            self._psnames = ['BO-03U:PS-CH', 'BO-03U:PS-CV']
        else:
            self._psnames = _PSSearch.conv_bbbname_2_psnames(bbbname)

        # retrieve power supply model and corresponding database
        self._psmodel = _PSSearch.conv_psname_2_psmodel(self._psnames[0])
        self._database = _PSData(self._psnames[0]).propty_database

        # creates corresponding PRU and controller
        if not self._simulate:
            self._controller = _IOController(_PRU(), self._psmodel)
        else:
            self._controller = _IOControllerSim(_PRUSim(), self._psmodel)

        # create abstract power supply objects
        self._power_supplies = self._create_power_supplies()

    @property
    def psnames(self):
        """Return list of associated power supply names."""
        return self._psnames.copy()

    @property
    def power_supplies(self):
        """Return power supplies."""
        return self._power_supplies

    @property
    def controller(self):
        """Return beaglebone controller."""
        return self._controller

    def write(self, device_name, field, value):
        """BBB write."""
        # intercept writes that affect all controlled power supplies
        if field == 'OpMode-Sel':
            return self._set_opmode(device_name, field, value)
        else:
            # write to a specific power supply
            return self._power_supplies[device_name].write(field, value)

    def __getitem__(self, index):
        """Return corresponding power supply object."""
        if isinstance(index, int):
            return self._power_supplies[self.psnames.index(index)]
        else:
            return self._power_supplies[index]

    def __contains__(self, psname):
        """Test is psname is in psname list."""
        return psname in self._psnames

    # --- private methods ---

    def _set_opmode(self, device_name, field, value):

        # try to set all power supply to Cycle mode
        success = True
        for ps in self._power_supplies.values():
            success &= ps.write(field, value)
        if not success:
            return False

        # configure PRU sync mode according to the opmode selected
        if value == _cPS.OpMode.SlowRef:
            return self._set_pru_sync_slowref(device_name, field, value)
        if value == _cPS.OpMode.Cycle:
            return self._set_pru_sync_cycle(device_name, field, value)
        elif value == _cPS.OpMode.RmpWfm:
            return self._set_pru_sync_rmpwfm(device_name, field, value)
        elif value == _cPS.OpMode.MifWfm:
            return self._set_pru_sync_migwfm(device_name, field, value)

        return success

    def _set_pru_sync_slowref(self, device_name, field, value):
        ret = self.controller.pru.sync_stop()
        return ret

    def _set_pru_sync_cycle(self, device_name, field, value):
        sync_mode = self.controller.pru.SYNC_CYCLE
        ret = self._set_pru_sync_start(sync_mode)
        return ret

    def _set_pru_sync_rmpwfm(self, device_name, field, value):
        sync_mode = self.controller.pru.SYNC_RMPEND
        ret = self._set_pru_sync_start(sync_mode)
        return ret

    def _set_pru_sync_migwfm(self, device_name, field, value):
        # turn on PRU sync mode
        sync_mode = self.controller.pru.SYNC_MIGEND
        ret = self._set_pru_sync_start(sync_mode)
        return ret

    def _set_pru_sync_start(self, sync_mode):
        slave_id = self._power_supplies[self.psnames[0]]._slave_id
        ret = self.controller.pru.sync_start(
            sync_mode=sync_mode, sync_address=slave_id)
        return ret

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
