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

    CONST = Const

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
    def query_protocol_version(self):
        """Consult protocol version. Command 0x00."""
        # TODO: needs implementation!
        raise NotImplementedError()

    def query_list_of_variables(self):
        """Consult list of variables. Command 0x02."""
        # TODO: needs implementation!
        raise NotImplementedError()

    def query_list_of_group_of_variables(self):
        """Consult groups list. Command 0x04."""
        # TODO: needs implementation!
        raise NotImplementedError()

    def query_group_of_variables(self, group_id, timeout):
        """Return id of the variables in the given group."""
        # command and expected response
        cmd, ack = Const.QUERY_GROUP_OF_VARIABLES, Const.GROUP_OF_VARIABLES

        # build payload
        payload = [chr(group_id)]

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        # expected response
        if res.cmd == ack:
            return Const.ACK_OK, list(map(ord, res.payload))

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    def query_list_of_curves(self):
        """Consult curves_list. Command 0x08."""
        raise NotImplementedError()

    def query_curve_checksum(self, curve_id):
        """Consult curve checksum given curve id. Command 0x0A."""
        raise NotImplementedError()

    def query_list_of_functions(self):
        """Consult functions list. Command 0x0C."""
        raise NotImplementedError()

    # 0x1_
    def read_variable(self, var_id, timeout):
        """Read variable."""
        # command and expected response
        cmd, ack = Const.READ_VARIABLE, Const.VARIABLE_VALUE

        # build payload
        payload = [chr(var_id)]

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        if res.cmd == ack:
            variable = self.entities.variables[var_id]
            if len(res.payload) == variable.size:
                # expected response
                return Const.ACK_OK, variable.load_to_value(res.payload)
            # unexpected variable size
            fmts = 'Unexpected BSMP variable size for {} command: {}!'
            print(fmts.format(cmd, res.cmd))
            return None, None

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    def read_group_of_variables(self, group_id, timeout):
        """Read variable group."""
        # command and expected response
        cmd, ack = \
            Const.READ_GROUP_OF_VARIABLES, Const.GROUP_OF_VARIABLES_VALUE

        # build payload
        payload = [chr(group_id)]

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        if res.cmd == ack:
            # expected response
            group = self.entities.groups[group_id]
            if len(res.payload) == group.variables_size():
                return Const.ACK_OK, group.load_to_value(res.payload)
            # unexpected group variables size
            fmts = 'Unexpected BSMP group variables size for {} command: {}!'
            print(fmts.format(cmd, res.cmd))
            return None, None

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    # 0x2_
    def write_variable(self, var_id, value):
        """Write to variable. Command 0x20."""
        raise NotImplementedError()

    def write_group_of_variables(self, group_id, value):
        """Write to the variables of a group. Command 0x22."""
        raise NotImplementedError()

    def binoperation_variable(self, var_id, operation, mask):
        """Perform a binary operation to variable. Command 0x24."""
        raise NotImplementedError()

    def binoperation_group(self, group_id, operation, mask):
        """Perform a binary oeration to the vars of a group. Command 0x26."""
        raise NotImplementedError()

    def write_and_read_variable(self, w_var_id, r_var_id, value):
        """Write value to a var and read another var value. Command 0x28."""
        raise NotImplementedError()

    # 0x3_
    def create_group_of_variables(self, var_ids, timeout):
        """Create new group with given variable ids."""
        cmd, ack = \
            Const.CREATE_GROUP_OF_VARIABLES, Const.ACK_OK

        # build payload
        var_ids = sorted(var_ids)
        payload = [chr(var_id) for var_id in var_ids]

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        if res.cmd == ack:
            if not res.payload:
                # expected response
                # TODO: revise this. do we need to change entities?!
                # if so, should we make a local copy instead?
                self.entities.add_group(var_ids)
                return Const.ACK_OK, None
            # unexpected non-empty response payload
            fmts = 'Unexpected BSMP non-empty resp payload for {} command: {}!'
            print(fmts.format(cmd, res.cmd))
            return None, None

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    def remove_all_groups_of_variables(self, timeout):
        """Remove all groups."""
        cmd, ack = \
            Const.REMOVE_ALL_GROUPS_OF_VARIABLES, Const.ACK_OK

        # build payload
        payload = []

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        if res.cmd == ack:
            if not res.payload:
                # expected response
                # TODO: revise this. do we need to change entities?!
                # if so, should we make a local copy instead?
                self.entities.remove_all_groups_of_variables()
                return Const.ACK_OK, None
            # unexpected non-empty response payload
            fmts = 'Unexpected BSMP non-empty resp payload for {} command: {}!'
            print(fmts.format(cmd, res.cmd))
            return None, None

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    # 0x4_
    def request_curve_block(self, curve_id, block, timeout):
        """Read curve block."""
        # command and expected response
        cmd, ack = Const.REQUEST_CURVE_BLOCK, Const.CURVE_BLOCK

        # build payload
        lsb, hsb = block & 0xff, (block & 0xff00) >> 8
        payload = [chr(curve_id), chr(hsb), chr(lsb)]

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        if res.cmd == ack:
            data = res.payload[3:]
            curve = self.entities.curves[curve_id]
            if len(data) % curve.type.size:
                # unexpected curve size
                fmts = ('Curve size is not multiple of curve.type.size!\n'
                        ' received curce size: {}\n'
                        ' curve.type.size: {}')
                print(fmts.format(len(data), curve.type.size))
                return None, None
            cid = ord(res.payload[0])
            cblock = (ord(res.payload[1]) << 8) + ord(res.payload[2])
            if cid != curve_id or cblock != block:
                # unexpected curve id or block number
                fmts = ('Invalid curve id or block offset in response!\n'
                        ' expected - curve_id:{}, block_offset:{}\n'
                        ' received - curve_id:{}, block_offset:{}')
                print(fmts.format(curve_id, block, cid, cblock))
                return None, None

            # expected result
            data_float = curve.load_to_value(data)
            return Const.ACK_OK, data_float

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    def curve_block(self, curve_id, block, value, timeout):
        """Write to curve block."""
        # command and expected response
        cmd, ack = Const.CURVE_BLOCK, Const.ACK_OK

        # build payload
        curve = self.entities.curves[curve_id]
        lsb, hsb = block & 0xff, (block & 0xff00) >> 8
        payload = [chr(curve_id), chr(hsb), chr(lsb)] + \
            curve.value_to_load(value)

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        if res.cmd == ack:
            # expected response
            return res.cmd, res.payload

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    def recalculate_curve_checksum(self, curve_id, timeout):
        """Recalculate curve checksum."""
        # command and expected response
        cmd, ack = Const.RECALCULATE_CURVE_CHECKSUM, Const.CURVE_CHECKSUM

        # build payload
        payload = [chr(curve_id)]

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout)

        if res.cmd == ack:
            # expected response
            return res.cmd, res.payload

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    # 0x5_
    def execute_function(self, func_id, input_val=None, timeout=100,
                         read_flag=True):
        """Execute a function.

        parameter:
            read_flag: whether to execute a read after a write.
        """
        # command and expected response
        cmd, ack = Const.EXECUTE_FUNCTION, Const.FUNCTION_RETURN

        # build payload
        function = self.entities.functions[func_id]
        payload = [chr(func_id)] + function.value_to_load(input_val)

        # send request package
        msg = _Message.message(cmd, payload=payload)
        res = self.channel.request(msg, timeout=timeout, read_flag=read_flag)

        if res.cmd == ack:
            if len(res.payload) == function.o_size:
                # expected response
                return Const.ACK_OK, function.load_to_value(res.payload)
        if res.cmd == Const.FUNCTION_ERROR:
            # function error
            if len(res.payload) == 1:
                # return error code
                return res.cmd, res.payload[0]

        # anomalous response
        return BSMP._anomalous_response(cmd, res)

    @staticmethod
    def _anomalous_response(cmd, res):
        # response with error
        if Const.ACK_OK < res.cmd <= Const.ACK_RESOURCE_BUSY:
            return res.cmd, None

        # unexpected response
        fmts = 'Unexpected BSMP response for {} command: {}!'
        print(fmts.format(cmd, res.cmd))
        return None, None


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
    def read_variable(self, var_id, timeout):
        """Read a variable."""
        return Const.ACK_OK, self._variables[var_id]

    def read_group_of_variables(self, group_id, timeout):
        """Read group of variables."""
        ids = [var.eid for var in self.entities.groups[group_id].variables]
        values = [self.read_variable(id)[1] for id in ids]
        return Const.ACK_OK, values

    # 0x3_
    def create_group_of_variables(self, var_ids, timeout):
        """Create new group."""
        self.entities.add_group(var_ids)
        return Const.ACK_OK, None

    def remove_all_groups_of_variables(self, timeout):
        """Remove all groups."""
        self.entities.remove_all_groups_of_variables()
        return Const.ACK_OK, None

    # 0x4_
    def request_curve_block(self, curve_id, block, timeout):
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
