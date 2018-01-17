"""Module implementing BSMP protocol."""


__version__ = '2.20'


class Const:
    """BSMP constants."""

    ok = 0xE0,
    invalid_message = 0xE1,
    operation_not_supported = 0xE2,
    invalid_id = 0xE3,
    invalid_value = 0xE4,
    invalid_data_length = 0xE5,
    read_only = 0xE6,
    insufficient_memory = 0xE7,
    busy_resource = 0xE8,


class BSMPDevice:
    """BSMP class."""

    def __init__(self, variables, functions):
        """Init method."""
        self._variables = {ID: value for ID, value in variables.items()}
        self._functions = {ID: value for ID, value in functions.items()}

    @property
    def variables(self):
        """Return variables dictionary."""
        return self._variables

    @property
    def functions(self):
        """Return functions dictionary."""
        return self._functions


class BSMPDeviceMaster(BSMPDevice):
    """BSMP Master class."""

    def __init__(self, variables, functions, slaves=None):
        """Init method."""
        BSMPDevice.__init__(self, variables=variables, functions=functions)
        self._ID_device = 0
        self._slaves = {}
        if slaves is not None:
            for slave in slaves:
                self.add_slave(slave)

    @property
    def slaves(self):
        """Return slave devices."""
        return self._slaves

    def add_slave(self, slave):
        """Add slave."""
        self._slaves[slave.ID_device] = slave

    def cmd_0x00(self, ID_slave):
        """Query BSMP protocol version."""
        slave = self._slaves[ID_slave]
        return slave.query(0x00)

    def cmd_0x10(self, ID_slave, ID_variable):
        """Query BSMP variable."""
        slave = self._slaves[ID_slave]
        return slave.query(0x10, ID_variable=ID_variable)

    def cmd_0x12(self, ID_slave, ID_group):
        """Query BSMP variables group."""
        slave = self._slaves[ID_slave]
        return slave.query(0x12, ID_group=ID_group)

    def cmd_0x30(self, ID_slave, ID_group, IDs_variable):
        """Query create BSMP variables group."""
        slave = self._slaves[ID_slave]
        if ID_group < 3:
            raise ValueError('Invalid group ID number!')
        return slave.query(0x30, ID_group=ID_group, IDs_variable=IDs_variable)

    def cmd_0x32(self, ID_slave):
        """Query remove all BSMP variables groups."""
        slave = self._slaves[ID_slave]
        return slave.query(0x32)

    def cmd_0x50(self, ID_slave, ID_function, **kwargs):
        """Query execute BSMP function."""
        slave = self._slaves[ID_slave]
        return slave.query(0x50, ID_function=ID_function, **kwargs)


class BSMPDeviceSlave(BSMPDevice):
    """BSMP class."""

    def __init__(self, ID_device, variables, functions):
        """Init method."""
        BSMPDevice.__init__(self, variables=variables, functions=functions)
        if ID_device < 1:
            raise ValueError('Invalid ID_device number!')
        self._ID_device = ID_device
        self._groups = {}
        # create group with ID 0
        self._groups[0] = [] # all variables
        self._groups[1] = [] # all read-variables
        self._groups[2] = [] # all write-variables
        for variable in variables:
            variable

    _query2resp = {
        0x00: 'cmd_0x01',
        0x10: 'cmd_0x11',
        0x12: 'cmd_0x13',
        0x30: '_create_group',
        0x32: '_remove_groups',
        0x50: 'cmd_0x51',
    }

    @property
    def ID_device(self):
        """Return BSMP protocol version."""
        return self._ID_device

    def query(self, cmd, **kwargs):
        """Receive a command from master."""
        if cmd not in BSMPDeviceSlave._query2resp:
            raise NotImplementedError(
                'command {} for implemented'.format(hex(cmd)))
        func = getattr(self, BSMPDeviceSlave._query2resp[cmd])
        return func(**kwargs)

    def cmd_0x01(self):
        """Respond BSMP protocol version."""
        raise NotImplementedError

    def cmd_0x11(self, ID_variable):
        """Respond BSMP variable."""
        raise NotImplementedError

    def cmd_0x13(self, ID_group):
        """Respond BSMP variables group."""
        raise NotImplementedError

    def cmd_0x51(self, ID_function, **kwargs):
        """Respond execute BSMP function."""
        raise NotImplementedError

    def _create_group(self, ID_group, IDs_variable):
        """Respond create BSMP bariables group."""
        raise NotImplementedError

    def _remove_groups(self):
        """Respond remove all BSMP variables groups."""
        raise NotImplementedError
