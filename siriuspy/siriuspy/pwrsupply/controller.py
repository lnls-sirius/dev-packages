"""E2SController."""


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
        for name in self._readers:
            split = name.split(':')
            self._fields.add(split[-1])
        self._init_setpoints()

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
        if reader is not None:
            return reader.read()
        raise AttributeError('Could not find reader for "{}"'.format(field))

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
                rdr = self._readers[rb_field]
                if rdr is None:
                    raise AttributeError(
                        'Could not find reader for "{}"'.format(rb_field))
                value = rdr.read()
                if key.endswith('OpMode-Sel'):
                    if value is not None:
                        value = 0 if value < 3 else value - 3
                reader.apply(value)
                # try:
                #     value = self._readers[rb_field].read()
                # except KeyError:
                #     err_str = '\
                #         Could not find reader for PV {}!'.format(rb_field)
                #     print(err_str)
                #     continue
                # else:
                #     if key.endswith('OpMode-Sel'):
                #         if value is not None:
                #             value = 0 if value < 3 else value - 3
                #     reader.apply(value)

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

    def _set_opmode(self, writer, op_mode):
        writer.execute(op_mode)

    def _get_siggen_arg_values(self, device_name):
        """Get cfg_siggen args and execute it."""
        args = [self._readers[device_name + ':' + arg].read()
                for arg in StandardPSController._siggen_parms[:-1]]
        aux = StandardPSController._siggen_parms[-1]
        args.extend(self._readers[device_name + ':' + aux].read())
        return args
