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
        if hasattr(Const, field_name):
            raise NameError('Field "{}" already exists.'.format(field_name))
        const = get_namedtuple(field_name, values)
        setattr(Const, field_name, const)
