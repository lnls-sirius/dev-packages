"""Control system Device Util Module."""

from siriuspy.util import get_namedtuple as _get_namedtuple


class ETypes:
    """Enumerate types."""

    DSBL_ENBL = ('Dsbl', 'Enbl')
    OFF_ON = ('Off', 'On')
    CLOSE_OPEN = ('Close', 'Open')
    DISCONN_CONN = ('Disconnected', 'Connected')
    FIXED_INCR = ('Fixed', 'Incr')
    NORM_INV = ('Normal', 'Inverse')
    UNLINK_LINK = ('Unlink', 'Link')


_et = ETypes  # syntactic sugar


class Const:
    """Const class defining power supply constants."""

    DsblEnbl = _get_namedtuple('DsblEnbl', _et.DSBL_ENBL)
    OffOn = _get_namedtuple('OffOn', _et.OFF_ON)
    CloseOpen = _get_namedtuple('CloseOpen', _et.CLOSE_OPEN)
    DisconnConn = _get_namedtuple('DisconnConn', _et.DISCONN_CONN)

    @staticmethod
    def register(name, field_names, values=None):
        """Register namedtuple."""
        return _get_namedtuple(name, field_names, values)


def add_pvslist_cte(database):
    """Add PVsList-Cte."""
    pvslist_cte_name = 'Properties-Cte'
    keys = list(database.keys())
    keys.append(pvslist_cte_name)
    keys = sorted(keys)
    database[pvslist_cte_name] = {
        'type': 'string',
        'count': len(keys),
        'value': keys,
    }
    return database
