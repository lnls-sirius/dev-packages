"""E2SController."""
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.bsmp import ConstBSMP as _c
from siriuspy.pwrsupply.functions import PSOpMode as _PSOpMode
from siriuspy.pwrsupply.functions import BSMPFunction as _Function
from siriuspy.pwrsupply.watcher import Watcher as _Watcher


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
        pvname = device_name + ':' + field
        if field == 'CtrlLoop-Sts':
            sts = self._readers[device_name + ':CtrlLoop-Sts']
            sel = self._readers[device_name + ':CtrlLoop-Sel']
            if sts.read() != sel.read():
                sel.apply(sts.read())

        reader = self._readers[pvname]
        return reader.read()

    def read_all_fields(self, device_name):
        """Read all fields value from device."""
        values = dict()
        for field in self._fields:
            pvname = device_name + ':' + field
            value = self.read(device_name, field)
            values[pvname] = value
        return values

    def write(self, device_name, field, value):
        """Write value to pv."""
        pvname = device_name + ':' + field
        if pvname in self._functions:
            self._functions[pvname].execute(value)

    def check_connected(self, device_name):
        """Check if device is connected."""
        return self._connections[device_name].connected()

    def _init_setpoints(self):
        for key, reader in self._readers.items():
            if key.endswith(('-Sel', '-SP')):
                rb_field = PSController._get_readback_field(key)
                try:
                    value = self._readers[rb_field].read()
                except KeyError:
                    continue
                else:
                    if key.endswith('OpMode-Sel'):
                        if value is not None:
                            value = 0 if value < 3 else value - 3
                    reader.apply(value)

    @staticmethod
    def _get_readback_field(field):
        # TODO: check if siriuspvname already has a function for this
        return field.replace('-Sel', '-Sts').replace('-SP', '-RB')


class StandardPSController(PSController):
    """Standard behaviour for a PSController."""

    _siggen_parms = [
        'CycleType-Sel',
        'CycleNrCycles-SP',
        'CycleFreq-SP',
        'CycleAmpl-SP',
        'CycleOffset-SP',
        'CycleAuxParam-SP',  # start index of auxparams
    ]

    def __init__(self, readers, functions, connections, pru_controller,
                 devices):
        """Call super."""
        super().__init__(readers, functions, connections, pru_controller)
        self._devices = devices
        self._watchers = dict()

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
        pvname = device_name + ':' + field
        if pvname not in self._functions:
            return
        if field == 'OpMode-Sel':
            writer = self._functions[pvname]
            self._set_opmode(writer, value)
        elif field in StandardPSController._siggen_parms:
            idx = StandardPSController._siggen_parms.index(field)
            values = self._get_siggen_arg_values(device_name)
            if field == 'CycleAuxParam-SP':
                values[idx:] = value
            else:
                values[idx] = value
            self._functions[pvname].execute(values)
        elif field == 'PwrState-Sel':
            # NOTE: Should we set Current-SP to zero at Power On ? This may be
            # generating inconsistent behaviour when loading configuration in
            # HLA...
            # if self._readers[device_name + ':PwrState-Sel'].value == 0:
            #     self._readers[device_name + ':Current-SP'].apply(0.0)
            self._functions[pvname].execute(value)
        else:
            self._functions[pvname].execute(value)

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

    def _get_siggen_arg_values(self, device_name):
        """Get cfg_siggen args and execute it."""
        args = [self._readers[device_name + ':' + arg].read()
                for arg in StandardPSController._siggen_parms[:-1]]
        aux = StandardPSController._siggen_parms[-1]
        args.extend(self._readers[device_name + ':' + aux].read())
        return args
