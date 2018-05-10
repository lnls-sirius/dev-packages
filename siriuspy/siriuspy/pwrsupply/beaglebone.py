"""Beagle Bone implementation module."""
from copy import deepcopy as _deepcopy
import logging as _log
import re as _re
import threading as _threading
import time as _time
import numpy as _np
from collections import namedtuple as _namedtuple

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
# from siriuspy.pwrsupply.bsmp import FBPEntities as _FBPEntities
from siriuspy.pwrsupply.bsmp import Const as _c
from .status import PSCStatus as _PSCStatus
from siriuspy.csdevice.pwrsupply import Const as _PSConst


# TODO: improve code
#
# 01. try to optimize it. At this point it is taking up 80% of BBB1 CPU time.
#     from which ~20% comes from PRController. I think we could keep some kind
#     of device state mirror in E2SController such that it does not have to
#     invoke PRUController read at every device field update. This mirror state
#     could be updated in one go.


_DeviceInfo = _namedtuple('DeviceInfo', 'name, id')


class _E2SController:
    """Setpoints and field translation."""

    # Constants and Setpoint regexp patterns
    _ct = _re.compile('^.*-Cte$')
    _sp = _re.compile('^.*-(SP|Sel|Cmd)$')

    INTERVAL_SCAN = 1.0/_PRUController.FREQ.SCAN

    bsmp_2_epics = {
        _c.V_PS_STATUS: ('PwrState-Sts', 'OpMode-Sts',
                         'CtrlMode-Mon', 'OpenLoop-Mon'),
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
        'OpenLoop-Mon': _c.V_PS_STATUS,
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
        'CycleOffset-RB': _c.V_SIGGEN_OFFSET,
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

    _sync_mode = {
        _PRUController.PRU.SYNC_MODE.CYCLE: 1,
        _PRUController.PRU.SYNC_MODE.RMPEND: 2,
        _PRUController.PRU.SYNC_MODE.MIGEND: 3
    }

    def __init__(self, controller, devices_info, database):
        """Init."""
        self._pru_controller = controller
        self._devices_info = devices_info
        self._database = database
        # define and init constant and setpoint fields
        self._setpoints = dict()
        self._constants = dict()
        # self._locals = ('WfmData-RB', )
        # self._local_vars = dict()
        for device_info in devices_info.values():
            self._setpoints[device_info.name] = dict()
            self._constants[device_info.name] = dict()
            # self._local_vars[device_info.name] = dict()
        for field, db in self.database.items():
            for device_info in devices_info.values():
                if self._sp.match(field):
                    self._setpoints[device_info.name][field] = _deepcopy(db)
                elif self._ct.match(field):
                    self._constants[device_info.name][field] = _deepcopy(db)
                # elif field in self._locals:
                #     self._local_vars[device_info.name][field] = _deepcopy(db)
        self._initiated = False
        self._init()
        self._watchers = dict()

    # --- public interface ---

    @property
    def database(self):
        """Device database."""
        return self._database

    def read(self, device_name, field):
        """Read field from device."""
        if field in self._epics_2_wfuncs:
            return self._setpoints[device_name][field]['value']
        else:
            device_id = self._devices_info[device_name].id
            return self._read(device_id, field)

    def read_all(self, device_name):
        """Read all fields."""
        values = dict()
        self._read_variables(device_name, values)
        self._read_setpoints(device_name, values)
        self._read_pru(device_name, values)
        return values

    def write(self, devices_names, field, value):
        """Write to value one or many devices' field."""
        devices_names = self._tuplify(devices_names)
        if self._check_write_values(field, value):
            func = getattr(self, _E2SController._epics_2_wfuncs[field])
            devices_info = [self._devices_info[dev_name]
                            for dev_name in devices_names]
            value = self._trim_value(field, value)
            value = self._trim_array(devices_names, field, value)
            func(devices_info, value)
        else:
            _log.warning(
                'Value {} is out of range for {} field'.format(value, field))

    def check_connected(self, device_name):
        """Connected."""
        device_id = self._devices_info[device_name].id
        return self._pru_controller.check_connected(device_id)

    # --- private methods ---

    def _read(self, device_id, field):
        """Read a field."""
        if field in self.epics_2_bsmp:
            variable_id = self.epics_2_bsmp[field]
            # TODO: this is not optimized! all variables of a given device id
            # should be read at once!
            value = self._pru_controller.read_variables(device_id, variable_id)
            value = self._parse_value(field, value)
        elif field == 'WfmData-RB':
            value = self._pru_controller.pru_curve_read(device_id)
        return value

    def _init(self):
        if not self._initiated:
            for dev_info in self._devices_info.values():
                dev_name = dev_info.name
                setpoints = list()
                values = list()
                for field in self.epics_2_bsmp:
                    if '-Sts' in field or '-RB' in field:
                        setpoints.append(self._get_setpoint_field(field))
                        values.append(self.read(dev_name, field))
                self._set_setpoints(dev_info, setpoints, values)

    @staticmethod
    def _get_setpoint_field(field):
        return field.replace('-Sts', '-Sel').replace('-RB', '-SP')

    def _check_write_values(self, field, setpoint):
        if not self._sp.match(field):
            return False
        elif '-Sel' in field:
            enums = self.database[field]['enums']
            if setpoint not in tuple(range(len(enums))):
                return False
        elif '-SP' in field:
            pass
            # if 'WfmData-' == field:
            #     if len(setpoint) != self._pru_controller.pru_curve_length:
            #         return False
        elif '-Cmd' in field:
            if setpoint < 1:
                return False
        return True

    def _execute_command(self, devices_info, command, setpoints=None):
        devices_info = self._tuplify(devices_info)
        dev_ids = [dev_info.id for dev_info in devices_info]
        if setpoints is None:
            self._pru_controller.exec_functions(dev_ids, command)
        elif not hasattr(setpoints, '__iter__'):
            self._pru_controller.exec_functions(dev_ids, command, setpoints)
        else:
            for idx, dev_id in enumerate(dev_ids):
                self._pru_controller.exec_functions(
                    dev_id, command, setpoints[idx])

    def _set_setpoints(self, devices_info, fields, values):
        devices_info = self._tuplify(devices_info)
        fields = self._tuplify(fields)
        values = self._tuplify(values)
        for i, field in enumerate(fields):
            for dev_info in devices_info:
                self._setpoints[dev_info.name][field]['value'] = values[i]

    def _set_cmd_setpoints(self, devices_info, field):
        for dev_info in devices_info:
            self._setpoints[dev_info.name][field]['value'] += 1

    # Methods that execute function

    def _set_pwrstate(self, devices_info, setpoint):
        """Set PS On/Off."""
        # Execute function to devices
        if setpoint == 1:
            self._execute_command(devices_info, _c.F_TURN_ON)
            _time.sleep(0.3)  # TODO: this is already done in PRUController!
            self._execute_command(devices_info, _c.F_CLOSE_LOOP)
        elif setpoint == 0:
            self._execute_command(devices_info, _c.F_TURN_OFF)

        # Set setpoints
        fields = ('Current-SP', 'OpMode-Sel', 'PwrState-Sel')
        values = (0.0, 0, setpoint)
        self._set_setpoints(devices_info, fields, values)

    def _set_opmode(self, devices_info, setpoint):
        """Operation mode setter."""
        # TODO: this expedient 'setpoint+3' seems to be too fragile
        # against possible future modifications of ps firmware/spec.
        self._pre_opmode(devices_info, setpoint)
        self._execute_command(devices_info, _c.F_SELECT_OP_MODE, setpoint+3)
        self._set_setpoints(devices_info, 'OpMode-Sel', setpoint)
        self._pos_opmode(devices_info, setpoint)

    def _set_current(self, devices_info, setpoint):
        """Set current."""
        op_mode = self._get_opmode(devices_info[0])
        if op_mode == _PSConst.OpMode.SlowRefSync:
            self._set_slowrefsync_setpoints(devices_info, setpoint)
        else:
            self._execute_command(devices_info, _c.F_SET_SLOWREF, setpoint)
        self._set_setpoints(devices_info, 'Current-SP', setpoint)

    def _reset(self, devices_info, setpoint):
        """Reset command."""
        self._execute_command(devices_info, _c.F_RESET_INTERLOCKS)
        self._set_cmd_setpoints(devices_info, 'Reset-Cmd')

    def _abort(self, devices_info, setpoint):
        _log.warning('Abort not implemented')

    def _enable_cycle(self, devices_info, setpoint):
        """Enable cycle command."""
        self._execute_command(devices_info, _c.F_ENABLE_SIGGEN, setpoint)
        self._set_cmd_setpoints(devices_info, 'CycleEnbl-Cmd')

    def _disable_cycle(self, devices_info, setpoint):
        """Disable cycle command."""
        self._execute_command(devices_info, _c.F_DISABLE_SIGGEN, setpoint)
        self._set_cmd_setpoints(devices_info, 'CycleDsbl-Cmd')

    def _set_cycle_type(self, devices_info, setpoint):
        """Set cycle type."""
        self._set_setpoints(devices_info, 'CycleType-Sel', setpoint)
        values = self._cfg_siggen_args(devices_info)
        self._execute_command(devices_info, _c.F_CFG_SIGGEN, values)

    def _set_cycle_nr_cycles(self, devices_info, setpoint):
        """Set number of cycles."""
        self._set_setpoints(devices_info, 'CycleNrCycles-SP', setpoint)
        values = self._cfg_siggen_args(devices_info)
        self._execute_command(devices_info, _c.F_CFG_SIGGEN, values)

    def _set_cycle_frequency(self, devices_info, setpoint):
        """Set cycle frequency."""
        self._set_setpoints(devices_info, 'CycleFreq-SP', setpoint)
        values = self._cfg_siggen_args(devices_info)
        self._execute_command(devices_info, _c.F_CFG_SIGGEN, values)

    def _set_cycle_amplitude(self, devices_info, setpoint):
        """Set cycle amplitude."""
        self._set_setpoints(devices_info, 'CycleAmpl-SP', setpoint)
        values = self._cfg_siggen_args(devices_info)
        self._execute_command(devices_info, _c.F_CFG_SIGGEN, values)

    def _set_cycle_offset(self, devices_info, setpoint):
        """Set cycle offset."""
        self._set_setpoints(devices_info, 'CycleOffset-SP', setpoint)
        values = self._cfg_siggen_args(devices_info)
        self._execute_command(devices_info, _c.F_CFG_SIGGEN, values)

    def _set_cycle_aux_params(self, devices_info, setpoint):
        """Set cycle offset."""
        self._set_setpoints(devices_info, 'CycleAuxParam-SP', [setpoint])
        values = self._cfg_siggen_args(devices_info)
        self._execute_command(devices_info, _c.F_CFG_SIGGEN, values)

    def _set_wfmdata_sp(self, devices_info, setpoint):
        """Set wfmdata."""
        self._set_setpoints(devices_info, 'WfmData-SP', [setpoint])
        for dev_info in devices_info:
            self._pru_controller.pru_curve_write(dev_info.id, setpoint)
        return True

    # Watchers

    def _watcher(self, op_mode):
        # Return watcher target method
        if op_mode == _PSConst.OpMode.Cycle:
            return self._watch_cycle
        elif op_mode == _PSConst.OpMode.MigWfm:
            return self._watch_mig

    def _set_watchers(self, op_mode, devices_info):
        self._watchers.clear()
        for dev_info in devices_info:
            t = _threading.Thread(
                target=self._watcher(op_mode), args=(dev_info, ), daemon=True)
            try:
                if self._watchers[dev_info.id].is_alive():
                    self._watchers[dev_info.id].join()
            except KeyError:
                pass
            self._watchers[dev_info.id] = t
            self._watchers[dev_info.id].start()

    def _watch_cycle(self, dev_info):
        _time.sleep(0.5)
        dev_name = dev_info.name
        if self.read(dev_name, 'PwrState-Sts') == 0:
            return

        state = 'wait_trigger'

        while True:
            if state == 'wait_trigger':
                if self.read(dev_name, 'OpMode-Sts') != _PSConst.OpMode.Cycle:
                    break
                elif self._pru_controller.pru_sync_status != 1:
                    if not self.read(dev_name, 'CycleEnbl-Mon'):
                        break
                    state = 'wait_cycle'
            elif state == 'wait_cycle':
                if self.read(dev_name, 'OpMode-Sts') != _PSConst.OpMode.Cycle:
                    break
                elif not self.read(dev_name, 'CycleEnbl-Mon'):
                    self._set_opmode([dev_info], 0)
                    break
            _time.sleep(_E2SController.INTERVAL_SCAN)

        return

    def _watch_mig(self, dev_info):
        _time.sleep(0.5)
        dev_name = dev_info.name
        if self.read(dev_name, 'PwrState-Sts') == 0:
            return

        while True:
            if self.read(dev_name, 'OpMode-Sts') != _PSConst.OpMode.MigWfm:
                break
            elif self._pru_controller.pru_sync_status != 1:
                if self._pru_controller.pru_sync_pulse_count > 0:
                    wfmdata = self.read(dev_info.name, 'WfmData-RB')
                    self._execute_command(
                       [dev_info], _c.F_SET_SLOWREF, wfmdata[-1])
                    self._set_setpoints([dev_info], 'Current-SP', wfmdata[-1])
                    self._set_opmode([dev_info], 0)
                break
            _time.sleep(_E2SController.INTERVAL_SCAN)
        return

    # Helpers

    def _get_opmode(self, device_info):
        return self.read(device_info.name, 'OpMode-Sts')

    def _pre_opmode(self, devices_info, setpoint):
        # Execute function to set PSs operation mode
        if setpoint == _PSConst.OpMode.Cycle:
            # set SlowRef setpoint to last cycling value (offset) so that
            # magnetic history is not spoiled when power supply returns
            # automatically to SlowRef mode
            # TODO: in the general case (start and end siggen phases not
            # equal to zero) the offset parameter is not the last cycling
            # value!
            for device_info in devices_info:
                offset_val = self.read(device_info.name, 'CycleOffset-RB')
                self._execute_command(
                    [device_info], _c.F_SET_SLOWREF, offset_val)
                self._set_setpoints([device_info], 'Current-SP', offset_val)
        elif setpoint in (_PSConst.OpMode.RmpWfm, _PSConst.OpMode.MigWfm):
            pass
            # for device_info in devices_info:
            #    wfmdata = self.read(device_info.name, 'WfmData-RB')
            #    self._execute_command(
            #        [device_info], _c.F_SET_SLOWREF, wfmdata[-1])
            #    self._set_setpoints([device_info], 'Current-SP', wfmdata[-1])
        elif setpoint == _PSConst.OpMode.SlowRefSync:
            self._set_slowrefsync_setpoints()

    def _pos_opmode(self, devices_info, setpoint):
        # Further actions that depend on op mode
        if setpoint == _PSConst.OpMode.SlowRef:
            # disable siggen
            self._execute_command(devices_info, _c.F_DISABLE_SIGGEN)
        elif setpoint in (_PSConst.OpMode.Cycle, _PSConst.OpMode.MigWfm):
            self._set_watchers(setpoint, devices_info)
        else:
            # TODO: implement actions for other modes
            pass

    def _cfg_siggen_args(self, devices_info):
        """Get cfg_siggen args and execute it."""
        values = []
        for dev_info in devices_info:
            args = []
            dev_name = dev_info.name
            args.append(self._setpoints[dev_name]['CycleType-Sel']['value'])
            args.append(self._setpoints[dev_name]['CycleNrCycles-SP']['value'])
            args.append(self._setpoints[dev_name]['CycleFreq-SP']['value'])
            args.append(self._setpoints[dev_name]['CycleAmpl-SP']['value'])
            args.append(self._setpoints[dev_name]['CycleOffset-SP']['value'])
            args.extend(self._setpoints[dev_name]['CycleAuxParam-SP']['value'])
            values.append(args)
        return values

    def _get_dev_ids(self, devices_info):
        return [dev_info.id for dev_info in devices_info]

    def _parse_value(self, field, value):
        if field == 'PwrState-Sts':
            psc_status = _PSCStatus(ps_status=value)
            value = psc_status.ioc_pwrstate
        elif field == 'OpenLoop-Mon':
            psc_status = _PSCStatus(ps_status=value)
            value = psc_status.open_loop
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

    def _trim_value(self, field, setpoint):
        # TODO: generalize method so that it accept limit-checking for arrays,
        # such as WfmData-SP, for example.
        try:
            low = self.database[field]['lolo']
            high = self.database[field]['hihi']
        except KeyError:
            pass
        else:
            setpoint = max(low, setpoint)
            setpoint = min(high, setpoint)
        return setpoint

    def _trim_array(self, device_names, field, setpoint):
        # TODO: rething method.
        return setpoint
        try:  # TODO: fix
            self.database[field]['count']
        except KeyError:
            pass
        else:
            sp = self._setpoints[device_names][field]['value']
            setpoint = setpoint[:len(sp)]
            setpoint += sp[len(setpoint):]
        return setpoint

    def _read_variables(self, device_name, values):
        device_id = self._devices_info[device_name].id
        for field in self.epics_2_bsmp:
            key = device_name + ':' + field
            values[key] = self._read(device_id, field)

    def _read_setpoints(self, device_name, values):
        for field, db in self._setpoints[device_name].items():
            key = device_name + ':' + field
            values[key] = db['value']

    def _read_pru(self, device_name, values):
        if not self._pru_controller.pru_sync_status:
            values[device_name + ':PRUSyncMode-Mon'] = 0
        else:
            mode = self._sync_mode[self._pru_controller.pru_sync_mode]
            values[device_name + ':PRUSyncMode-Mon'] = mode
        values[device_name + ':PRUBlockIndex-Mon'] = \
            self._pru_controller.pru_curve_block
        values[device_name + ':PRUSyncPulseCount-Mon'] = \
            self._pru_controller.pru_sync_pulse_count
        values[device_name + ':PRUCtrlQueueSize-Mon'] = \
            self._pru_controller.queue_length
        _, dev_id = self._devices_info[device_name]
        values[device_name + ':WfmData-RB'] = \
            self._pru_controller.pru_curve_read(dev_id)

    def _set_slowrefsync_setpoints(self, devices_info=(), setpoint=None):
        setpoints = []
        for dev_info in self._devices_info.values():
            if dev_info in devices_info:
                setpoints.append(setpoint)
            else:
                cur_sp = self.read(dev_info.name, 'Current-SP')
                setpoints.append(cur_sp)
        self._pru_controller.pru_curve_write_slowref_sync(setpoints)

    def _tuplify(self, value):
        # Return tuple if value is not iterable
        if not hasattr(value, '__iter__') or \
                isinstance(value, str) or \
                isinstance(value, _np.ndarray) or \
                isinstance(value, _DeviceInfo):
            return value,
        return value


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
        if self._bbbname == 'BO-01:CO-BBB-1':
            self._psnames = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        elif self._bbbname == 'BO-01:CO-BBB-2':
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
        if self._bbbname == 'BO-01:CO-BBB-1':
            # test-bench BBB # 1
            return (1, 2)
        elif self._bbbname == 'BO-01:CO-BBB-2':
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
