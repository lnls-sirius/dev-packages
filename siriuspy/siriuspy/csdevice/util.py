"""Util module."""


class ETypes:
    """Enumerate types."""

    DSBL_ENBL = ('Dsbl', 'Enbl')
    OFF_ON = ('Off', 'On')
    CLOSE_OPEN = ('Close', 'Open')
    DISCONN_CONN = ('Disconnected', 'Connected')
    FIXED_INCR = ('Fixed', 'Incr')
    NORM_INV = ('Normal', 'Inverse')
    UNLINK_LINK = ('Unlink', 'Link')


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
