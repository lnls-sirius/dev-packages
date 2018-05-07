"""Const class."""

from collections import namedtuple as _namedtuple


class Const:
    """Const class defining power supply constants."""

    @staticmethod
    def add_field(field_name, values):
        """Add field with constant values in const namespace."""
        for i in range(len(values)):
            if not Const._checked_ok(values[i]):
                raise ValueError('Invalid field value "{}"'.format(values[i]))
            Const._add_const(field_name, values[i], i)

    @staticmethod
    def _add_const(group, const, i):
        if not hasattr(Const, group):
            setattr(Const, group, _namedtuple(group, ''))
        obj = getattr(Const, group)
        setattr(obj, const, i)

    @staticmethod
    def _checked_ok(value):
        if not isinstance(value, str):
            return False
        if not value.replace('_','').isalnum():
            return False
        if value[0].isnumeric():
            return False
        return True
