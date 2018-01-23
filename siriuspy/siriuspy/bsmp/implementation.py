"""Module implementing BSMP protocol."""


__version__ = '2.20.0'


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

    _labels = {
        0xE0: 'Ok',
        0xE1: 'invalid_message',
        0xE2: 'operation_not_supported',
        0xE3: 'invalid_id',
        0xE4: 'invalid_value',
        0xE5: 'invalid_data_length',
        0xE6: 'read_only',
        0xE7: 'insufficient_memory',
        0xE8: 'busy_resource',
    }

    @staticmethod
    def conv_ID2label(ID_cmd):
        """Return label of a given error command ID."""
        return Const._labels[ID_cmd]


class BSMP:
    """BSMP class."""

    def __init__(self, ID_device, variables, functions):
        """Init method."""
        self._ID_device = ID_device
        self._variables = {ID: value for ID, value in variables.items()}
        self._functions = {ID: value for ID, value in functions.items()}

    @property
    def ID_device(self):
        """Return ID of BSMP device."""
        return self._ID_device

    @property
    def variables(self):
        """Return variables dictionary."""
        return self._variables

    @property
    def functions(self):
        """Return functions dictionary."""
        return self._functions

    @staticmethod
    def parse_stream(stream):
        """Return parsed message from stream."""
        if len(stream) < 5:
            raise ValueError('BSMP message too short!')
        if not BSMP._verifyChecksum(stream):
            raise ValueError('BSMP message checksum failed!')
        ID_receiver = stream[0]
        ID_cmd = ord(stream[1])
        load_size = (ord(stream[3]) << 8) + ord(stream[2])
        load = stream[4:-1]
        return ID_receiver, ID_cmd, load_size, load

    @staticmethod
    def _verifyChecksum(stream):
        """Return True if checksum matches load."""
        raise NotImplementedError


class BSMPQuery(BSMP):
    """BSMP query commands."""

    def __init__(self, variables, functions, slaves=None):
        """Init method."""
        BSMP.__init__(self, ID_device=0,
                      variables=variables, functions=functions)
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

    def cmd_0x00(self, ID_receiver):
        """Query BSMP protocol version."""
        slave = self._slaves[ID_receiver]
        return slave.query(0x00, ID_receiver=self.ID_device)

    def cmd_0x10(self, ID_receiver, ID_variable):
        """Query BSMP variable."""
        slave = self._slaves[ID_receiver]
        return slave.query(0x10, ID_receiver=self.ID_device,
                           ID_variable=ID_variable)

    def cmd_0x12(self, ID_receiver, ID_group):
        """Query BSMP variables group."""
        slave = self._slaves[ID_receiver]
        return slave.query(0x12, ID_receiver=self.ID_device,
                           ID_group=ID_group)

    def cmd_0x30(self, ID_receiver, ID_group, IDs_variable):
        """Query create BSMP variables group."""
        slave = self._slaves[ID_receiver]
        if ID_group < 3:
            raise ValueError('Invalid group ID number!')
        return slave.query(0x30, ID_receiver=ID_receiver,
                           ID_group=ID_group, IDs_variable=IDs_variable)

    def cmd_0x32(self, ID_receiver):
        """Query remove all BSMP variables groups."""
        slave = self._slaves[ID_receiver]
        return slave.query(0x32, ID_receiver=ID_receiver)

    def cmd_0x50(self, ID_receiver, **kwargs):
        """Query execute BSMP function."""
        slave = self._slaves[ID_receiver]
        return slave.query(0x50, ID_receiver=self.ID_device, **kwargs)


class BSMPResponse(BSMP):
    """BSMP response commands."""

    def __init__(self, ID_device, variables, functions):
        """Init method."""
        if ID_device < 1 or ID_device > 31:
            raise ValueError('Invalid or reserved ID_device number!')
        BSMP.__init__(self, ID_device=ID_device,
                      variables=variables, functions=functions)
        self._groups = {}
        # create group with ID 0
        self._groups[0] = []  # all variables
        self._groups[1] = []  # all read-variables
        self._groups[2] = []  # all write-variables
        for variable in variables:
            variable

    _query2resp = {
        0x00: 'cmd_0x01',
        0x10: 'cmd_0x11',
        0x12: 'cmd_0x13',
        0x30: 'create_group',
        0x32: 'remove_groups',
        0x50: 'cmd_0x51',
    }

    def query(self, cmd, ID_receiver, **kwargs):
        """Receive a command from master."""
        if cmd not in BSMPResponse._query2resp:
            raise NotImplementedError(
                'command {} for implemented'.format(hex(cmd)))
        func = getattr(self, BSMPResponse._query2resp[cmd])
        return func(ID_receiver=ID_receiver, **kwargs)

    def create_group(self, ID_receiver, ID_group, IDs_variable):
        """Respond create BSMP bariables group."""
        raise NotImplementedError

    def remove_groups(self, ID_receiver):
        """Respond remove all BSMP variables groups."""
        raise NotImplementedError

    def cmd_0x01(self, ID_receiver):
        """Respond BSMP protocol version."""
        raise NotImplementedError

    def cmd_0x11(self, ID_receiver, ID_variable):
        """Respond BSMP variable."""
        raise NotImplementedError

    def cmd_0x13(self, ID_receiver, ID_group):
        """Respond BSMP variables group."""
        raise NotImplementedError

    def cmd_0x51(self, ID_receiver, ID_function, **kwargs):
        """Respond execute BSMP function."""
        raise NotImplementedError
