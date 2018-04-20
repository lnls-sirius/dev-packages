"""Beagle Bone implementation module."""
from copy import deepcopy as _deepcopy
import logging as _log
import re as _re

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _cPS
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.controller import IOController as _IOController
from siriuspy.pwrsupply.controller import IOControllerSim as _IOControllerSim
from siriuspy.pwrsupply.model import FBPPowerSupply as _FBPPowerSupply
from siriuspy.pwrsupply.bbb import BBBController as _BBBController
from siriuspy.pwrsupply.bsmp import FBPEntities as _FBPEntities
from siriuspy.pwrsupply.bsmp import Const as _c
from .status import PSCStatus as _PSCStatus
from siriuspy.csdevice.pwrsupply import Const as _devc


class IOCDevice:
    """Setpoints and field translation."""

    # Constants and Setpoint regexp patterns
    _ct = _re.compile('^.*-Cte$')
    _sp = _re.compile('^.*-(SP|Sel|Cmd)$')

    bsmp_2_epics = {
        _c.V_PS_STATUS: ('PwrState-Sts', 'OpMode-Sts', 'CtrlMode-Mon'),
        _c.V_PS_SETPOINT: 'Current-RB',
        _c.V_PS_REFERENCE: 'CurrentRef-Mon',
        _c.V_FIRMWARE_VERSION: 'Version-Cte',
        _c.V_SIGGEN_ENABLE: 'CycleEnbl-Mon',
        _c.V_SIGGEN_TYPE: 'CycleType-Sts',
        _c.V_SIGGEN_NUM_CYCLES: 'CycleNrCycles-RB',
        _c.V_SIGGEN_N: 'CycleIndex-Mon',
        _c.V_SIGGEN_FREQ: 'CycleFreq-RB',
        _c.V_SIGGEN_AMPLITUDE: 'CycleAmpl-RB',
        _c.V_SIGGEN_OFFSET: 'CycleOffset-RB',
        _c.V_SIGGEN_AUX_PARAM: 'CycleAuxParam-RB',
        _c.V_PS_SOFT_INTERLOCKS: 'IntlkSoft-Mon',
        _c.V_PS_HARD_INTERLOCKS: 'IntlkHard-Mon',
        _c.V_I_LOAD: 'Current-Mon',
    }

    epics_2_bsmp = {
        'PwrState-Sts': _c.V_PS_STATUS,
        'OpMode-Sts': _c.V_PS_STATUS,
        'CtrlMode-Mon': _c.V_PS_STATUS,
        'Current-RB': _c.V_PS_SETPOINT,
        'CurrentRef-Mon': _c.V_PS_REFERENCE,
        'Version-Cte': _c.V_FIRMWARE_VERSION,
        'CycleEnbl-Mon': _c.V_SIGGEN_ENABLE,
        'CycleType-Sts': _c.V_SIGGEN_TYPE,
        'CycleNrCycles-RB': _c.V_SIGGEN_NUM_CYCLES,
        'CycleIndex-Mon': _c.V_SIGGEN_N,
        'CycleFreq-RB': _c.V_SIGGEN_FREQ,
        'CycleAmpl-RB': _c.V_SIGGEN_AMPLITUDE,
        'CycleOffset-SP': _c.V_SIGGEN_OFFSET,
        'CycleAuxParam-RB': _c.V_SIGGEN_AUX_PARAM,
        'IntlkSoft-Mon': _c.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _c.V_PS_HARD_INTERLOCKS,
        'Current-Mon': _c.V_I_LOAD,
    }

    _epics_2_wfuncs = {
        'PwrState-Sel': '_set_pwrstate',
        'OpMode-Sel': '_set_opmode',
        'Current-SP': '_set_current',
        'Reset-Cmd': '_reset',
        'Abort-Cmd': '_abort',
        'CycleEnbl-Cmd': '_enable_cycle',
        'CycleDsbl-Cmd': '_disable_cycle',
        'CycleType-Sel': '_set_cycle_type',
        'CycleNrCycles-SP': '_set_cycle_nr_cycles',
        'CycleFreq-SP': '_set_cycle_frequency',
        'CycleAmpl-SP': '_set_cycle_amplitude',
        'CycleOffset-SP': '_set_cycle_offset',
        'CycleAuxParam-SP': '_set_cycle_aux_params',
        'WfmData-SP': '_set_wfmdata_sp',
    }

    _ct = _re.compile('^.*-Cte$')
    _sp = _re.compile('^.*-(SP|Sel|Cmd)$')

    def __init__(self, bsmp_device, psname, database):
        """Init."""
        self._bsmp_device = bsmp_device
        self._psname = psname
        self._database = database
        # define and init constant and setpoint fields
        self._setpoints = dict()
        self._constants = dict()
        for field, db in self.database.items():
            if self._sp.match(field):
                self._setpoints[field] = db
            elif self._ct.match(field):
                self._constants[field] = db
        #self._initiated = False
        #self._init()

    # API
    @property
    def psname(self):
        """Device name."""
        return self._psname

    @property
    def database(self):
        """Device database."""
        return self._database

    @property
    def connected(self):
        return self._bsmp_device.connected

    @property
    def setpoints(self):
        return self._setpoints

    def read(self, field):
        """Read a field."""
        variable_id = self.epics_2_bsmp[field]
        value = self._bsmp_device.read(variable_id)

        if value is None:
            return None

        if field == 'PwrState-Sts':
            psc_status = _PSCStatus(ps_status=value)
            value = psc_status.ioc_pwrstate
        elif field == 'OpMode-Sts':
            psc_status = _PSCStatus(ps_status=value)
            value = psc_status.ioc_opmode
        elif field == 'CtrlMode-Mon':
            psc_status = _PSCStatus(ps_status=value)
            value = psc_status.interface
        elif field == 'Version-Cte':
            version = ''.join([c.decode() for c in value])
            try:
                value, _ = version.split('\x00', 0)
            except ValueError:
                value = version

        return value

    def read_all(self):
        """Read all fields."""
        values = dict()
        for field in self.epics_2_bsmp:
            key = self.psname + ':' + field
            values[key] = self.read(field)
        for field, db in self._setpoints.items():
            key = self.psname + ':' + field
            values[key] = db['value']
        values[self.psname+':WfmData-RB'] = self.database['WfmData-RB']['value']

        return values

    def write(self, field, value):
        """Write to field."""
        func = getattr(self, IOCDevice._epics_2_wfuncs[field])
        func(value)

    # Private
    def _set_pwrstate(self, setpoint):
        """Set PwrState setpoint."""
        if setpoint == 1:
            self._bsmp_device.turn_on()
        elif setpoint == 0:
            self._bsmp_device.turn_off()
        else:
            self.setpoints['PwrState-Sel']['value'] = setpoint
            return

        self.setpoints['Current-SP']['value'] = 0.0
        self.setpoints['OpMode-Sel']['value'] = 0
        self.setpoints['PwrState-Sel']['value'] = setpoint

    def _set_opmode(self, setpoint):
        """Operation mode setter."""
        if setpoint >= 0 or \
                setpoint <= len(self.setpoints['OpMode-Sel']['enums']):
            self._bsmp_device.select_op_mode(setpoint)
            self.setpoints['OpMode-Sel']['value'] = setpoint
            if setpoint == _devc.OpMode.SlowRef:
                # disable siggen
                self._bsmp_device.disable_siggen()
                # turn PRU sync off - This is done in the BBB class
                pass
            elif setpoint == _devc.OpMode.Cycle:
                # implement actions for Cycle
                pass
            else:
                # TODO: implement actions for other modes
                pass

    def _set_current(self, setpoint):
        """Set current."""
        setpoint = max(self.setpoints['Current-SP']['lolo'], setpoint)
        setpoint = min(self.setpoints['Current-SP']['hihi'], setpoint)

        self._bsmp_device.set_slowref(setpoint)
        self.setpoints['Current-SP']['value'] = setpoint

    def _reset(self, setpoint):
        """Reset command."""
        if setpoint:
            self.setpoints['Reset-Cmd']['value'] += 1
            self._bsmp_device.reset_interlocks()

    def _abort(self, setpoint):
        if setpoint:
            self.setpoints['Reset-Cmd']['value'] += 1
            self._bsmp_device.set_opmode(_devc.OpMode.SlowRef)

    def _enable_cycle(self, setpoint):
        """Enable cycle command."""
        if setpoint:
            self.setpoints['CycleEnbl-Cmd']['value'] += 1
            self._bsmp_device.enable_siggen()

    def _disable_cycle(self, setpoint):
        """Disable cycle command."""
        if setpoint:
            self.setpoints['CycleDsbl-Cmd']['value'] += 1
            self._bsmp_device.disable_siggen()

    def _set_cycle_type(self, setpoint):
        """Set cycle type."""
        self.setpoints['CycleType-Sel']['value'] = setpoint
        # if setpoint < 0 or \
        #         setpoint > len(self.setpoints['CycleType-Sel']['enums']):
        #     return
        self._bsmp_device.cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_nr_cycles(self, setpoint):
        """Set number of cycles."""
        self.setpoints['CycleNrCycles-SP']['value'] = setpoint
        self._bsmp_device.cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_frequency(self, setpoint):
        """Set cycle frequency."""
        self.setpoints['CycleFreq-SP']['value'] = setpoint
        self._bsmp_device.cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_amplitude(self, setpoint):
        """Set cycle amplitude."""
        self.setpoints['CycleAmpl-SP']['value'] = setpoint
        self._bsmp_device.cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_offset(self, setpoint):
        """Set cycle offset."""
        self.setpoints['CycleOffset-SP']['value'] = setpoint
        return self._bsmp_device.cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_aux_params(self, setpoint):
        """Set cycle offset."""
        # trim setpoint list
        cur_sp = self.setpoints['CycleAuxParam-SP']['value']
        setpoint = setpoint[:len(cur_sp)]
        setpoint += cur_sp[len(setpoint):]
        # update setpoint
        self.setpoints['CycleAuxParam-SP']['value'] = setpoint
        return self._bsmp_device.cfg_siggen(*self._cfg_siggen_args())

    def _cfg_siggen_args(self):
        """Get cfg_siggen args and execute it."""
        args = []
        args.append(self.setpoints['CycleType-Sel']['value'])
        args.append(self.setpoints['CycleNrCycles-SP']['value'])
        args.append(self.setpoints['CycleFreq-SP']['value'])
        args.append(self.setpoints['CycleAmpl-SP']['value'])
        args.append(self.setpoints['CycleOffset-SP']['value'])
        args.append(self.setpoints['CycleAuxParam-SP']['value'])
        return args

    def _set_wfmdata_sp(self, setpoint):
        """Set wfmdata."""
        self.setpoints['WfmData-SP']['value'] = setpoint
        self.database['WfmData-RB']['value'] = setpoint
        return True


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
        # if not self._simulate:
        #     # self._controller = _IOController(_PRU(), self._psmodel)
        #     slave_ids = self._get_bsmp_slave_IDs()
        #     self._controller = _BBBController(FBPEntities(), slave_ids)
        # else:
        #     # self._controller = _IOControllerSim(_PRUSim(), self._psmodel)
        #     pass

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

    def read(self, device_name):
        """Read all device fields."""
        return self.power_supplies[device_name].read_all()

    def write(self, device_name, field, value):
        """BBB write."""
        if field == 'OpMode-Sel':
            self._set_opmode(value)
        else:
            self.power_supplies[device_name].write(field, value)

    def is_connected(self, device_name):
        """"Return connection status."""
        return self.power_supplies[device_name].connected

    def __getitem__(self, index):
        """Return corresponding power supply object."""
        if isinstance(index, int):
            return self._power_supplies[self.psnames.index(index)]
        else:
            return self._power_supplies[index]

    def __contains__(self, psname):
        """Test if psname is in psname list."""
        return psname in self._psnames

    # --- private methods ---

    def _set_opmode(self, op_mode):
        self.controller.pru_sync_stop()
        for ps in self.power_supplies.values():
            ps.write('PwrState-Sel', op_mode)
        if op_mode == 2:
            sync_mode = self.controller.SYNC.CYCLE
            return self.controller.pru_sync_start(sync_mode)

        # return self._state.set_op_mode(self)

    # def _set_opmode(self, device_name, field, value):
    #
    #     # first set sync mode to OFF so that BSMP comm can happen
    #     # TODO: In order to avoid messing with PRU sync mode the IOC should
    #     # check whether required OpMode is not already selected!
    #     success = self._set_pru_sync_slowref(device_name, field, value)
    #     if not success:
    #         _log.warning('[!!] - could not set PRU sync mode to off!')
    #
    #     if success and value == _cPS.OpMode.SlowRef:
    #         # set opmode slowref in all ps controllers.
    #         success &= self._set_bsmp_opmode(field, value)
    #     if success and value == _cPS.OpMode.Cycle:
    #         # set opmode slowref in all ps controllers.
    #         success &= self._set_bsmp_opmode(field, value)
    #         # set PRU sync mode to Cycle
    #         success &= self._set_pru_sync_cycle(device_name, field, value)
    #     elif success and value == _cPS.OpMode.RmpWfm:
    #         # set opmode slowref in all ps controllers.
    #         success &= self._set_bsmp_opmode(field, value)
    #         # set PRU sync mode to RmpWfm
    #         success = self._set_pru_sync_rmpwfm(device_name, field, value)
    #     elif success and value == _cPS.OpMode.MigWfm:
    #         # set opmode slowref in all ps controllers.
    #         success &= self._set_bsmp_opmode(field, value)
    #         # set PRU sync mode to MigWfm
    #         success = self._set_pru_sync_migwfm(device_name, field, value)
    #     return success

    # def _set_bsmp_opmode(self, field, value):
    #     success = True
    #     for ps in self._power_supplies.values():
    #         success &= ps.write(field, value)
    #     return success

    # def _set_pru_sync_slowref(self, device_name, field, value):
    #     # print('set_pru_sync_slowref!')
    #     ret = self.controller.pru.sync_stop()
    #     return ret

    # def _set_pru_sync_cycle(self, device_name, field, value):
    #     # print('set_pru_sync_cycle!')
    #     sync_mode = self.controller.pru.SYNC_CYCLE
    #     ret = self._set_pru_sync_start(sync_mode)
    #     return ret
    #     return True

    # def _set_pru_sync_rmpwfm(self, device_name, field, value):
    #     sync_mode = self.controller.pru.SYNC_RMPEND
    #     ret = self._set_pru_sync_start(sync_mode)
    #     return ret

    # def _set_pru_sync_migwfm(self, device_name, field, value):
    #     sync_mode = self.controller.pru.SYNC_MIGEND
    #     ret = self._set_pru_sync_start(sync_mode)
    #     return ret

    # def _set_pru_sync_start(self, sync_mode):
    #     slave_id = self._power_supplies[self.psnames[0]]._slave_id
    #     ret = self.controller.pru.sync_start(
    #         sync_mode=sync_mode, sync_address=slave_id)
    #     return ret

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
        self._controller = _BBBController(_FBPEntities(), slave_ids)
        power_supplies = dict()
        for i, psname in enumerate(self._psnames):
            # Define device controller
            if self._psmodel == 'FBP':
                db = _deepcopy(self._database)
                device = _FBPPowerSupply(self._controller, slave_ids[i])
                power_supplies[psname] = IOCDevice(device, psname, db)
        return power_supplies


# class BBBSlowRefState:
#
#     @staticmethod
#     def set_op_mode(bbb):
#     """Set pru to aproppriate sync mode and set op mode for all devices."""
#         bbb.controller.pru_sync_stop()
#         for ps in bbb.power_supplies:
#             ps.write('PwrState-Sel', 0)
#         return True


# class BBBCycleState:
#
#     @staticmethod
#     def set_op_mode(bbb):
#         """Set pru to cycle sync mode and set op mode to for all devices."""
#         bbb.controller.pru_sync_stop()
#         for ps in bbb.power_supplies:
#             ps.write('PwrState-Sel', 2)
#         sync_mode = bbb.controller.SYNC.CYCLE
#         return bbb.controller.pru_sync_start(sync_mode)
