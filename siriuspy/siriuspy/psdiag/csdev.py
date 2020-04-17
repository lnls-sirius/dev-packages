"""Power Supply Diag Control System App."""

from .. import csdev as _csdev
from ..search import PSSearch as _PSSearch


class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    DIAG_STATUS = (
        'PS Connected', 'PwrState-Sts On', 'OpMode-Sts SlowRef',
        'Current-(SP|Mon) differ', 'Interlocks', 'Wfm error')


_et = ETypes  # syntactic sugar


def get_ps_diag_propty_database(psname):
    """Return property database of diagnostics for power supplies."""
    pstype = _PSSearch.conv_psname_2_pstype(psname)
    splims = _PSSearch.conv_pstype_2_splims(pstype)
    dtol = splims['DTOL_CUR']
    dbase = {
        'DiagVersion-Cte': {'type': 'str', 'value': 'UNDEF'},
        'DiagCurrentDiff-Mon': {'type': 'float', 'value': 0.0,
                                'hilim': dtol, 'hihi': dtol, 'high': dtol,
                                'low': -dtol, 'lolo': -dtol, 'lolim': -dtol},
        'DiagStatus-Mon': {'type': 'int', 'value': 0,
                           'hilim': 1, 'hihi': 1, 'high': 1,
                           'low': -1, 'lolo': -1, 'lolim': -1
                           },
        'DiagStatusLabels-Cte': {'type': 'string',
                                 'count': len(_et.DIAG_STATUS),
                                 'value': _et.DIAG_STATUS}}
    dbase = _csdev.add_pvslist_cte(dbase, 'Diag')
    return dbase
