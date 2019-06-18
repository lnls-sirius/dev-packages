"""BSMP protocol implementation."""
from .serial import Channel as _Channel
from .serial import Message as _Message


class Response:
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


class BSMP:
    """BSMP protocol implementation for Master Node."""

    def __init__(self, serial, slave_address, entities):
        """Constructor."""
        self._channel = _Channel(serial, slave_address)
        # self._variables = self.read_variables_list()
        self._entities = entities
        # Variables group cache
        self._group_cache = dict()

    @property
    def entities(self):
        """BSMP entities."""
        return self._entities

    @property
    def channel(self):
        """Serial channel to an address."""
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
        """Return id of the variables in the given group. Command 0x06."""
        # Send requestG package
        m = _Message.message(0x06, payload=[chr(group_id)])
        response = self.channel.request(m, timeout)
        # Check for errors
        if response.cmd == 0x07:
            return Response.ok, list(map(ord, response.payload))
        else:  # Error
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None

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
        """Read variable. (0x10)."""
        variable = self.entities.variables[var_id]
        m = _Message.message(0x10, payload=[chr(var_id)])
        response = self.channel.request(m, timeout=timeout)  # Returns a msg
        if response.cmd == 0x11:  # Ok
            if len(response.payload) == variable.size:
                return Response.ok, variable.load_to_value(response.payload)
        else:  # Error
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None
        return None, None

    def read_group_variables(self, group_id, timeout):
        """Read variable group. (0x12)."""
        group = self.entities.groups[group_id]
        m = _Message.message(0x12, payload=[chr(group_id)])
        response = self.channel.request(m, timeout)
        # read_group_variables takes typically 3 ms to run up to this at BBB1!
        if response.cmd == 0x13:
            if len(response.payload) == group.variables_size():
                return Response.ok, group.load_to_value(response.payload)
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

    def binop_variable(self, var_id, op, mask):
        """Perform a binary operation to variable. Command 0x24."""
        raise NotImplementedError()

    def binop_group_variables(self, group_id, op, mask):
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
                return Response.ok, None
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
                return Response.ok, None
        else:
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None

        return None, None

    # 0x4_
    def read_curve_block(self, curve_id, block, timeout):
        """Read curve block. Command 0x40."""
        curve = self.entities.curves[curve_id]
        # load = curve.nblock_to_load(block)
        # print(load)
        lsb, hsb = block * 0xff, (block & 0xff00) >> 8
        m = _Message.message(0x40, payload=[chr(curve_id), chr(hsb), chr(lsb)])
        response = self.channel.request(m, timeout)
        if response.cmd == 0x13:
            if len(response.payload) == curve.size:
                return Response.ok, curve.load_to_value(response.payload)
        else:
            if response.cmd > 0xE0 and response.cmd <= 0xE8:
                return response.cmd, None


    def write_curve_block(self, curve_id, block, value):
        """Write to curve block. Command 0x41."""
        raise NotImplementedError()

    def calc_curve_checksum(self, curve_id):
        """Recalculate curve checksum. Command 0x42."""
        raise NotImplementedError()

    # 0x5_
    def execute_function(self, func_id, input_val=None, timeout=100):
        """Execute a function. Command 0x50."""
        function = self.entities.functions[func_id]
        # Load = function id + input data
        load = [chr(func_id)] + function.value_to_load(input_val)
        m = _Message.message(0x50, payload=load)
        response = self.channel.request(m, timeout)
        # TODO: slave can also return and error message (0xE3 or 0xE5)
        if response.cmd == 0x51:
            # result of the execution
            if len(response.payload) == function.o_size:
                return Response.ok, function.load_to_value(response.payload)
        elif response.cmd == 0x53:
            # function error
            if len(response.payload) == 1:
                # TODO: the tuple order of return seems to be inverted!
                return response.payload, None
        return None, None  # reached in case of serial comm error?


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

    def read_variable(self, var_id, timeout=100):
        """Read a variable."""
        # print(var_id)
        return Response.ok, self._variables[var_id]

    def remove_all_groups(self, timeout=100):
        """Remove all groups."""
        self.entities.remove_all_groups()
        return Response.ok, None

    def read_group_variables(self, group_id, timeout=100):
        """Read group of variables."""
        ids = [var.eid for var in self.entities.groups[group_id].variables]
        # print('here')
        values = [self.read_variable(id)[1] for id in ids]
        return Response.ok, values

    def create_group(self, var_ids, timeout=100):
        """Create new group."""
        self.entities.add_group(var_ids)
        return Response.ok, None

    def execute_function(self, func_id, input_val=None, timeout=100):
        """Execute a function."""
        raise NotImplementedError()
