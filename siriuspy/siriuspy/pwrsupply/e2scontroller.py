"""E2SController."""
import numpy as _np
import re as _re
import time as _time
import threading as _threading

from collections import namedtuple as _namedtuple
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.prucontroller import PRUCParms_FBP as _PRUCParms_FBP
from siriuspy.pwrsupply.bsmp import ConstBSMP as _c
from siriuspy.pwrsupply.commands import PSOpMode as _PSOpMode
from siriuspy.pwrsupply.commands import Function as _Function


class PSController:
    """This class is used to communicate with PS controller.

    PRUController
    Fields method property holds objects trant translate EPICS fields to a BSMP
    variable.

    [List] devices_info, [dict] database -> [List] DevicesSetpoints
    [string] model -> PRUController
    [List] devices_info, [dict] database, [PRUController] controller
            -> [Commands List] writers
    [List] devices_info, [dict] database, [PRUController] controller
            -> [Fields List] variables
    """

    def __init__(self, readers, writers, connections):
        """Create class properties."""
        self._readers = readers
        self._writers = writers
        self._connections = connections

        self._fields = set()
        # self._devices = set()
        for name in self._readers:
            split = name.split(':')
            self._fields.add(split[-1])
            # self._devices.add(':'.join(split[:2]))

        # self._operation_mode = 0

    def read(self, device_name, field):
        """Read pv value."""
        return self._readers[device_name + ':' + field].read()

    def read_all_fields(self, device_name):
        """Read all fields value from device."""
        values = dict()
        for field in self._fields:
            values[device_name + ':' + field] = self.read(device_name, field)
        return values

    def write(self, device_name, field, value):
        """Write value to pv."""
        self._writers[device_name + ':' + field].execute(value)

    def check_connected(self, device_name):
        """Check if device is connected."""
        return self._connections[device_name].connected()


class StandardPSController(PSController):
    """Standard behaviour for a PSController."""
    INTERVAL_SCAN = 1.0/_PRUCParms_FBP.FREQ_SCAN

    def __init__(self, readers, writers, connections, devices, pru_controller):
        """Call super."""
        super().__init__(readers, writers, connections)
        self._devices = devices
        self._pru_controller = pru_controller
        self._watchers = dict()

    @property
    def pru_controller(self):
        """PRU Controller."""
        return self._pru_controller

    def read(self, device_name, field):
        """Read pv value."""
        if field == 'OpMode-Sts':
            try:
                if self._watchers[device_name].is_alive():
                    return self._watchers[device_name].op_mode
            except KeyError:
                pass
            # op_mode = self._readers[device_name + ':' + field].read()
            # if op_mode == 0:
            #     return self._operation_mode
            # else:
            #     return op_mode
        return self._readers[device_name + ':' + field].read()

    def write(self, device_name, field, value):
        """Override write method."""
        name = device_name + ':' + field
        if field == 'OpMode-Sel':
            writer = self._writers[device_name + ':' + field]
            # if value in (0, 3, 4):
            #     self._operation_mode = value
            self._set_opmode(writer, value)
        elif field == 'CycleType-SP':
            values = self._cfg_siggen_args(device_name)
            values[0] = value
            self._writers[device_name + ':' + field].execute(values)
        elif field == 'CycleNrCycles-SP':
            values = self._cfg_siggen_args(device_name)
            values[1] = value
            self._writers[device_name + ':' + field].execute(values)
        elif field == 'CycleFreq-SP':
            values = self._cfg_siggen_args(device_name)
            values[2] = value
            self._writers[device_name + ':' + field].execute(values)
        elif field == 'CycleAmpl-SP':
            values = self._cfg_siggen_args(device_name)
            values[3] = value
            self._writers[device_name + ':' + field].execute(values)
        elif field == 'CycleOffset-SP':
            values = self._cfg_siggen_args(device_name)
            values[4] = value
            self._writers[device_name + ':' + field].execute(values)
        elif field == 'CycleAuxParam-SP':
            values = self._cfg_siggen_args(device_name)
            values[5] = value
            self._writers[device_name + ':' + field].execute(values)
        elif field == 'PwrState-Sel':
            self._readers[device_name + ':Current-SP'].apply(0.0)
            self._writers[name].execute(value)
        else:
            self._writers[name].execute(value)

    # Private
    def _set_watchers(self, op_mode):
        self._stop_watchers()
        for dev_name in self._devices:
            dev_ids = [self._devices[dev_name]]
            writers = dict()
            writers['Current-SP'] = self._writers[dev_name + ':Current-SP']
            writers['OpMode-Sel'] = _PSOpMode(
                dev_ids,
                _Function(dev_ids, self._pru_controller, _c.F_SELECT_OP_MODE),
                self._readers[dev_name + ':OpMode-Sel'])

            t = _Watcher(writers, self, dev_name, op_mode)
            self._watchers[dev_name] = t
            self._watchers[dev_name].start()

    def _stop_watchers(self):
        for dev_name in self._devices:
            try:
                if self._watchers[dev_name].is_alive():
                    self._watchers[dev_name].stop()
                    self._watchers[dev_name].join()
            except KeyError:
                continue

    def _pre_opmode(self, setpoint):
        # Execute function to set PSs operation mode
        if setpoint == _PSConst.OpMode.Cycle:
            # set SlowRef setpoint to last cycling value (offset) so that
            # magnetic history is not spoiled when power supply returns
            # automatically to SlowRef mode
            # TODO: in the general case (start and end siggen phases not
            # equal to zero) the offset parameter is not the last cycling
            # value!
            for dev_name in self._devices:
                offset_val = self.read(dev_name, 'CycleOffset-RB')
                self.write(dev_name, 'Current-SP', offset_val)

    def _pos_opmode(self, setpoint):
        # Further actions that depend on op mode
        if setpoint in (_PSConst.OpMode.Cycle, _PSConst.OpMode.MigWfm,
                        _PSConst.OpMode.RmpWfm):
            self._set_watchers(setpoint)

    def _set_opmode(self, writer, op_mode):
        self._pru_controller.pru_sync_stop()
        self._pre_opmode(op_mode)
        writer.execute(op_mode)
        self._pos_opmode(op_mode)
        if op_mode == _PSConst.OpMode.Cycle:
            sync_mode = self._pru_controller.params.PRU.SYNC_MODE.BRDCST
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.RmpWfm:
            sync_mode = self._pru_controller.params.PRU.SYNC_MODE.RMPEND
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.MigWfm:
            sync_mode = self._pru_controller.params.PRU.SYNC_MODE.MIGEND
            return self._pru_controller.pru_sync_start(sync_mode)

    def _cfg_siggen_args(self, device_name):
        """Get cfg_siggen args and execute it."""
        args = []
        args.append(self._readers[device_name + ':CycleType-Sel'].read())
        args.append(self._readers[device_name + ':CycleNrCycles-SP'].read())
        args.append(self._readers[device_name + ':CycleFreq-SP'].read())
        args.append(self._readers[device_name + ':CycleAmpl-SP'].read())
        args.append(self._readers[device_name + ':CycleOffset-SP'].read())
        args.extend(self._readers[device_name + ':CycleAuxParam-SP'].read())
        return args


# # --- private methods ---
# def _create_setpoints(self):
#     """Create setpoints."""
#     self._setpoints = dict()
#     for device_info in self._devices_info.values():
#         self._setpoints[device_info.name] = \
#             _DeviceSetpoints(self._database)
#
# def _init_setpoints(self):
#     if not self._initiated:
#         for dev_info in self._devices_info.values():
#             dev_name = dev_info.name
#             setpoints = self._setpoints[dev_name]
#             for field in self._database:
#                 if '-Sts' in field or '-RB' in field:
#                     sp_field = self._get_setpoint_field(field)
#                     value = self.e2s_controller.read(dev_name, field)
#                     if value is not None:
#                         setpoints.set(sp_field, value)
# @staticmethod
# def _get_setpoint_field(field):
#     return field.replace('-Sts', '-Sel').replace('-RB', '-SP')


class _Watcher(_threading.Thread):
    """Watcher PS on given operation mode."""

    INSTANCE_COUNT = 0

    WAIT_OPMODE = 0
    WAIT_TRIGGER = 1
    WAIT_CYCLE = 2
    WAIT_MIG = 3
    WAIT_RMP = 4

    def __init__(self, writers, controller, dev_name, op_mode):
        """Init thread."""
        super().__init__(daemon=True)
        self.writers = writers
        self.controller = controller
        self.dev_name = dev_name
        self.op_mode = op_mode
        self.wait = 1.0/controller.pru_controller.params.FREQ_SCAN
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
                elif self._cycle_started() and self._sync_pulsed():
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
            _time.sleep(self.wait)

    def _watch_mig(self):
        while True:
            if self.exit:
                break
            elif self.state == _Watcher.WAIT_OPMODE:
                if self._achieved_op_mode() and self._sync_started():
                    self.state = _Watcher.WAIT_MIG
            elif self.state == _Watcher.WAIT_MIG:
                if self._sync_stopped() or self._changed_op_mode():
                    if self._sync_pulsed():
                        self._set_current()
                        self._set_slow_ref()
                    break
            _time.sleep(self.wait)

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
            _time.sleep(self.wait)

    def _current_op_mode(self):
        return self.controller.read(self.dev_name, 'OpMode-Sts')

    def _achieved_op_mode(self):
        return self.op_mode == self._current_op_mode()

    def _changed_op_mode(self):
        return self.op_mode != self._current_op_mode()

    def _cycle_started(self):
        return self.controller.read(self.dev_name, 'CycleEnbl-Mon') == 1

    def _cycle_stopped(self):
        return self.controller.read(self.dev_name, 'CycleEnbl-Mon') == 0

    def _sync_started(self):
        return self.controller.pru_controller.pru_sync_status == 1

    def _sync_stopped(self):
        return self.controller.pru_controller.pru_sync_status == 0

    def _sync_pulsed(self):
        return self.controller.pru_controller.pru_sync_pulse_count > 0

    def _set_current(self):
        # cur_sp = 'Current-SP'
        dev_name = self.dev_name
        if self.op_mode == _PSConst.OpMode.Cycle:
            val = self.controller.read(dev_name, 'CycleOffset-RB')
        else:
            val = self.controller.read(dev_name, 'WfmData-RB')[-1]
        # self.setpoints[dev_name + ':' + cur_sp].apply(val)
        self.writers['Current-SP'].execute(val)

    def _set_slow_ref(self):
        # self.setpoints[dev_name + ':' + field].apply(value)
        # self.controller.write(dev_name, field, value)
        self.writers['OpMode-Sel'].execute(0)
        # self.controller.write(self.dev_name, 'OpMode-Sel', 0)
