"""Power Supply Diag Control System App."""

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice import util as _cutil


class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    DIAG_STATUS = (
        'PS Disconnected', 'OpMode-(Sel|Sts) differ',
        'Current-(SP|Mon) differ', 'MA Disconnected',
        'Soft Interlock',
        'Hard Interlock', 'Reserved', 'Reserved',)


_et = ETypes  # syntatic sugar


def get_ps_diag_propty_database(psname):
    """Return property database of diagnostics for power supplies."""
    pstype = _PSSearch.conv_psname_2_pstype(psname)
    splims = _PSSearch.conv_pstype_2_splims(pstype)
    dtol = splims['DTOL']
    db = {
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
    db = _cutil.add_pvslist_cte(db, 'Diag')
    return db
