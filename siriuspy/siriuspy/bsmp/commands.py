"""BSMP protocol implementation."""
from .serial import Channel as _Channel
from .serial import Message as _Message


class Const:
    """BSMP Commands."""

    # --- Query Commands ---
    QUERY_PROTOCOL_VERSION = 0x00
    PROTOCOL_VERSION = 0x01
    QUERY_LIST_OF_VARIABLES = 0x02
    LIST_OF_VARIABLE = 0x03
    QUERY_LIST_OF_GROUP_OF_VARIABLES = 0x04
    LIST_OF_GROUP_OF_VARIABLES = 0x05
    QUERY_GROUP_OF_VARIABLES = 0x06
    GROUP_OF_VARIABLES = 0x07
    QUERY_LIST_OF_CURVES = 0x08
    LIST_OF_CURVES = 0x09
    QUERY_CURVE_CHECKSUM = 0x0A
    CURVE_CHECKSUM = 0x0B
    QUERY_LIST_OF_FUNCTIONS = 0x0C
    LIST_OF_FUNCTIONS = 0x0D
    # --- Reading Commands ---
    READ_VARIABLE = 0x10
    VARIABLE_VALUE = 0x11
    READ_GROUP_OF_VARIABLES = 0x12
    GROUP_OF_VARIABLES_VALUE = 0x13
    # --- Writing Commands ---
    WRITE_VARIABLE = 0x20
    WRITE_GROUP_OF_VARIABLES = 0x22
    BINARY_OPERATION_IN_A_VARIABLE = 0x24
    BINARY_OPERATION_IN_A_GROUP = 0x26
    WRITE_AND_READ_VARIABLES = 0x28
    # --- Group of Variables Manipulation Commnads ---
    CREATE_GROUP_OF_VARIABLES = 0x30
    REMOVE_ALL_GROUPS_OF_VARIABLES = 0x32
    # --- Curve Transfer Commands ---
    REQUEST_CURVE_BLOCK = 0x40
    CURVE_BLOCK = 0x41
    RECALCULATE_CURVE_CHECKSUM = 0x42
    # --- Function Execution Commands ---
    EXECUTE_FUNCTION = 0x50
    FUNCTION_RETURN = 0x51
    FUNCTION_ERROR = 0x53
    # --- Error Commands ---
    ACK_OK = 0xE0
    ACK_MALFORMED_MESSAGE = 0xE1
    ACK_OPERATION_NOT_SUPPORTED = 0xE2
    ACK_INVALID_ID = 0xE3
    ACK_INVALID_VALUE = 0xE4
    ACK_INVALID_PAYLOAD_SIZE = 0xE5
    ACK_READ_ONLY = 0xE6
    ACK_INSUFFICIENT_MEMORY = 0xE7
    ACK_RESOURCE_BUSY = 0xE8


class BSMP:
    """BSMP protocol implementation for Master Node."""

    const = Const

    def __init__(self, pru, slave_address, entities):
        """Constructor."""
        self._entities = entities
        self._channel = _Channel(pru, slave_address)

    @property
    def entities(self):
        """Return BSMP entities."""
        return self._entities

    @property
    def channel(self):
        """Return serial channel to an address."""
        return self._channel

    # 0x0_
    def consult_protocol_version(self):
        """Consult protocol version. Command 0x00."""
        # TODO: needs implementation!
        raise NotImplementedError()

    def consult_variables_list(self):
        """Consult list of variables. Command 0x02."""
        # TODO: needs implementation!
        raise NotImplementedError()

    def consult_groups_list(self):
        """Consult groups list. Command 0x04."""
        # TODO: needs implementation!
        raise NotImplementedError()

    def consult_group_variables(self, group_id, timeout):
        """Return id of the variables in the given group."""
        # Send request package
        msg = _Message.message(Const.QUERY_GROUP_OF_VARIABLES,
                               payload=[chr(group_id)])
        response = self.channel.request(msg, timeout)

        # expected response
        if response.cmd == Const.GROUP_OF_VARIABLES:
            return Const.ACK_OK, list(map(ord, response.payload))

        # response with error
        if Const.ACK_OK < response.cmd <= Const.ACK_RESOURCE_BUSY:
            return response.cmd, None

        # unexpected response
        fmts = 'Unexpected BSMP response for {} command: {}!'
        print(fmts.format(Const.GROUP_OF_VARIABLES, response.cmd))
        return None, None

    def consult_curves_list(self):
        """Consult curves_list. Command 0x08."""
        raise NotImplementedError()

    def consult_curve_checksum(self, curve_id):
        """Consult curve checksum given curve id. Command 0x0A."""
        raise NotImplementedError()

    def consult_functions_list(self):
        """Consult functions list. Command 0x0C."""
        raise NotImplementedError()

    # 0x1_
    def read_variable(self, var_id, timeout=100):
        """Read variable."""
        variable = self.entities.variables[var_id]

        # Send request package
        msg = _Message.message(Const.READ_VARIABLE, payload=[chr(var_id)])
        response = self.channel.request(msg, timeout=timeout)

        if response.cmd == Const.VARIABLE_VALUE:
            if len(response.payload) == variable.size:
                # expected response
                return Const.ACK_OK, variable.load_to_value(response.payload)
            # unexpected variable size
            fmts = 'Unexpected BSMP variable size for {} command: {}!'
            print(fmts.format(Const.READ_VARIABLE, response.cmd))
            return None, None

        # unexpected response
        fmts = 'Unexpected BSMP variable size for {} command: {}!'
        print(fmts.format(Const.READ_VARIABLE, response.cmd))
        return None, None

    def read_group_variables(self, group_id, timeout):
        """Read variable group. (0x12)."""
        group = self.entities.groups[group_id]
        m = _Message.message(0x12, payload=[chr(group_id)])
        response = self.channel.request(m, timeout)
        # read_group_variables takes typically 3 ms to run up to this at BBB1!
        if response.cmd == 0x13:
            if len(response.payload) == group.variables_size():
                return Const.ACK_OK, group.load_to_value(response.payload)
        else:
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None

        return None, None

    # 0x2
    def write_variable(self, var_id, value):
        """Write to variable. Command 0x20."""
        raise NotImplementedError()

    def write_group_variables(self, group_id, value):
        """Write to the variables of a group. Command 0x22."""
        raise NotImplementedError()

    def binop_variable(self, var_id, operation, mask):
        """Perform a binary operation to variable. Command 0x24."""
        raise NotImplementedError()

    def binop_group_variables(self, group_id, operation, mask):
        """Perform a binary oeration to the vars of a group. Command 0x26."""
        raise NotImplementedError()

    def write_read_variable(self, w_var_id, r_var_id, value):
        """Write value to a var and read another var value. Command 0x28."""
        raise NotImplementedError()

    # 0x3_
    def create_group(self, var_ids, timeout):
        """Create new group with given variable ids. Command 0x30."""
        var_ids = sorted(var_ids)
        m = _Message.message(0x30, payload=[chr(var_id) for var_id in var_ids])
        response = self.channel.request(m, timeout)
        if response.cmd == 0xE0:
            if len(response.payload) == 0:
                self.entities.add_group(var_ids)
                return Const.ACK_OK, None
        else:
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None

        return None, None

    def remove_all_groups(self, timeout):
        """Remove all groups. Command 0x32."""
        m = _Message.message(0x32)
        response = self.channel.request(m, timeout)
        if response.cmd == 0xE0:
            if len(response.payload) == 0:
                self.entities.remove_all_groups()
                return Const.ACK_OK, None
        else:
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None

        return None, None

    # 0x4_
    def read_curve_block(self, curve_id, block, timeout):
        """Read curve block. Command 0x40."""
        curve = self.entities.curves[curve_id]
        lsb, hsb = block & 0xff, (block & 0xff00) >> 8
        payload = [chr(curve_id), chr(hsb), chr(lsb)]
        message = _Message.message(0x40, payload=payload)
        response = self.channel.request(message, timeout)
        payload, cmd = response.payload, response.cmd

        if cmd != 0x41:
            print('Incorrect response: ', hex(cmd))
            if cmd > 0xE0 and cmd <= 0xE8:
                return cmd, None
            else:
                print('Unknown response!')
                return None, None

        # OK response 0x41
        cid = ord(payload[0])
        cblock = (ord(payload[1]) << 8) + ord(payload[2])
        data = payload[3:]
        if len(data) % curve.type.size:
            print('Curve size is not multiple of curve.type.size!')
            print(' received curve size:{}'.format(len(data)))
            print(' curve.type.size:{}'.format(curve.type.size))
            return None, None

        # OK curve size
        if cid != curve_id or cblock != block:
            print('Invalid curve id or block offset in response!')
            print(' expected - curve_id:{}, block_offset:{}'.format(
                curve_id, block))
            print(' received - curve_id:{}, block_offset:{}'.format(
                cid, cblock))
            return None, None

        # OK curve id and block off
        data_float = curve.load_to_value(data)
        return Const.ACK_OK, data_float

    def write_curve_block(self, curve_id, block, value, timeout):
        """Write to curve block. Command 0x41."""
        curve = self.entities.curves[curve_id]
        lsb, hsb = block & 0xff, (block & 0xff00) >> 8
        payload = [chr(curve_id), chr(hsb), chr(lsb)] + \
            curve.value_to_load(value)

        message = _Message.message(0x41, payload=payload)

        # dev_id = 1
        # package = _Package.package(dev_id, message)
        # print('write query : ', [hex(ord(c)) for c in package.stream])
        # return

        response = self.channel.request(message, timeout)

        if response.cmd > 0xE0 and response.cmd <= 0xE8:
            return response.cmd, None
        else:
            return response.cmd, response.payload

    def calc_curve_checksum(self, curve_id, timeout):
        """Recalculate curve checksum. Command 0x42."""
        payload = [chr(curve_id), ]
        message = _Message.message(0x42, payload=payload)
        response = self.channel.request(message, timeout)
        if response.cmd > 0xE0 and response.cmd <= 0xE8:
            return response.cmd, None
        else:
            return response.cmd, response.payload

    # 0x5_
    def execute_function(self,
                         func_id, input_val=None, timeout=100, read_flag=True):
        """Execute a function. Command 0x50.

        parameter:
            read_flag: whether to execute a read after a write.
        """
        function = self.entities.functions[func_id]
        # Load = function id + input data
        load = [chr(func_id)] + function.value_to_load(input_val)
        message = _Message.message(0x50, payload=load)
        response = self.channel.request(message, timeout, read_flag=read_flag)
        if response.cmd == 0x51:
            # result of the execution
            if len(response.payload) == function.o_size:
                return Const.ACK_OK, function.load_to_value(response.payload)
        elif response.cmd == 0x53:
            # function error
            if len(response.payload) == 1:
                # TODO: the tuple order of return seems to be inverted!
                return response.payload, None
        return None, None  # reached in case of functions with no return


class BSMPSim:
    """BSMP protocol implementation for simulated Master Node."""

    def __init__(self, entities):
        """Entities."""
        self._variables = []
        self._entities = entities

    def __getitem__(self, index):
        """Getitem."""
        return self.bsmp_conn[index]

    @property
    def entities(self):
        """PS entities."""
        return self._entities

    # 0x1_
    def read_variable(self, var_id, timeout=100):
        """Read a variable."""
        # print(var_id)
        return Const.ACK_OK, self._variables[var_id]

    def read_group_variables(self, group_id, timeout):
        """Read group of variables."""
        ids = [var.eid for var in self.entities.groups[group_id].variables]
        values = [self.read_variable(id)[1] for id in ids]
        return Const.ACK_OK, values

    # 0x3_
    def create_group(self, var_ids, timeout):
        """Create new group."""
        self.entities.add_group(var_ids)
        return Const.ACK_OK, None

    def remove_all_groups(self, timeout):
        """Remove all groups."""
        self.entities.remove_all_groups()
        return Const.ACK_OK, None

    # 0x4_
    def read_curve_block(self, curve_id, block, timeout):
        """Read curve block. Command 0x40."""
        curve = self.entities.curves[curve_id]
        lsb, hsb = block & 0xff, (block & 0xff00) >> 8
        m = _Message.message(0x40, payload=[chr(curve_id), chr(hsb), chr(lsb)])
        # print([hex(ord(c)) for c in m.stream])
        response = self.channel.request(m, timeout)
        # print(response.cmd)
        load = response.payload
        data = load[3:]
        # print('load len: ', len(load))
        if response.cmd == 0x41:
            # print('here1', len(data), curve.size)
            if len(data) == curve.size:
                # print('here2')
                cid = ord(load[0])
                cblock = ord(load[1]) << 8 + ord(load[0])
                if cid != curve_id or cblock != block:
                    print('Invalid curve id or block number in response!')
                    print('expected: ', curve_id, block)
                    print('received: ', cid, cblock)
                    return None, None
                else:
                    # print('here4')
                    return Const.ACK_OK, curve.load_to_value(data)
        else:
            # print('here5')
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None

        return None, None

    # 0x5_
    def execute_function(self,
                         func_id, input_val=None, timeout=100, read_flag=True):
        """Execute a function."""
        raise NotImplementedError()
