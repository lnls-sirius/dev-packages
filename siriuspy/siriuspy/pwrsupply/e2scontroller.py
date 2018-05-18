"""E2SController."""
import threading as _threading
import time as _time
import numpy as _np
from collections import namedtuple as _namedtuple
from copy import deepcopy as _deepcopy

from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
# from siriuspy.pwrsupply.bsmp import FBPEntities as _FBPEntities
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.commands import CommandFactory as _CommandFactory
from siriuspy.pwrsupply.fields import VariableFactory as _VariableFactory
from siriuspy.pwrsupply.fields import Setpoint as _Setpoint
from siriuspy.pwrsupply.fields import Constant as _Constant


DeviceInfo = _namedtuple('DeviceInfo', 'name, id')


class E2SController:
    """Setpoints and field translation."""

    INTERVAL_SCAN = 1.0/_PRUController.FREQ.SCAN

    def __init__(self, controller, devices_info, model, database):
        """Init."""
        # Properties
        self._pru_controller = controller
        self._devices_info = devices_info
        self._model = model
        self._database = database

        self._initiated = False
        self._operation_mode = 0
        self._watchers = dict()
        # Data structures
        self._fields = dict()
        self._writers = dict()
        # Fill fields and writes
        self._create_fields()
        # Init setpoint values
        self._init()

    # --- public interface ---

    @property
    def database(self):
        """Device database."""
        return self._database

    @property
    def pru_controller(self):
        """PRU Controller."""
        return self._pru_controller

    def read(self, device_name, field):
        """Read field from device."""
        return self._fields[field][device_name].read()

    def read_all(self, device_name):
        """Read all fields."""
        values = dict()
        for field in self.database:
            key = device_name + ':' + field
            values[key] = self.read(device_name, field)
        return values

    def write(self, devices_names, field, value):
        """Write to value one or many devices' field."""
        devices_names = self._tuplify(devices_names)
        setpoints = [self._fields[field][dev_name]
                     for dev_name in devices_names]
        ids = tuple([setpoint.device_id
                     for setpoint in setpoints if setpoint.apply(value)])

        if field == 'OpMode-Sel':
            self._pre_opmode(devices_names, value)
            self._write(ids, field, value)
            self._pos_opmode(devices_names, value)
            return

        elif field in ('CycleType-Sel', 'CycleNrCycles-SP',
                       'CycleFreq-SP', 'CycleAmpl-SP',
                       'CycleOffset-SP', 'CycleAuxParam-SP'):
            for dev_name in devices_names:
                dev_info = self._devices_info[dev_name]
                value = self._cfg_siggen_args([dev_name])
                # print("Setting {}: {}".format(field, value))
                self._write(dev_info.id, field, value[0])
            return

        if field == 'PwrState-Sel':
            # self._write(ids, 'Current-SP', 0.0)
            for setpoint in self._fields['Current-SP'].values():
                setpoint.apply(0.0)
        elif '-Cmd' in field:
            value = None

        self._write(ids, field, value)

    def check_connected(self, device_name):
        """Connected."""
        device_id = self._devices_info[device_name].id
        return self._pru_controller.check_connected(device_id)

    # --- private methods ---

    def _write(self, ids, field, value):
        ids = self._tuplify(ids)
        if ids:
            self._writers[field].execute(ids, value)

    def _init(self):
        if not self._initiated:
            for dev_info in self._devices_info.values():
                dev_name = dev_info.name
                for field in self.database:
                    if '-Sts' in field or '-RB' in field:
                        sp_field = self._get_setpoint_field(field)
                        value = self.read(dev_name, field)
                        if value is not None:
                            self._fields[sp_field][dev_name].value = value

    @staticmethod
    def _get_setpoint_field(field):
        return field.replace('-Sts', '-Sel').replace('-RB', '-SP')

    # Watchers

    def _set_watchers(self, op_mode, devices_names):
        self._stop_watchers(devices_names)
        for dev_name in devices_names:
            t = _Watcher(self, dev_name, op_mode)
            self._watchers[dev_name] = t
            self._watchers[dev_name].start()

    def _stop_watchers(self, devices_names):
        for dev_name in devices_names:
            try:
                if self._watchers[dev_name].is_alive():
                    self._watchers[dev_name].stop()
                    self._watchers[dev_name].join()
            except KeyError:
                continue

    # Helpers

    def _create_fields(self):
        for field, db in self.database.items():
            self._fields[field] = dict()
            if _Setpoint.match(field):
                cmd = _CommandFactory.get(
                    self._model, field, self._pru_controller)
                self._writers[field] = cmd
                for device_info in self._devices_info.values():
                    self._fields[field][device_info.name] = _Setpoint(
                        device_info.name, device_info.id, field, _deepcopy(db))
            else:
                for device_info in self._devices_info.values():
                    if 'Version-Cte' == field:
                        obj = _VariableFactory.get(
                            self._model, device_info.id,
                            field, self._pru_controller)
                    elif _Constant.match(field):
                        obj = _Constant(db['value'])
                    else:
                        obj = _VariableFactory.get(
                            self._model, device_info.id,
                            field, self._pru_controller)
                    self._fields[field][device_info.name] = obj

    def _pre_opmode(self, devices_names, setpoint):
        # Execute function to set PSs operation mode
        if setpoint == _PSConst.OpMode.Cycle:
            # set SlowRef setpoint to last cycling value (offset) so that
            # magnetic history is not spoiled when power supply returns
            # automatically to SlowRef mode
            # TODO: in the general case (start and end siggen phases not
            # equal to zero) the offset parameter is not the last cycling
            # value!
            for dev_name in devices_names:
                dev_id = self._devices_info[dev_name].id
                offset_val = self.read(dev_name, 'CycleOffset-RB')
                sp = self._fields['Current-SP'][dev_name]
                if sp.apply(offset_val):
                    self._write((dev_id,), 'Current-SP', offset_val)

    def _pos_opmode(self, devices_names, setpoint):
        # Further actions that depend on op mode
        if setpoint in (_PSConst.OpMode.Cycle, _PSConst.OpMode.MigWfm,
                        _PSConst.OpMode.RmpWfm):
            self._set_watchers(setpoint, devices_names)

    def _cfg_siggen_args(self, dev_names):
        """Get cfg_siggen args and execute it."""
        values = []
        for dev_name in dev_names:
            args = []
            args.append(self._fields['CycleType-Sel'][dev_name].read())
            args.append(self._fields['CycleNrCycles-SP'][dev_name].read())
            args.append(self._fields['CycleFreq-SP'][dev_name].read())
            args.append(self._fields['CycleAmpl-SP'][dev_name].read())
            args.append(self._fields['CycleOffset-SP'][dev_name].read())
            args.extend(self._fields['CycleAuxParam-SP'][dev_name].read())
            values.append(args)
        return values

    def _tuplify(self, value):
        # Return tuple if value is not iterable
        if not hasattr(value, '__iter__') or \
                isinstance(value, str) or \
                isinstance(value, _np.ndarray) or \
                isinstance(value, DeviceInfo):
            return value,
        return value


class _Watcher(_threading.Thread):
    """Watcher PS on given operation mode."""

    INSTANCE_COUNT = 0

    WAIT_OPMODE = 0
    WAIT_TRIGGER = 1
    WAIT_CYCLE = 2
    WAIT_MIG = 3
    WAIT_RMP = 4

    WAIT = 1.0/_PRUController.FREQ.SCAN

    def __init__(self, controller, dev_name, op_mode):
        """Init thread."""
        super().__init__(daemon=True)
        self.controller = controller
        self.dev_name = dev_name
        self.op_mode = op_mode
        self.state = _Watcher.WAIT_OPMODE
        self.exit = False

    def run(self):
        _Watcher.INSTANCE_COUNT += 1
        if self.op_mode == _PSConst.OpMode.Cycle:
            self._watch_cycle()
        elif self.op_mode == _PSConst.OpMode.MigWfm:
            self._watch_mig()
        elif self.op_mode == _PSConst.OpMode.RmpWfm:
            self._watch_rmp()
        _Watcher.INSTANCE_COUNT -= 1

    def stop(self):
        """Stop thread."""
        self.exit = True

    def _watch_cycle(self):
        while True:
            if self.exit:
                break
            elif self.state == _Watcher.WAIT_OPMODE:
                if self._achieved_op_mode() and self._sync_started():
                    self.state = _Watcher.WAIT_TRIGGER
                elif self._sync_pulsed():
                    self.state = _Watcher.WAIT_CYCLE
            elif self.state == _Watcher.WAIT_TRIGGER:
                if self._changed_op_mode():
                    break
                elif self._sync_stopped():
                    if self._cycle_started() or self._sync_pulsed():
                        self.state = _Watcher.WAIT_CYCLE
                    else:
                        break
            elif self.state == _Watcher.WAIT_CYCLE:
                if self._changed_op_mode():
                    break
                elif self._cycle_stopped():
                    # self._set_current()
                    self._set_slow_ref()
                    break
            _time.sleep(_Watcher.WAIT)

    def _watch_mig(self):
        while True:
            if self.exit:
                break
            elif self.state == _Watcher.WAIT_OPMODE:
                if self._achieved_op_mode() and self._sync_started():
                    self.state = _Watcher.WAIT_MIG
            elif self.state == _Watcher.WAIT_MIG:
                if self._changed_op_mode():
                    break
                elif self._sync_stopped():
                    if self._sync_pulsed():
                        self._set_current()
                        self._set_slow_ref()
                    break
            _time.sleep(_Watcher.WAIT)

    def _watch_rmp(self):
        while True:
            if self.exit:
                break
            elif self.state == _Watcher.WAIT_OPMODE:
                if self._achieved_op_mode() and self._sync_started():
                    self.state = _Watcher.WAIT_RMP
            elif self.state == _Watcher.WAIT_RMP:
                if self._sync_stopped() or self._changed_op_mode():
                    if self._sync_pulsed():
                        self._set_current()
                    break
            _time.sleep(_Watcher.WAIT)

    def _current_op_mode(self):
        return self.controller.read(self.dev_name, 'OpMode-Sts')

    def _achieved_op_mode(self):
        return self.op_mode == self._current_op_mode()

    def _changed_op_mode(self):
        return self.op_mode != self._current_op_mode()

    def _cycle_started(self):
        return self.controller.read(
            self.dev_name, 'CycleEnbl-Mon') == 1

    def _cycle_stopped(self):
        return self.controller.read(
            self.dev_name, 'CycleEnbl-Mon') == 0

    def _sync_started(self):
        return self.controller.pru_controller.pru_sync_status == 1

    def _sync_stopped(self):
        return self.controller.pru_controller.pru_sync_status == 0

    def _sync_pulsed(self):
        return \
            self.controller.pru_controller.pru_sync_pulse_count > 0

    def _set_current(self):
        cur_sp = 'Current-SP'
        dev_name = self.dev_name
        if self.op_mode == _PSConst.OpMode.Cycle:
            val = self.controller.read(dev_name, 'CycleOffset-RB')
        else:
            val = self.controller.read(dev_name, 'WfmData-RB')[-1]
        # print('Writing {} to {}'.format(val, dev_name))
        self.controller.write(dev_name, cur_sp, val)

    def _set_slow_ref(self):
        self.controller.write(self.dev_name, 'OpMode-Sel', 0)
