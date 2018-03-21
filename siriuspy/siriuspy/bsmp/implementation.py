"""Module implementing BSMP protocol."""
import struct as _struct

__version__ = '2.20.0'


class Const:
    """BSMP constants."""

    ok = 0xE0
    invalid_message = 0xE1
    operation_not_supported = 0xE2
    invalid_id = 0xE3
    invalid_value = 0xE4
    invalid_data_length = 0xE5
    read_only = 0xE6
    insufficient_memory = 0xE7
    busy_resource = 0xE8

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
    def conv_error2label(ID_cmd):
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

    # @staticmethod
    # def _verifyChecksum(stream):
    #     """Return True if checksum matches load."""
    #     raise NotImplementedError

    @staticmethod
    def _verifyChecksum(stream):
        """Verify stream checksum."""
        counter = 0
        i = 0
        while (i < len(stream) - 1):
            counter += ord(stream[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        if (stream[len(stream) - 1] == chr(counter)):
            return(True)
        else:
            return(False)


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
        return slave.query(0x00, ID_receiver=ID_receiver)

    def cmd_0x10(self, ID_receiver, ID_variable):
        """Query BSMP variable."""
        slave = self._slaves[ID_receiver]
        return slave.query(0x10, ID_receiver=ID_receiver,
                           ID_variable=ID_variable)

    def cmd_0x12(self, ID_receiver, ID_group):
        """Query BSMP variables group."""
        slave = self._slaves[ID_receiver]
        return slave.query(0x12, ID_receiver=ID_receiver,
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
        return slave.query(0x50, ID_receiver=ID_receiver, **kwargs)


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


class Message:
    """BSMP Message.

    Command: command id; 1 byte;
    Load Size: load size in bytes; 2 bytes (big endian);
    Load: 0..65535 bytes.
    """

    # Constructors
    def __init__(self, cmd, load=None):
        """Build a BSMP message."""
        if load and not isinstance(load, list):
            raise TypeError("Load must be a list.")
        if load and len(load) > 65535:
            raise ValueError("Load must be smaller than 65535.")

        self._cmd = cmd
        self._load = load

    @classmethod
    def init_stream(cls, stream):
        """Build a Message object from a byte stream."""
        if len(stream) < 3:
            raise ValueError("BSMP Message too short.")
        # cmd = cls.decode_cmd(stream[0])
        # load = cls.decode_load(stream[3:])

        return cls(stream[0], stream[3:])

    # API
    @property
    def cmd(self):
        """Command ID."""
        return self._cmd

    @property
    def load(self):
        """Message load."""
        return self._load

    def to_stream(self):
        """Get byte stream."""
        stream = []
        # stream.append(Message.encode_cmd(self.cmd))
        # stream.extend(self._get_load_size())
        # if self._load:
        #     stream.extend(Message.encode_load(self.load))
        stream.append(self.cmd)
        stream.extend(self._get_load_size())
        if self.load:
            stream.extend(self.load)
        return stream

    # @staticmethod
    # def encode_cmd(cmd):
    #     """Encode command to bytes."""
    #     return chr(cmd)

    # @staticmethod
    # def decode_cmd(cmd):
    #     """Decode command from bytes."""
    #     return ord(cmd)

    # @staticmethod
    # def encode_load(load):
    #     """Encode load value/array to bytes."""
    #     return [chr(l) for l in load]

    # @staticmethod
    # def decode_load(load):
    #     """Decode load value/array to bytes."""
    #     return [ord(l) for l in load]

    def _get_load_size(self):
        # Get load size in bytes
        n = len(self._load)
        return [chr((n & 0xFF00) >> 8), chr(n & 0xFF)]


class Package:
    """BSMP package.

    Address: 1 byte, 0..31
    Message: no limit
    Checksum: package checksum
    """

    # Constructors
    def __init__(self, address, message):
        """Build a BSMP package."""
        # if address < 0 or address > 31:
        #     raise ValueError("Address {} out of range.".format(address))
        self._address = address  # 0 to 31
        self._message = message

        self._stream = None

    @classmethod
    def init_stream(cls, stream):
        """Build a Package object from a byte stream."""
        if len(stream) < 5:
            raise ValueError("BSMP Package too short.")
        # Verify checksum
        if not Package.verify_checksum(stream):
            raise ValueError("Inconsistent message. Checksum does not check.")
        # Return new package
        address = stream[0]
        message = Message.init_stream(stream[1:-1])
        return cls(address, message)

    # API
    @property
    def address(self):
        """Receiver node serial address."""
        return self._address

    @property
    def message(self):
        """Package message."""
        return self._message

    @property
    def checksum(self):
        """Package checksum."""
        stream = []
        stream.append(self._address)
        stream.extend(self._message.to_stream())
        return Package.calc_checksum(stream)

    def to_stream(self):
        """Convert Package to byte stream."""
        stream = []
        stream.append(self._address)
        stream.extend(self._message.to_stream())
        return stream + [chr(Package.calc_checksum(stream))]

    @staticmethod
    def calc_checksum(stream):
        """Return stream checksum."""
        counter = 0
        i = 0
        while (i < len(stream)):
            counter += ord(stream[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        return counter

    @staticmethod
    def verify_checksum(stream):
        """Verify stream checksum."""
        counter = 0
        i = 0
        while (i < len(stream) - 1):
            counter += ord(stream[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        if (stream[len(stream) - 1] == chr(counter)):
            return(True)
        else:
            return(False)


class Channel:
    """Serial comm with address."""

    def __init__(self, serial, address):
        """Set channel."""
        self.serial = serial
        self.address = address
        # self.error = False

    def read(self):
        """Read from serial."""
        package = Package.init_stream(self.serial.UART_read())
        # if package.message.cmd > 0xE0:
        #     self.error = package.message.cmd
        # else:
        #     self.error = False
        return package.message

    def write(self, message, timeout=100):
        """Write to serial."""
        stream = Package(chr(self.address), message).to_stream()
        return self.serial.UART_write(stream, timeout=timeout)

    def request(self, message, timeout=100):
        """Write and wait for response."""
        self.write(message, timeout)
        return self.read()


class Variable:
    """BSMP variable."""

    def __init__(self, eid, waccess, size, var_type):
        """Set variable properties."""
        self.eid = eid
        self.waccess = waccess
        if size == 0:
            size = 128
        self.size = size  # 1..128 bytes
        self.type = var_type

    # @classmethod
    # def load_init(cls, id, load):
    #     """Construct variable from load."""
    #     write_access = (load & 0x80) >> 7
    #     size = (load & 0x7F)
    #     return cls(id, write_access, size)

    # def read(self, channel):
    #     """Send command 0x10."""
    #     m = Message(chr(0x10), [chr(self.eid)])
    #     message = channel.request(m)
    #     value = self.load_to_value(message.load)
    #     return value

    # def write(self, channel, value):
    #     """Send command 0x20."""
    #     if not self.waccess:
    #         return
    #     load = self.value_to_load(value)
    #     m = Message(chr(0x20), load)
    #     return channel.request(m)

    # def bin_op(self, op, mask):
    #     """Send binary operation command 0x24."""
    #     raise NotImplementedError()

    def load_to_value(self, load):
        """Parse value from load."""
        if self.type == 'int':
            value = 0
            for i in range(self.size):
                value += ord(load[i]) << (i*8)
        elif self.type == 'float':
            value = _struct.unpack('<f', bytes(load))[0]
        elif self.type == 'string':
            value = ''
            byte, _ = load.split(chr(0), 1)
            for char in byte:
                value += '{:c}'.format(ord(char))
        elif self.type == 'arr_float':
            value = []
            for i in range(int(self.size/4)):
                value.append(_struct.unpack('<f', bytes(load[i*4:i*4+4]))[0])
        else:
            raise NotImplementedError("Type not defined.")

        return value

    def value_to_load(self, value):
        """Convert value to load."""
        if isinstance(value, int):
            return chr(value)
        elif isinstance(value, float):
            return _struct.pack('<f', value)
        elif isinstance(value, str) and self.type == 'string':
            return value.encode()
        elif isinstance(value, list) and self.type == 'arr_float':
            load = bytes()
            for v in value:
                load += _struct.pack('<f', v)
            return load
        else:
            raise NotImplementedError("Type not defined.")


class VariablesGroup:
    """BSMP variables group entity."""

    def __init__(self, eid, waccess, size, variables):
        """Set group parameter."""
        self.eid = eid
        self.waccess = waccess
        self.size = size
        self.variables = variables

    # def read(self, channel):
    #     """Read variables id. Command 0x12."""
    #     m = Message(chr(0x12), [chr[self.eid]])
    #     message = channel.send(m)
    #     ids = [self._load_to_value(message.load)]
    #     return ids

    # def write(self, value, n_vars):
    #     """Write to variables group. Command 0x22."""
    #     raise NotImplementedError()

    # def bin_op(self, op, mask, n_vars):
    #     """Binary operaion on group of variables."""
    #     raise NotImplementedError()

    def load_to_value(self, load):
        """Parse value from load."""
        value = list()
        offset = 0
        for variable in self.variables:
            i, j = offset, offset + variable.size
            value.append(variable.load_to_value(load[i:j]))
            offset += variable.size
        return value

    def value_to_load(self, value):
        """Parse load from value."""
        pass

    def variables_size(self):
        """Return sum of variables size."""
        size = 0
        for variable in self.variables:
            size += variable.size
        return size


class Curve:
    """BSMP Curve entity."""

    def __init__(self, eid, waccess, sblocks, nblocks, checksum):
        """Set curve properties."""
        self.eid = eid  # Entity ID
        self.waccess = waccess
        self.sblocks = sblocks  # Block size
        self.nblocks = nblocks  # Number of blocks
        self.checksum = checksum

    # def read_block(self):
    #     """Read a curve block. Command 0x40."""
    #     pass

    # def send_block(self, block_number, block_data):
    #     """Write curve block. Commadn 0x41."""
    #     pass

    # def calc_checksum(self):
    #     """Recalculate curve checksum. Command 0x42."""
    #     pass


class Function:
    """BSMP function."""

    def __init__(self, func_id, input_size, output_size):
        """Set function properties."""
        self.id = func_id
        self.input_size = input_size  # 0..15
        self.output_size = output_size  # 0..15

    # @classmethod
    # def load_init(cls, id, load):
    #     """Construct variable from load."""
    #     input_size = (load & 0xF0) >> 4
    #     output_size = (load & 0x0F)
    #     return cls(id, input_size, output_size)

    # def execute(self):
    #     """Execute function. Command 0x50."""
    #     pass


class Entities:
    """BSMP entities."""

    def __init__(self, variables, functions):
        """Constructor."""
        self.variables = [
            Variable(0, False, 2, 'int'),
            Variable(1, False, 4, 'float'),
            Variable(2, False, 4, 'float'),
            Variable(3, False, 0, 'arr_char'),
            Variable(4, False, 2, 'int'),
            Variable(5, False, 2, 'int'),
            Variable(6, False, 2, 'int'),
            Variable(7, False, 2, 'int'),
            Variable(8, False, 2, 'int'),
            Variable(9, False, 4, 'float'),
            Variable(10, False, 4, 'float'),
            Variable(11, False, 4, 'float'),
            Variable(12, False, 4, 'float'),
            Variable(13, False, 16, 'arr_float'),
            Variable(14, False, 2, 'int'),
            Variable(15, False, 2, 'int'),
            Variable(16, False, 4, 'float'),
            Variable(17, False, 4, 'float'),
            Variable(18, False, 4, 'float'),
            Variable(19, False, 4, 'float'),
            Variable(20, False, 4, 'float'),
            Variable(21, False, None, None),
            Variable(22, False, None, None),
            Variable(23, False, None, None),
            Variable(24, False, None, None),
            Variable(25, False, 2, 'int'),
            Variable(26, False, 2, 'int'),
            Variable(27, False, 4, 'float'),
            Variable(28, False, 4, 'float'),
            Variable(29, False, 4, 'float'),
            Variable(30, False, 4, 'float'),
        ]

        self.functions = []


class BSMP:
    """BSMP protocol implementation."""

    OK = 0xE0
    INVALID_LOAD_SIZE = 0xE5

    def __init__(self, serial, slave_address, entities):
        """Constructor."""
        self._channel = Channel(self._serial, self._slave_address)
        # self._variables = self.read_variables_list()
        self._entities = entities
        # Variables group cache
        self._group_cache = dict()

    @property
    def entitites(self):
        """BSMP entities."""
        return self._entities

    @property
    def channel(self):
        """Serial channel to an address."""
        return self._channel

    # def read_variables_list(self):
    #     """Consult list of variables. Command 0x02."""
    #     variables = list()
    #     # Build package
    #     package = Package(self._slave_address, Message(0x02))
    #     response = Transaction.send(self._serial, package)
    #
    #     for id, var_load in enumerate(response.message.load):
    #         variables.append(Variable.from_load(id, var_load))
    #
    #     return variables

    # def read_functions_list(self):
    #     """Consult list of functions. Command 0x0C."""
    #     functions = list()
    #     # Build package
    #     package = Package(self._slave_address, Message(0x0C))
    #     response = Transaction.send(self._serial, package)
    #
    #     for id, fun_load in enumerate(response.message.load):
    #         functions.append(Function.from_load(id, fun_load))
    #
    #     return functions

    # 0x0_
    def consult_variables_group(self, group_id):
        """Return id of the variables in the given group. Command 0x06."""
        # Send request package
        m = Message(chr(0x06), [chr(group_id)])
        message = self.channel.request(m)
        # Check for errors
        if message.cmd == 0x07:
            return BSMP.OK, message.load

        return None, None

    # 0x1_
    def read_variable(self, var_id):
        """Read variable. (0x10)."""
        variable = self.entities.variables[var_id]
        m = Message(chr(0x10), [chr(var_id)])
        response = self.channel.request(m)  # Returns a message
        if response.cmd == 0x11:  # Ok
            if len(response.load) == variable.size:
                return BSMP.OK, variable.load_to_value(response.load)
        else:  # Error
            if response.cmd > 0x0E:
                return response.cmd, None
        return None, None

    def read_variables_group(self, group_id):
        """Read variable group. (0x12)."""
        group = self.entities.group[group_id]
        m = Message(chr(0x12), [chr(group_id)])
        response = self.channel.request(m)
        if response.cmd == 0x13:
            if len(response.load) == group.variables_size():
                return BSMP.OK, group.load_to_value(response.load)
        else:
            if response.cmd > 0xE0:
                return response.cmd, None
        return None, None

    # 0x5_
    def execute_function(self, id_function, input):
        """Execute a function. Command 0x50."""
        pass
