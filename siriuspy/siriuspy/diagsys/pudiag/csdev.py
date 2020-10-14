"""Pulsed Power Supply Diag App."""

from ... import csdev as _csdev
from ...search import PSSearch as _PSSearch


class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    DIAG_STATUS_LABELS_PU = (
        'PU Disconnected',
        'PwrState-Sts Off',
        'Pulse-Sts Off',
        'Voltage-(SP|Mon) are different',
        'Interlocks')


_et = ETypes  # syntactic sugar


def get_pu_diag_status_labels():
    """Return Diag Status Labels enum."""
    return _et.DIAG_STATUS_LABELS_PU


def get_pu_diag_propty_database(puname):
    """Return property database."""
    pstype = _PSSearch.conv_psname_2_pstype(puname)
    splims = _PSSearch.conv_pstype_2_splims(pstype)
    dtol = splims['DTOL_CUR']
    enums = get_pu_diag_status_labels()
    dbase = {
        'DiagVersion-Cte': {'type': 'str', 'value': 'UNDEF'},
        'DiagVoltageDiff-Mon': {'type': 'float', 'value': 0.0,
                                'hilim': dtol, 'hihi': dtol, 'high': dtol,
                                'low': -dtol, 'lolo': -dtol, 'lolim': -dtol},
        'DiagStatus-Mon': {'type': 'int', 'value': 0,
                           'hilim': 1, 'hihi': 1, 'high': 1,
                           'low': -1, 'lolo': -1, 'lolim': -1},
        'DiagStatusLabels-Cte': {'type': 'string', 'count': len(enums),
                                 'value': enums}
    }
    dbase = _csdev.add_pvslist_cte(dbase, 'Diag')
    return dbase
