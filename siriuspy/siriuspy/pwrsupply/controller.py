"""E2SController."""
from siriuspy.csdevice.pwrsupply import Const as _PSConst
# from siriuspy.pwrsupply.model_factory import PRUCParms_FBP as _PRUCParms_FBP
from siriuspy.pwrsupply.bsmp import ConstBSMP as _c
from siriuspy.pwrsupply.functions import PSOpMode as _PSOpMode
from siriuspy.pwrsupply.functions import BSMPFunction as _Function
from siriuspy.pwrsupply.watcher import Watcher as _Watcher
from siriuspy.pwrsupply.pruc_ramp import Ramp as _Ramp


class PSController:
    """Class used to communicate with PS controller.

    PRUController
    Fields method property holds objects trant translate EPICS fields to a BSMP
    variable.
    """

    def __init__(self, readers, functions, connections, pru_controller):
        """Create class properties."""
        self._readers = readers
        self._functions = functions
        self._connections = connections
        self._pru_controller = pru_controller

        self._fields = set()
        # self._devices = set()
        for name in self._readers:
            split = name.split(':')
            self._fields.add(split[-1])
            # self._devices.add(':'.join(split[:2]))
        self._init_setpoints()
        # self._operation_mode = 0

    @property
    def pru_controller(self):
        """PRU controller."""
        return self._pru_controller

    @property
    def fields(self):
        """Field of ps controller."""
        return self._fields

    def read(self, device_name, field):
        """Read pv value."""
        if field == 'CtrlLoop-Sts':
            sts = self._readers[device_name + ':CtrlLoop-Sts']
            sel = self._readers[device_name + ':CtrlLoop-Sel']
            if sts.read() != sel.read():
                sel.apply(sts.read())
        return self._readers[device_name + ':' + field].read()

    def read_all_fields(self, device_name):
        """Read all fields value from device."""
        values = dict()
        for field in self._fields:
            values[device_name + ':' + field] = self.read(device_name, field)
        return values

    def write(self, device_name, field, value):
        """Write value to pv."""
        self._functions[device_name + ':' + field].execute(value)

    def check_connected(self, device_name):
        """Check if device is connected."""
        return self._connections[device_name].connected()

    def _init_setpoints(self):
        for key, reader in self._readers.items():
            if '-Sel' in key or '-SP' in key:
                rb_field = PSController._get_readback_field(key)
                try:
                    value = self._readers[rb_field].read()
                except KeyError:
                    continue
                else:
                    if 'PwrState-Sel' == key:
                        value -= 3
                    reader.apply(value)

    @staticmethod
    def _get_readback_field(field):
        # TODO: check if siriuspvname already has a function for this
        return field.replace('-Sel', '-Sts').replace('-SP', '-RB')


class StandardPSController(PSController):
    """Standard behaviour for a PSController."""

    # INTERVAL_SCAN = 1.0/_PRUCParms_FBP.FREQ_SCAN

    def __init__(self,
                 readers, functions, connections, pru_controller, devices):
        """Call super."""
        super().__init__(readers, functions, connections, pru_controller)
        self._devices = devices
        self._watchers = dict()
        self._pruc_ramp = None
        # self._interval_scan = 1.0/pru_controller.scan_interval

    def read(self, device_name, field):
        """Read pv value."""
        if field == 'OpMode-Sts':
            try:
                if self._watchers[device_name].is_alive():
                    return self._watchers[device_name].op_mode + 3
            except KeyError:
                pass
        return super().read(device_name, field)

    def write(self, device_name, field, value):
        """Override write method."""
        name = device_name + ':' + field
        if field == 'OpMode-Sel':
            writer = self._functions[device_name + ':' + field]
            # if value in (0, 3, 4):
            #     self._operation_mode = value
            self._set_opmode(writer, value)
        elif field == 'CycleType-Sel':
            values = self._cfg_siggen_args(device_name)
            values[0] = value
            self._functions[device_name + ':' + field].execute(values)
        elif field == 'CycleNrCycles-SP':
            values = self._cfg_siggen_args(device_name)
            values[1] = value
            self._functions[device_name + ':' + field].execute(values)
        elif field == 'CycleFreq-SP':
            values = self._cfg_siggen_args(device_name)
            values[2] = value
            self._functions[device_name + ':' + field].execute(values)
        elif field == 'CycleAmpl-SP':
            values = self._cfg_siggen_args(device_name)
            values[3] = value
            self._functions[device_name + ':' + field].execute(values)
        elif field == 'CycleOffset-SP':
            values = self._cfg_siggen_args(device_name)
            values[4] = value
            self._functions[device_name + ':' + field].execute(values)
        elif field == 'CycleAuxParam-SP':
            values = self._cfg_siggen_args(device_name)
            values[5:] = value
            self._functions[device_name + ':' + field].execute(values)
        elif field == 'PwrState-Sel':
            if self._readers[device_name + ':PwrState-Sel'].value == 0:
                self._readers[device_name + ':Current-SP'].apply(0.0)
            self._functions[name].execute(value)
        else:
            self._functions[name].execute(value)

    # Private
    def _set_watchers(self, op_mode):
        self._stop_watchers()
        for dev_name in self._devices:
            dev_ids = [self._devices[dev_name]]
            functions = dict()
            functions['Current-SP'] = self._functions[dev_name + ':Current-SP']
            functions['OpMode-Sel'] = _PSOpMode(
                dev_ids,
                _Function(dev_ids, self._pru_controller, _c.F_SELECT_OP_MODE),
                self._readers[dev_name + ':OpMode-Sel'])

            t = _Watcher(functions, self, dev_name, op_mode)
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
        if setpoint in (_PSConst.OpMode.RmpWfm, ):
            self._set_pruc_ramp()

    def _set_pruc_ramp(self):
        if self._pruc_ramp is not None and self._pruc_ramp.is_alive:
            self._pruc_ramp.stop()
            self._pruc_ramp.join()
        self._pruc_ramp = _Ramp(self._devices, self)
        self._pruc_ramp.start()

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
