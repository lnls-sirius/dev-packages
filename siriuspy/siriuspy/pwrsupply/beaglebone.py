"""Beagle Bone implementation module."""
import time as _time
import re as _re
import threading as _threading
from copy import deepcopy as _deepcopy

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.prucontroller import PRUCQueue as _PRUCQueue
from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
from siriuspy.pwrsupply.e2scontroller import E2SController as _E2SController
from siriuspy.pwrsupply.e2scontroller import DeviceInfo as _DeviceInfo

# NOTE on current behaviour of BeagleBone:
#
# 01. While in RmpWfm, MigWfm or SlowRefSync, the PS_I_LOAD variable read from
#     power supplies after setting the last curve point may not be the
#     final value given by PS_REFERENCE. This is due to the fact that the
#     power supply control loop takes some time to converge and the PRU may
#     block serial comm. before it. This is evident in SlowRefSync mode, where
#     reference values may change considerably between two setpoints.
#     (see identical note in PRUController)

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

    All power supplies under a BBB must share the same PS model and database.

    Manages the devices setpoints.
    Uses E2SController to read variable and execute function from a BSMP device
    given the PV field name.
    """

    def __init__(self, bbbname, simulate=False):
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
        elif self._bbbname == 'AS-Glob:CO-PSCtrl-2':
            self._psnames = ['AS-Glob:PS-DCLinkFBP-2']
        elif self._bbbname == 'BBBS_TEST':
            self._psnames = ['BO-01U:PS-CH', 'BO-01U:PS-CV',
                             'BO-03U:PS-CH', 'BO-03U:PS-CV']

        else:
            # self._psnames = _PSSearch.conv_bbbname_2_psnames(bbbname)
            bsmps = _PSSearch.conv_bbbname_2_bsmps(bbbname)
            self._psnames = [bsmp[0] for bsmp in bsmps]
            self._device_ids = (bsmp[1] for bsmp in bsmps)

        # retrieve power supply model and corresponding database
        self._psmodel = _PSSearch.conv_psname_2_psmodel(self._psnames[0])
        self._database = _PSData(self._psnames[0]).propty_database

        # create abstract power supply objects
        # self._power_supplies = self._create_power_supplies()
        self._watchers = dict()
        self._initiated = False
        # self._operation_mode = 0
        self._create_e2s_controller()
        self._create_setpoints()
        self._init_setpoints()

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

    def read(self, device_name, field=None):
        """Read all device fields."""
        if field is None:
            field_values = self._e2s_controller.read_all(device_name)
            # Change op_mode sts
            # op_mode = field_values[device_name + ':' + 'OpMode-Sts']
            # if op_mode == 0:
            #     field_values[device_name + ':' + 'OpMode-Sts'] = \
            #         self._operation_mode
            # field_values = self.power_supplies[device_name].read_all()
            setpoints = self._setpoints[device_name]
            for field in setpoints.fields():
                field_values[device_name + ':' + field] = setpoints.get(field)

            return field_values
        else:
            return self._e2s_controller.read(device_name, field)

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
                if 'Current-SP' in self._database:
                    setpoints.set('Current-SP', 0.0)
                if 'VoltageGain-SP' in self._database:
                    setpoints.set('VoltageGain-SP', 0.0)
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
        # if op_mode in (0, 3, 4):
        #     self._operation_mode = op_mode
        #     self.e2s_controller.write_to_many(psnames, 'OpMode-Sel', 0)
        # else:
        #     self.e2s_controller.write_to_many(psnames, 'OpMode-Sel', op_mode)
        self.e2s_controller.write_to_many(psnames, 'OpMode-Sel', op_mode)
        self._pos_opmode(psnames, op_mode)
        if op_mode == _PSConst.OpMode.Cycle:
            sync_mode = self._pru_controller.params.PRU.SYNC_MODE.BRDCST
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.RmpWfm:
            sync_mode = self._pru_controller.params.PRU.SYNC_MODE.RMPEND
            return self._pru_controller.pru_sync_start(sync_mode)
        elif op_mode == _PSConst.OpMode.MigWfm:
            sync_mode = self._pru_controller.params.PRU.SYNC_MODE.MIGEND
            return self._pru_controller.pru_sync_start(sync_mode)

    def _get_bsmp_slave_IDs(self):
        # TODO: temp code. this should be deleted once PS bench tests are over.
        if self._bbbname == 'BO-01:CO-PSCtrl-1':
            # test-bench BBB # 1
            return (1, 2)
        elif self._bbbname == 'BO-01:CO-PSCtrl-2':
            # test-bench BBB # 2
            return (5, 6)
        elif self._bbbname == 'AS-Glob:CO-PSCtrl-2':
            return (20, )
        elif self._bbbname == 'BBBS_TEST':
            return (1, 2, 5, 6)
        else:
            return self._device_ids

    def _create_e2s_controller(self):
        # Return dict of power supply objects
        slave_ids = self._get_bsmp_slave_IDs()
        if self._simulate:
            pru = _PRUSim()
        else:
            pru = _PRU()
        prucqueue = _PRUCQueue()
        self._pru_controller = _PRUController(pru, prucqueue,
                                              self._psmodel, slave_ids)
        # TODO: delete this test code line
        if self._bbbname == 'BBBS_TEST':
            self._pru_controller2 = _PRUController(pru, prucqueue,
                                                   'FBP_DCLink', (20,))

        for i, psname in enumerate(self._psnames):
            self._devices_info[psname] = _DeviceInfo(psname, slave_ids[i])
        db = _deepcopy(self._database)
        self._e2s_controller = _E2SController(
            self._pru_controller, self._devices_info, self._psmodel, db)

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


class _Setpoint:
    """Setpoint."""

    _setpoint_regexp = _re.compile('^.*-(SP|Sel|Cmd)$')

    def __init__(self, epics_field, epics_database):
        """Init."""
        self.field = epics_field
        self.value = epics_database['value']
        self.database = epics_database
        if '-Cmd' in epics_field:
            self.is_cmd = True
        else:
            self.is_cmd = False
        self.type = epics_database['type']
        if 'count' in epics_database:
            self.count = epics_database['count']
        else:
            self.count = None
        if self.type == 'enum' and 'enums' in epics_database:
            self.enums = epics_database['enums']
        else:
            self.enums = None
        self.value = epics_database['value']
        if self.type in ('int', 'float'):
            if 'hihi' in epics_database:
                self.high = epics_database['hihi']
            else:
                self.high = None
            if 'lolo' in epics_database:
                self.low = epics_database['lolo']
            else:
                self.low = None
        else:
            self.low = None
            self.high = None

    def apply(self, value):
        """Apply setpoint value."""
        if self.check(value):
            if self.is_cmd:
                self.value += 1
            else:
                self.value = value
            return True
        return False

    def check(self, value):
        """Check value."""
        if self.is_cmd:
            if value > 0:
                return True
        elif self.type in ('int', 'float'):
            if self.low is None and self.high is None:
                return True
            if value is not None and (value > self.low and value < self.high):
                return True
        elif self.type == 'enum':
            if value in tuple(range(len(self.enums))):
                return True
        return False

    @staticmethod
    def match(field):
        """Check if field is a setpoint."""
        return _Setpoint._setpoint_regexp.match(field)


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

    def __init__(self, setpoints, controller, dev_name, op_mode):
        """Init thread."""
        super().__init__(daemon=True)
        self.setpoints = setpoints
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
        cur_sp = 'Current-SP'
        dev_name = self.dev_name
        if self.op_mode == _PSConst.OpMode.Cycle:
            val = self.controller.read(dev_name, 'CycleOffset-RB')
        else:
            val = self.controller.read(dev_name, 'WfmData-RB')[-1]
        self.setpoints.set(cur_sp, val)
        self.controller.write(dev_name, cur_sp, val)

    def _set_slow_ref(self):
        dev_name = self.dev_name
        field = 'OpMode-Sel'
        value = 0
        self.setpoints.set(field, value)
        self.controller.write(dev_name, field, value)
        # self.controller.write(self.dev_name, 'OpMode-Sel', 0)
