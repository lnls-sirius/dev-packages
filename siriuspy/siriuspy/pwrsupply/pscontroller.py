"""Controller classes."""


class PSController:
    """Power supply controller.

        Objects of this class are used to communicate with power supply devices
    by invoking properties and methods of the PRU controller.
    """

    _ignored_fields = {
        # these are fields managed in BeagleBone class objects.
        'Energy-SP', 'Energy-RB', 'EnergyRef-Mon', 'Energy-Mon',
        'Kick-SP', 'Kick-RB', 'KickRef-Mon', 'Kick-Mon',
        'KL-SP', 'KL-RB', 'KLRef-Mon', 'KL-Mon',
        'SL-SP', 'SL-RB', 'SLRef-Mon', 'SL-Mon'}

    def __init__(self, readers, writers,
                 pru_controller, devname2devid):
        """Initialize PS controller.

        readers : objects from classes in fields module that are responsible
                  for reading power supply parameters
        writers : objects from classes in writers

        """
        self._readers = readers
        self._writers = writers
        self._pru_controller = pru_controller

        self._devname2devid = devname2devid

        # get all controller fields
        self._fields = self._get_fields()

        # shortcut to fields not to be ignored
        self._fields_not_ignored = self._fields - self._ignored_fields

    @property
    def pru_controller(self):
        """PRU controller."""
        return self._pru_controller

    @property
    def fields(self):
        """Field of ps controller."""
        return self._fields

    def read(self, devname, field):
        """Read pv value."""
        pvname = devname + ':' + field
        if field == 'CtrlLoop-Sts':
            sts = self._readers[devname + ':CtrlLoop-Sts']
            sel = self._readers[devname + ':CtrlLoop-Sel']
            if sts.read() != sel.read():
                sel.apply(sts.read())

        reader = self._readers[pvname]
        if reader is not None:
            return reader.read()
        raise AttributeError('Could not find reader for "{}"'.format(field))

    def read_all_fields(self, devname):
        """Read non-ignored-field values from device."""
        values = dict()
        for field in self._fields_not_ignored:
            pvname = devname + ':' + field
            value = self.read(devname, field)
            values[pvname] = value
        return values

    def write(self, devname, field, value):
        """Write value to pv."""
        pvname = devname + ':' + field
        if pvname in self._writers:
            self._writers[pvname].execute(value)

    def check_connected(self, devname):
        """Check if device is connected."""
        devid = self._devname2devid[devname]
        return self._pru_controller.check_connected(devid)

    def init_setpoints(self):
        """Initialize controller setpoint fields."""
        for key, reader_sp in self._readers.items():

            # ignore non-setpoint fields
            if not key.endswith(('-Sel', '-SP')):
                continue

            # ignore strength fields
            *_, prop = key.split(':')
            if prop in PSController._ignored_fields:
                continue

            # initiliaze setpoint fields using corresponding readers

            # use corresponding readback field
            field_rb = PSController._get_readback_field(key)

            # check if reader exists
            reader_rb = self._readers[field_rb]
            if reader_rb is None:
                raise AttributeError(
                    'Could not find reader for "{}"'.format(field_rb))

            # read readback value
            value = reader_rb.read()
            if key.endswith('OpMode-Sel'):
                # OpModel-Sel is shifted in 3 units relative OpMode-Sts
                if value is not None:
                    value = 0 if value < 3 else value - 3

            # apply value to setpoint using its reader
            reader_sp.apply(value)

    # --- private methods ---

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

    def write(self, devname, field, value):
        """Override write method."""
        pvname = devname + ':' + field
        if pvname not in self._writers:
            return
        if field == 'OpMode-Sel':
            writer = self._writers[pvname]
            StandardPSController._set_opmode(writer, value)
        elif field in StandardPSController._siggen_parms:
            idx = StandardPSController._siggen_parms.index(field)
            values = self._get_siggen_arg_values(devname)
            if field == 'CycleAuxParam-SP':
                values[idx:] = value
            else:
                values[idx] = value
            self._writers[pvname].execute(values)
        elif field == 'PwrState-Sel':
            # NOTE: Should we set Current-SP to zero at Power On ? This may be
            # generating inconsistent behaviour when loading configuration in
            # HLA...
            # if self._readers[devname + ':PwrState-Sel'].value == 0:
            #     self._readers[devname + ':Current-SP'].apply(0.0)
            self._writers[pvname].execute(value)
        else:
            self._writers[pvname].execute(value)

    # --- private methods ---

    @staticmethod
    def _set_opmode(writer, op_mode):
        writer.execute(op_mode)

    def _get_siggen_arg_values(self, devname):
        """Get cfg_siggen args and execute it."""
        args = [self._readers[devname + ':' + arg].read()
                for arg in StandardPSController._siggen_parms[:-1]]
        aux = StandardPSController._siggen_parms[-1]
        args.extend(self._readers[devname + ':' + aux].read())
        return args
