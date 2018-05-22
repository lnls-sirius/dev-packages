"""Beagle Bone implementation module."""
import time as _time
import threading as _threading
from copy import deepcopy as _deepcopy

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
from siriuspy.pwrsupply.e2scontroller \
    import E2SController as _E2SController
from siriuspy.pwrsupply.e2scontroller \
    import DeviceInfo as _DeviceInfo
from siriuspy.pwrsupply.fields import Setpoint as _Setpoint

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
        self._watchers = dict()
        self._initiated = False
        self._operation_mode = 0
        self._create_e2s_controller()
        self._create_setpoints()
        self._init_setpoints()
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
        # Change op_mode sts
        op_mode = field_values[device_name + ':' + 'OpMode-Sts']
        if op_mode == 0:
            field_values[device_name + ':' + 'OpMode-Sts'] = \
                self._operation_mode
        # field_values = self.power_supplies[device_name].read_all()
        setpoints = self._setpoints[device_name]
        for field in setpoints.fields():
            field_values[device_name + ':' + field] = setpoints.get(field)

        return field_values

    def write(self, device_name, field, value):
        """BBB write."""
        setpoints = self._setpoints[device_name]
        if field == 'OpMode-Sel':
            self._set_opmode(value)
        elif field in ('CycleType-Sel', 'CycleNrCycles-SP',
                       'CycleFreq-SP', 'CycleAmpl-SP',
                       'CycleOffset-SP', 'CycleAuxParam-SP'):
            if setpoints.set(field, value):
                value = self._cfg_siggen_args(device_name)
                self.e2s_controller.write(device_name, field, value)
        elif field == 'PwrState-Sel':
            if setpoints.set(field, value):
                setpoints.set('Current-SP', 0.0)
                self.e2s_controller.write(device_name, field, value)
        elif '-Cmd' in field:
            if setpoints.set(field, value):
                self.e2s_controller.write(device_name, field, None)
        else:
            if setpoints.set(field, value):
                self.e2s_controller.write(device_name, field, value)

    def check_connected(self, device_name):
        """"Return connection status."""
        return self._e2s_controller.check_connected(device_name)

    # --- private methods ---
    def _set_watchers(self, op_mode, devices_names):
        self._stop_watchers(devices_names)
        for dev_name in devices_names:
            t = _Watcher(self._setpoints[dev_name],
                         self.e2s_controller, dev_name, op_mode)
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
                setpoints = self._setpoints[dev_name]
                offset_val = \
                    self.e2s_controller.read(dev_name, 'CycleOffset-RB')
                if setpoints.set('Current-SP', offset_val):
                    self.e2s_controller.write(
                        dev_name, 'Current-SP', offset_val)

    def _pos_opmode(self, devices_names, setpoint):
        # Further actions that depend on op mode
        if setpoint in (_PSConst.OpMode.Cycle, _PSConst.OpMode.MigWfm,
                        _PSConst.OpMode.RmpWfm):
            self._set_watchers(setpoint, devices_names)

    def _set_opmode(self, op_mode):
        self._pru_controller.pru_sync_stop()  # TODO: not necessary. test.
        # self._restore_wfm()
        psnames = [psname for psname in self.psnames
                   if self._setpoints[psname].set('OpMode-Sel', op_mode)]
        self._pre_opmode(psnames, op_mode)
        if op_mode in (0, 3, 4):
            self._operation_mode = op_mode
            self.e2s_controller.write_to_many(psnames, 'OpMode-Sel', 0)
        else:
            self.e2s_controller.write_to_many(psnames, 'OpMode-Sel', op_mode)
        self._pos_opmode(psnames, op_mode)
        if op_mode == _PSConst.OpMode.Cycle:
            sync_mode = self._pru_controller.PRU.SYNC_MODE.BRDCST
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.RmpWfm:
            sync_mode = self._pru_controller.PRU.SYNC_MODE.RMPEND
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.MigWfm:
            sync_mode = self._pru_controller.PRU.SYNC_MODE.MIGEND
            return self._pru_controller.pru_sync_start(sync_mode)

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
            self._pru_controller, self._devices_info, 'FBP', db)

    def _cfg_siggen_args(self, device_name):
        """Get cfg_siggen args and execute it."""
        setpoints = self._setpoints[device_name]
        args = []
        args.append(setpoints.get('CycleType-Sel'))
        args.append(setpoints.get('CycleNrCycles-SP'))
        args.append(setpoints.get('CycleFreq-SP'))
        args.append(setpoints.get('CycleAmpl-SP'))
        args.append(setpoints.get('CycleOffset-SP'))
        args.extend(setpoints.get('CycleAuxParam-SP'))
        return args

    def _create_setpoints(self):
        """Create setpoints."""
        self._setpoints = dict()
        for device_info in self._devices_info.values():
            self._setpoints[device_info.name] = \
                _DeviceSetpoints(self._database)

    def _init_setpoints(self):
        if not self._initiated:
            for dev_info in self._devices_info.values():
                dev_name = dev_info.name
                setpoints = self._setpoints[dev_name]
                for field in self._database:
                    if '-Sts' in field or '-RB' in field:
                        sp_field = self._get_setpoint_field(field)
                        value = self.e2s_controller.read(dev_name, field)
                        if value is not None:
                            setpoints.set(sp_field, value)

    @staticmethod
    def _get_setpoint_field(field):
        return field.replace('-Sts', '-Sel').replace('-RB', '-SP')


class _DeviceSetpoints:
    """Structure that holds a device setpoints."""

    def __init__(self, database, device_name=None):
        """Create setpoints."""
        self._device_name = device_name
        self._database = database
        self._setpoints = dict()
        # Create setpoints
        for field, db in self._database.items():
            if _Setpoint.match(field):
                self._setpoints[field] = _Setpoint(field, _deepcopy(db))

    def get(self, field):
        """Get setpoint value."""
        return self._setpoints[field].value

    def set(self, field, value):
        """Set setpoint value."""
        return self._setpoints[field].apply(value)

    def fields(self):
        """Return fields."""
        return self._setpoints.keys()


class _Watcher(_threading.Thread):
    """Watcher PS on given operation mode."""

    INSTANCE_COUNT = 0

    WAIT_OPMODE = 0
    WAIT_TRIGGER = 1
    WAIT_CYCLE = 2
    WAIT_MIG = 3
    WAIT_RMP = 4

    WAIT = 1.0/_PRUController.FREQ.SCAN

    def __init__(self, setpoints, controller, dev_name, op_mode):
        """Init thread."""
        super().__init__(daemon=True)
        self.setpoints = setpoints
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
        return self.controller.read(self.dev_name, 'CycleEnbl-Mon') == 1

    def _cycle_stopped(self):
        return self.controller.read(self.dev_name, 'CycleEnbl-Mon') == 0

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
        self.setpoints.set(cur_sp, val)
        self.controller.write(dev_name, cur_sp, val)

    def _set_slow_ref(self):
        dev_name = self.dev_name
        field = 'OpMode-Sel'
        value = 0
        self.setpoints.set(field, value)
        self.controller.write(dev_name, field, value)
        # self.controller.write(self.dev_name, 'OpMode-Sel', 0)
