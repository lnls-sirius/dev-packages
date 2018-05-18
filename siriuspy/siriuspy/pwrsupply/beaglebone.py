"""Beagle Bone implementation module."""
from copy import deepcopy as _deepcopy

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
from siriuspy.pwrsupply.e2scontroller \
    import E2SController as _E2SController
from siriuspy.pwrsupply.e2scontroller \
    import DeviceInfo as _DeviceInfo

# TODO: improve code
#
# 01. try to optimize it. At this point it is taking up 80% of BBB1 CPU time.
#     from which ~20% comes from PRController. I think we could keep some kind
#     of device state mirror in E2SController such that it does not have to
#     invoke PRUController read at every device field update. This mirror state
#     could be updated in one go.


class BeagleBone:
    """BeagleBone class.

    This class implements methods to read and write process variables of power
    supplies controlled by a specific beaglebone system.
    """

    def __init__(self, bbbname, simulate=True):
        """Retrieve power supply."""
        self._bbbname = bbbname
        self._simulate = simulate
        self._devices_info = dict()

        # retrieve names of associated power supplies
        # TODO: temporary 'if' for tests.
        if self._bbbname == 'BO-01:CO-PSCtrl-1':
            self._psnames = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        elif self._bbbname == 'BO-01:CO-PSCtrl-2':
            self._psnames = ['BO-03U:PS-CH', 'BO-03U:PS-CV']
        else:
            self._psnames = _PSSearch.conv_bbbname_2_psnames(bbbname)

        # retrieve power supply model and corresponding database
        self._psmodel = _PSSearch.conv_psname_2_psmodel(self._psnames[0])
        self._database = _PSData(self._psnames[0]).propty_database

        # create abstract power supply objects
        # self._power_supplies = self._create_power_supplies()
        self._create_e2s_controller()
        self._wfm_dirty = False

    # --- public interface ---

    @property
    def psnames(self):
        """Return list of associated power supply names."""
        return self._psnames.copy()

    @property
    def pru_controller(self):
        """Return PRU controller."""
        return self._pru_controller

    @property
    def e2s_controller(self):
        """Return E2S controller."""
        return self._e2s_controller

    @property
    def devices_database(self):
        """Database."""
        return self._database

    def read(self, device_name):
        """Read all device fields."""
        field_values = self._e2s_controller.read_all(device_name)
        # field_values = self.power_supplies[device_name].read_all()
        return field_values

    def write(self, device_name, field, value):
        """BBB write."""
        if field == 'OpMode-Sel':
            self._set_opmode(value)
        elif field == 'CycleDsbl-Cmd':
            self._e2s_controller.write(self.psnames, field, 1)
        else:
            # self.power_supplies[device_name].write(field, value)
            self._e2s_controller.write(device_name, field, value)

    def check_connected(self, device_name):
        """"Return connection status."""
        return self._e2s_controller.check_connected(device_name)

    # --- private methods ---

    def _set_opmode(self, op_mode):
        self._pru_controller.pru_sync_stop()  # TODO: not necessary. test.
        self._restore_wfm()
        self._e2s_controller.write(self.psnames, 'OpMode-Sel', op_mode)
        if op_mode == _PSConst.OpMode.Cycle:
            sync_mode = self._pru_controller.PRU.SYNC_MODE.CYCLE
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.RmpWfm:
            sync_mode = self._pru_controller.PRU.SYNC_MODE.RMPEND
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.MigWfm:
            sync_mode = self._pru_controller.PRU.SYNC_MODE.MIGEND
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.SlowRefSync:
            self._wfm_dirty = True
            sync_mode = self._pru_controller.PRU.SYNC_MODE.RMPEND
            return self._pru_controller.pru_sync_start(sync_mode)
        # else:
        #     print('mode {} not implemented yet!', format(op_mode))

        # return self._state.set_op_mode(self)

    def _get_bsmp_slave_IDs(self):
        # TODO: temp code. this should be deleted once PS bench tests are over.
        if self._bbbname == 'BO-01:CO-PSCtrl-1':
            # test-bench BBB # 1
            return (1, 2)
        elif self._bbbname == 'BO-01:CO-PSCtrl-2':
            # test-bench BBB # 2
            return (5, 6)
        else:
            return tuple(range(1, 1+len(self._psnames)))

    def _create_e2s_controller(self):
        # Return dict of power supply objects
        slave_ids = self._get_bsmp_slave_IDs()
        self._pru_controller = _PRUController(
            self._psmodel, slave_ids, simulate=self._simulate)
        for i, psname in enumerate(self._psnames):
            self._devices_info[psname] = _DeviceInfo(psname, slave_ids[i])
        db = _deepcopy(self._database)
        self._e2s_controller = _E2SController(
            self._pru_controller, self._devices_info, db)

    def _restore_wfm(self):
        if self._wfm_dirty:
            self._pru_controller.pru_curve_send()
            self._wfm_dirty = False
