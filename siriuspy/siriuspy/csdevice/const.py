"""Const class."""

from collections import namedtuple as _namedtuple


def get_namedtuple(name, field_names, values=None):
    """Return an instance of a namedtuple Class.

    Inputs:
        - name:  Defines the name of the Class (str).
        - field_names:  Defines the field names of the Class (iterable).
        - values (optional): Defines field values . If not given, the value of
            each field will be its index in 'field_names' (iterable).

    Raises ValueError if at least one of the field names are invalid.
    Raises TypeError when len(values) != len(field_names)
    """
    if values is None:
        values = range(len(field_names))
    return _namedtuple(name, field_names)(*values)


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
