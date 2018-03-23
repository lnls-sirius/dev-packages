"""BSMP entities."""
import struct as _struct


class Entity:
    """BSMP entity."""

    def _conv_value(self, fmt, value):
        if fmt == '<c':
            return value
        else:
            return list(map(chr, _struct.pack(fmt, value)))

    def _check_type(self, type_, value):
        pass

    def _conv_value_to_load(self, var_type, size, value):
        if var_type.size < size:
            for v in value:
                if not var_type.check(v):
                    raise TypeError("{}, {}".format(var_type.type, value))
        else:
            if not var_type.check(value):
                raise TypeError("{}, {}".format(var_type.type, value))
        try:
            length = len(value)
        except TypeError:
            length = 1
        if length > 1:
            load = []
            for v in value:
                load += self._conv_value(var_type.fmt, v)
            while len(load) < size:
                load += chr(0)
            return load
        else:
            return self._conv_value(var_type.fmt, value)

    def _conv_load_to_value(self, var_type, size, load):
        load = list(map(ord, load))
        if len(load) > var_type.size:  # Array
            if var_type.type == 'char':
                value = ''
                for char in load:
                    if char == 0:
                        break
                    value += '{:c}'.format(char)
                return value
            else:
                values = []
                t_size = var_type.size
                for i in range(int(size/t_size)):
                    ld = load[i*t_size:i*t_size+t_size]
                    values.append(_struct.unpack(var_type.fmt, bytes(ld))[0])
                return values
        else:
            return _struct.unpack(var_type.fmt, bytes(load))[0]


class Variable(Entity):
    """BSMP variable."""

    def __init__(self, eid, waccess, var_type, length=1):
        """Set variable properties."""
        if (var_type.size * length) > 128 or (var_type.size * length) < 1:
            raise ValueError("Variable size incorrect.")
        super().__init__()
        self.eid = eid
        self.waccess = waccess
        self.size = (var_type.size * length)  # 1..128 bytes
        self.type = var_type

    def load_to_value(self, load):
        """Parse value from load."""
        return self._conv_load_to_value(self.type, self.size, load)

    def value_to_load(self, value):
        """Convert value to load."""
        return self._conv_value_to_load(self.type, self.size, value)


class VariablesGroup(Entity):
    """BSMP variables group entity."""

    def __init__(self, eid, waccess, variables):
        """Set group parameter."""
        super().__init__()
        self.eid = eid
        self.waccess = waccess
        self.size = len(variables)
        self.variables = variables

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
        if len(value) != self.size:
            return []
        load = list()
        for i, variable in enumerate(self.variables):
            load.extend(variable.value_to_load(value[i]))
        return load

    def variables_size(self):
        """Return sum of variables size."""
        size = 0
        for variable in self.variables:
            size += variable.size
        return size


class Curve(Entity):
    """BSMP Curve entity."""

    def __init__(self, eid, waccess, sblocks, nblocks, checksum):
        """Set curve properties."""
        super().__init__()
        self.eid = eid  # Entity ID
        self.waccess = waccess
        self.sblocks = sblocks  # Block size
        self.nblocks = nblocks  # Number of blocks
        self.checksum = checksum


class Function(Entity):
    """BSMP function."""

    def __init__(self, eid, i_length, i_type, o_length, o_type):
        """Set function properties."""
        super().__init__()
        self.eid = eid
        i_size = i_type.size * i_length
        o_size = o_type.size * o_length
        if i_size < 0 or i_size > 15:
            raise ValueError("Input size {} is out of range".format(i_size))
        if o_size < 0 or o_size > 15:
            raise ValueError("Output size {} is out of range".format(o_size))
        self.i_size = i_size  # 0..15
        self.i_type = i_type
        self.o_size = o_size  # 0..15
        self.o_type = o_type

    def load_to_value(self, load):  # Parse output_size
        """Parse value from load."""
        if load is None or len(load) == 0:
            return None
        return self._conv_load_to_value(self.o_type, self.o_size, load)

    def value_to_load(self, value):
        """Convert value to load."""
        if value is None:
            return []
        return self._conv_value_to_load(self.i_type, self.i_size, value)


class Entities:
    """BSMP entities."""

    def __init__(self, variables, curves, functions):
        """Constructor."""
        # Get variables
        self._variables = list()
        for variable in variables:
            var_id = variable['id']
            write_access = variable['access']
            var_type = variable['type']
            length = variable['length']
            self._variables.append(
                Variable(var_id, write_access, var_type, length))

        # Standard groups
        r_var = [var for var in self.variablesvar if not var.waccess]
        w_var = [var for var in self.variables if var.waccess]
        self._groups = [
            VariablesGroup(0, False, self.variables),
            VariablesGroup(1, False, r_var),
            VariablesGroup(2, True, w_var),
        ]
        self._curves = []
        self._functions = []

    @property
    def variables(self):
        """Variables."""
        return self._variables

    @property
    def groups(self):
        """Groups."""
        return self._groups

    @property
    def curves(self):
        """Curves."""
        return self._curves

    @property
    def functions(self):
        """Functions."""
        return self._functions

    def add_group(self, var_ids):
        """Add group."""
        variables = []
        for var_id in var_ids:
            variables.append(self.variables[var_id])
        self.groups.append(VariablesGroup(len(self.groups), False, variables))
