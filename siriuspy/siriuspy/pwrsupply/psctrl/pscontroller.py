"""Controller classes."""

from ...search import PSSearch as _PSSearch


class PSController:
    """Power supply controller.

    Objects of this class are used to communicate with power supply devices
    by invoking properties and methods of the PRU controller.
    """

    _FIELDS_IGNORED = {
        # these are fields managed in BeagleBone class objects.
        'Energy-SP', 'Energy-RB', 'EnergyRef-Mon', 'Energy-Mon',
        'Kick-SP', 'Kick-RB', 'KickRef-Mon', 'Kick-Mon',
        'KL-SP', 'KL-RB', 'KLRef-Mon', 'KL-Mon',
        'SL-SP', 'SL-RB', 'SLRef-Mon', 'SL-Mon',
        'WfmOffsetKick-SP', 'WfmOffsetKick-RB',
        'WfmOffsetKL-SP', 'WfmOffsetKL-RB',
        'WfmOffsetSL-SP', 'WfmOffsetSL-RB',
        'WfmOffsetEnergy-SP', 'WfmOffsetEnergy-RB',
        }

    def __init__(self, readers, writers,
                 pru_controller, devname2devid):
        """Initialize PS controller.

        readers : objects from classes in psreaders module that are responsible
                  for reading power supply parameters
        writers : objects from classes in pscwriters

        """
        self._readers = readers
        self._writers = writers
        self._pru_controller = pru_controller

        self._devname2devid = devname2devid

        # get all controller fields
        self._fields = self._get_fields()

        # shortcut to fields not to be ignored
        self._fields_not_ignored = self._fields - self._FIELDS_IGNORED

        # get udc to dev dictionary
        self._udc2dev = self._get_udc2dev()

    @property
    def pru_controller(self):
        """PRU controller."""
        return self._pru_controller

    @property
    def fields(self):
        """Field of ps controller."""
        return self._fields

    @property
    def readers(self):
        """Return controller readers."""
        return self._readers

    @property
    def writers(self):
        """Return controller writers."""
        return self._writers

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
        priority_pvs = dict()

        pvname = devname + ':' + field
        if pvname in self._writers:
            self._writers[pvname].execute(value)

        # update all setpoint properties upon return from IDFFMode
        if value == 0 and 'IDFFMode-Sel' in field:
            self._update_setpoints(devname)

        # return priority pvs
        return priority_pvs

    def check_connected(self, devname):
        """Check if device is connected."""
        devid = self._devname2devid[devname]
        return self._pru_controller.check_connected(devid)

    def init_setpoints(self, devname=None):
        """Initialize controller setpoint fields."""
        for key, reader_sp in self._readers.items():

            # if devname was passed, continue in case reader does not belong to device
            if devname and devname not in key:
                continue

            # ignore non-setpoint fields
            if not key.endswith(('-Sel', '-SP')):
                continue

            # ignore strength fields
            *_, prop = key.split(':')
            if prop in PSController._FIELDS_IGNORED:
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

    def _get_udc2dev(self):
        udc2dev = dict()
        for devname in self._devname2devid:
            udc = _PSSearch.conv_psname_2_udc(devname)
            if udc not in udc2dev:
                udc2dev[udc] = set()
            udc2dev[udc].add(devname)
        return udc2dev

    def _get_fields(self):
        fields = set()
        for name in self._readers:
            split = name.split(':')
            fields.add(split[-1])
        return fields

    def _update_setpoints(self, devname):
        """."""
        self.read_all_fields(devname)
        self.init_setpoints(devname)

    @staticmethod
    def _get_readback_field(field):
        # NOTE: to be updated
        return field.replace('-Sel', '-Sts').replace('-SP', '-RB')


class StandardPSController(PSController):
    """Standard PSController.

    This is used in DCDC-type power supply models.
    """

    PARMS_SIGGEN = [
        'CycleType-Sel',
        'CycleNrCycles-SP',
        'CycleFreq-SP',
        'CycleAmpl-SP',
        'CycleOffset-SP',
        'CycleAuxParam-SP',  # start index of auxparams
    ]

    PARMS_WFM = [
        'WfmSyncMode-Sel',
        'WfmFreq-SP',
        'WfmGain-SP',
        'WfmOffset-SP',
    ]

    def write(self, devname, field, value):
        """Write value to pv."""
        priority_pvs = dict()

        pvname = devname + ':' + field
        if pvname not in self._writers:
            return priority_pvs

        if field == 'IDFFMode-Sel':
            self._set_idff_mode(pvname, value, devname, field, priority_pvs)
        elif field in StandardPSController.PARMS_SIGGEN:
            self._set_siggen(pvname, value, devname, field, priority_pvs)
        elif field in StandardPSController.PARMS_WFM:
            self._set_wfm(pvname, value, devname, field, priority_pvs)
        else:
            self._writers[pvname].execute(value)

        # update all setpoint properties upon return from IDFFMode
        if 'IDFFMode-Sel' in field and value == 0:
            self._update_setpoints(devname)

        # return priority pvs
        return priority_pvs

    # --- private methods ---

    def _set_siggen(self, pvname, value, devname, field, priority_pvs):
        _ = priority_pvs
        idx = StandardPSController.PARMS_SIGGEN.index(field)
        values = self._get_siggen_arg_values(devname)
        if field == 'CycleAuxParam-SP':
            values[idx:] = value
        else:
            values[idx] = value
        self._writers[pvname].execute(values)

    def _set_wfm(self, pvname, value, devname, field, priority_pvs):
        _ = priority_pvs
        idx = StandardPSController.PARMS_WFM.index(field)
        values = self._get_wfm_arg_values(devname)
        values[idx] = value
        self._writers[pvname].execute(values)

    def _set_idff_mode(self, pvname, value, devname, field, priority_pvs):
        _, _, _ = pvname, field, priority_pvs
        # loop over all UDC devices
        for udc_devnames in self._udc2dev.values():
            if devname in udc_devnames:
                # loop over other UDC devices
                for devname_ in udc_devnames:
                    pvn = devname_ + ':IDFFMode-Sel'
                    self._writers[pvn].execute(value)

    def _get_siggen_arg_values(self, devname):
        """Get cfg_siggen args."""
        args = [self._readers[devname + ':' + arg].read()
                for arg in StandardPSController.PARMS_SIGGEN[:-1]]
        aux = StandardPSController.PARMS_SIGGEN[-1]
        args.extend(self._readers[devname + ':' + aux].read())
        return args

    def _get_wfm_arg_values(self, devname):
        """Get Wfm args."""
        args = [self._readers[devname + ':' + arg].read()
                for arg in StandardPSController.PARMS_WFM]
        return args
