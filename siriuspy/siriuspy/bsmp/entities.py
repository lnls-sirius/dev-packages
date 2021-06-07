"""BSMP entities."""
import struct as _struct
import typing

import numpy as _np

from .types import BSMPType


class Entity:
    """BSMP entity."""

    def _conv_value(self, fmt: str, value) -> typing.List[str]:
        if fmt == '<c':
            return value
        else:
            return [chr(c) for c in _struct.pack(fmt, value)]

    def _check_type(self, var_type: BSMPType, value: typing.Union[str, int, float]):
        if not var_type.check(value):
            raise TypeError("{}, {}".format(var_type.type, value))

    def _calc_types_size(
        self,
        var_types: typing.Tuple[BSMPType],
    ) -> int:
        size = 0
        try:
            for var_type in var_types:
                size += var_type.size
        except TypeError:
            if isinstance(var_types, BSMPType):
                return var_types.size
            else:
                raise TypeError("Failed to calc types size, invalid type {}".format(var_types))

        return size

    def _conv_value_to_load(
        self,
        var_types: typing.Union[typing.Tuple[BSMPType], typing.List[BSMPType]],
        size: int,
        values: typing.Union[str, typing.List[str]]
    ) -> typing.List[str]:
        if len(var_types) > 1:
            load: typing.List[str] = []
            for idx, value in enumerate(values):
                self._check_type(var_types[idx], value)
                load += self._conv_value(var_types[idx].fmt, value)
            while len(load) < size:
                load += chr(0)
            return load
        else:
            self._check_type(var_types[0], values[0])
            return self._conv_value(var_types[0].fmt, values[0])

    def _conv_load_to_value(
        self,
        var_types: typing.Union[typing.Tuple[BSMPType], typing.List[BSMPType]],
        load: typing.List[str]
    ) -> typing.Union[str, float, int, typing.List[typing.Union[str, float, int]]]:
        """Return a value or a list of values unpacked according to the BMSPType.fmt"""
        # NOTE: optimize this critical function!
        _load = list(map(ord, load))
        if len(var_types) > 1:
            values = []
            offset = 0
            for var_type in var_types:
                datum = _load[offset:offset+var_type.size]
                values.append(_struct.unpack(var_type.fmt, bytes(datum))[0])
                offset += var_type.size
            return values
        return _struct.unpack(var_types[0].fmt, bytes(_load))[0]


class Variable(Entity):
    """BSMP variable."""

    def __init__(self, eid: int, waccess: bool, var_type: BSMPType, count: int = 1):
        """Set variable properties."""
        if (var_type.size * count) > 128 or (var_type.size * count) < 1:
            errstr = ('Variable size incorrect: eid:{}, '
                      'vtype_size:{}, count:{}').format(eid, var_type.size,
                                                        count)
            raise ValueError(errstr)
        super().__init__()  # NOTE: is it necessary?
        self.eid: int = eid
        self.waccess: bool = waccess
        self.size: int = (var_type.size * count)  # 1..128 bytes
        self.type: BSMPType = var_type

        self._var_types: typing.List[BSMPType] = [var_type for _ in range(count)]

    def load_to_value(self, load: typing.List[str]):
        """Parse value from load."""
        return self._conv_load_to_value(self._var_types, load)

    def value_to_load(self, value) -> typing.List[str]:
        """Convert value to load."""
        if not isinstance(value, (list, tuple, _np.ndarray)):
            value = [value, ]
        return self._conv_value_to_load(self._var_types, self.size, value)


class VariablesGroup(Entity):
    """BSMP variables group entity."""

    ALL: int = 0
    READ_ONLY: int = 1
    WRITEABLE: int = 2

    def __init__(
        self,
        eid: int,
        waccess: bool,
        variables: typing.List[Variable]
    ):
        """Set group parameter."""
        super().__init__()
        self.eid: int = eid
        self.waccess: bool = waccess
        self.size: int = len(variables)
        self.variables: typing.List[Variable] = variables

    def load_to_value(self, load: typing.List[str]) -> typing.List[typing.Union[str, float, int]]:
        """Parse value from load."""
        value: typing.List[typing.Union[str, float, int]] = []
        offset = 0
        for variable in self.variables:
            i, j = offset, offset + variable.size
            value.append(variable.load_to_value(load[i:j]))
            offset += variable.size
        return value

    def value_to_load(
        self,
        value: typing.List
    ) -> typing.List[str]:
        """Parse load from value."""
        if len(value) != self.size:
            # Value list must match the amount of variables
            return []
        load: typing.List[str] = []
        for i, variable in enumerate(self.variables):
            load.extend(variable.value_to_load(value[i]))
        return load

    def variables_size(self) -> int:
        """Return sum of variables size."""
        size = 0
        for variable in self.variables:
            size += variable.size
        return size


class Curve(Entity):
    """BSMP Curve entity."""

    def __init__(
        self,
        eid: int,
        waccess: bool,
        var_type: BSMPType,
        nblocks: int,
        count: int
    ):
        """Set curve properties."""
        super().__init__()
        self.eid: int = eid  # Entity ID
        self.waccess: bool = waccess
        self.size: int = (var_type.size * count)  # 1..128 bytes
        self.type: BSMPType = var_type
        self.nblocks: int = nblocks  # Number of blocks
        self.max_size_t_float: int = self.nblocks * (self.size // self.type.size)
        self._var_types: typing.List[BSMPType] = [var_type for _ in range(count)]

    def load_to_value(self, load: typing.List[str]):
        """Parse value from load."""
        _load = [ord(c) for c in load]
        values = []
        offset = 0
        for var_type in self._var_types:
            datum = _load[offset:offset+var_type.size]
            values.append(_struct.unpack(var_type.fmt, bytes(datum))[0])
            offset += var_type.size
            if offset >= len(_load):
                break
        return values

    def value_to_load(self, value) -> typing.List[str]:
        """Convert curve block number to load."""
        load: typing.List[str] = []
        for idx, val in enumerate(value):
            self._check_type(self._var_types[idx], val)
            load += self._conv_value(self._var_types[idx].fmt, val)
        return load

    def get_indices(self, data_length) -> typing.List[typing.Tuple[int, int]]:
        """Return list of indices corresponding to data blocks."""
        block_len = self.size // self.type.size
        nblocks = int(_np.ceil(data_length / block_len))
        indices: typing.List[typing.Tuple[int, int]] = []
        for i in range(nblocks-1):
            indices.append((block_len*i, block_len*(i+1)))
        indices.append((block_len*(nblocks-1), data_length))
        return indices


class Function(Entity):
    """BSMP function."""

    def __init__(
        self,
        eid: int,
        i_type: typing.Tuple[BSMPType],
        o_type: typing.Tuple[BSMPType]
    ):
        """Set function properties."""
        super().__init__()
        self.eid: int = eid
        i_size: int = self._calc_types_size(i_type)
        o_size: int = self._calc_types_size(o_type)
        if i_size < 0 or i_size > 64:
            raise ValueError("Input size {} is out of range".format(i_size))
        if o_size < 0 or o_size > 32:
            raise ValueError("Output size {} is out of range".format(o_size))

        self.i_size: int = i_size  # 0..64
        self.i_type: typing.Tuple[BSMPType] = i_type

        self.o_size: int = o_size  # 0..32
        self.o_type: typing.Tuple[BSMPType] = o_type

    def load_to_value(self, load: typing.Optional[typing.List[str]]):  # Parse output_size
        """Parse value from load."""
        if load is None or not load:
            return None
        return self._conv_load_to_value(self.o_type, load)

    def value_to_load(self, value) -> typing.List:
        """Convert value to load."""
        if value is None:
            return []
        if not isinstance(value, (list, tuple, _np.ndarray)):
            value = [value, ]
        return self._conv_value_to_load(self.i_type, self.i_size, value)


class Entities:
    """BSMP entities."""

    def __init__(
        self,
        variables: typing.Tuple[typing.Union[Variable, typing.Dict[str, typing.Any]]],
        curves: typing.Tuple[typing.Union[Curve, typing.Dict[str, typing.Any]]],
        functions: typing.Tuple[typing.Union[Function, typing.Dict[str, typing.Any]]]
    ):
        """Constructor."""
        # Get variables
        self._variables: typing.List[Variable] = []
        for variable in variables:

            if isinstance(variable, Variable):
                self.variables.append(variable)
                continue

            var_id = variable['eid']
            waccess = variable['waccess']
            var_type = variable['var_type']
            count = variable['count']
            self.variables.append(
                Variable(var_id, waccess, var_type, count)
            )

        # Standard groups
        self._groups: typing.List[VariablesGroup] = []
        self.reset_group()

        self._curves: typing.List[Curve] = []
        for curve in curves:

            if isinstance(curve, Curve):
                self.curves.append(curve)
                continue

            curve_id = curve['eid']
            waccess = curve['waccess']
            nblocks = curve['nblocks']
            count = curve['count']
            var_type = curve['var_type']
            self.curves.append(
                Curve(curve_id, waccess, var_type, nblocks, count))

        self._functions: typing.List[Function] = []
        for function in functions:

            if isinstance(function, Function):
                self.functions.append(function)
                continue

            func_id = function['eid']
            i_type = function['i_type']
            o_type = function['o_type']
            self.functions.append(Function(func_id, i_type, o_type))

    @property
    def variables(self) -> typing.List[Variable]:
        """Variables."""
        return self._variables

    @property
    def groups(self) -> typing.List[VariablesGroup]:
        """Groups."""
        return self._groups

    @property
    def curves(self) -> typing.List[Curve]:
        """Curves."""
        return self._curves

    @property
    def functions(self) -> typing.List[Function]:
        """Functions."""
        return self._functions

    def reset_group(self) -> None:
        """."""
        r_var = [var for var in self.variables if not var.waccess]
        w_var = [var for var in self.variables if var.waccess]
        self._groups = [
            VariablesGroup(0, False, self.variables),
            VariablesGroup(1, False, r_var),
            VariablesGroup(2, True, w_var),
        ]

    def add_group(self, var_ids: typing.List[int], waccess: bool = False):
        """Add group."""
        variables: typing.List[Variable] = []
        for var_id in var_ids:
            variables.append(self.variables[var_id])
        self.groups.append(VariablesGroup(len(self.groups), waccess, variables))

    def remove_all_groups_of_variables(self) -> None:
        """Remove all groups bigger than eid 2."""
        self._groups = self.groups[:3]

    def list_variables(self, group_id: int) -> typing.List[int]:
        """List variable ids."""
        return [var.eid for var in self.groups[group_id].variables]
