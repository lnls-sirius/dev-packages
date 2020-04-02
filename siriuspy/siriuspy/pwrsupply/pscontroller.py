"""Controller classes."""


class PSController:
    """Class used to communicate with PS controller.

    PRUController
    Fields method property holds objects trant translate EPICS fields to a BSMP
    variable.
    """

    _ignored_fields = {
        # these are fields managed in BeagleBone class objects.
        'Energy-SP', 'Energy-RB', 'EnergyRef-Mon', 'Energy-Mon',
        'Kick-SP', 'Kick-RB', 'KickRef-Mon', 'Kick-Mon',
        'KL-SP', 'KL-RB', 'KLRef-Mon', 'KL-Mon',
        'SL-SP', 'SL-RB', 'SLRef-Mon', 'SL-Mon'}

    def __init__(self, readers, functions,
                 pru_controller, psname2dev):
        """Initialize PS controller.

        readers : objects from classes in fields module that are responsible
                  for reading power supply parameters
        functions : objects from classes in functions

        """
        self._readers = readers
        self._writers = functions
        self._pru_controller = pru_controller
        self._psname2dev = psname2dev
        self._fields = self._get_fields()
        self._fields_not_ignored = self._fields - self._ignored_fields
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
        """Read non-ignored-field values from device."""
        values = dict()
        for field in self._fields_not_ignored:
            pvname = device_name + ':' + field
            value = self.read(device_name, field)
            values[pvname] = value
        return values

    def write(self, device_name, field, value):
        """Write value to pv."""
        pvname = device_name + ':' + field
        if pvname in self._writers:
            self._writers[pvname].execute(value)

    def check_connected(self, device_name):
        """Check if device is connected."""
        dev_id = self._psname2dev[device_name]
        return self._pru_controller.check_connected(dev_id)

    def _init_setpoints(self):
        for key, reader in self._readers.items():
            # ignore strength fields
            *_, prop = key.split(':')
            if prop in PSController._ignored_fields:
                continue
            if key.endswith(('-Sel', '-SP')):
                rb_field = PSController._get_readback_field(key)

                # NOTE: to be updated
                # rb_field = _PVName.from_sp2rb(key)
                rdr = self._readers[rb_field]

                if rdr is None:
                    raise AttributeError(
                        'Could not find reader for "{}"'.format(rb_field))
                # TODO: Uncomment !!!
                # value = rdr.read()
                # if key.endswith('OpMode-Sel'):
                #     if value is not None:
                #         value = 0 if value < 3 else value - 3
                # reader.apply(value)

    def _get_fields(self):
        fields = set()
        for name in self._readers:
            split = name.split(':')
            fields.add(split[-1])
        return fields

    @staticmethod
    def _get_readback_field(field):
        # NOTE: to be updated
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

    def write(self, device_name, field, value):
        """Override write method."""
        pvname = device_name + ':' + field
        if pvname not in self._writers:
            return
        if field == 'OpMode-Sel':
            writer = self._writers[pvname]
            self._set_opmode(writer, value)
        elif field in StandardPSController._siggen_parms:
            idx = StandardPSController._siggen_parms.index(field)
            values = self._get_siggen_arg_values(device_name)
            if field == 'CycleAuxParam-SP':
                values[idx:] = value
            else:
                values[idx] = value
            self._writers[pvname].execute(values)
        elif field == 'PwrState-Sel':
            # NOTE: Should we set Current-SP to zero at Power On ? This may be
            # generating inconsistent behaviour when loading configuration in
            # HLA...
            # if self._readers[device_name + ':PwrState-Sel'].value == 0:
            #     self._readers[device_name + ':Current-SP'].apply(0.0)
            self._writers[pvname].execute(value)
        else:
            self._writers[pvname].execute(value)

    def _set_opmode(self, writer, op_mode):
        writer.execute(op_mode)

    def _get_siggen_arg_values(self, device_name):
        """Get cfg_siggen args and execute it."""
        args = [self._readers[device_name + ':' + arg].read()
                for arg in StandardPSController._siggen_parms[:-1]]
        aux = StandardPSController._siggen_parms[-1]
        args.extend(self._readers[device_name + ':' + aux].read())
        return args
