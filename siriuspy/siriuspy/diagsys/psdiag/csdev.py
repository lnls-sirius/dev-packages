"""Power Supply Diag App."""

from ... import csdev as _csdev
from ...namesys import SiriusPVName as _PVName
from ...search import PSSearch as _PSSearch


class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    DIAG_STATUS_LABELS_AS = (
        'PS Disconnected/Comm. Broken',
        'PwrState-Sts Off',
        'Current-(SP|Mon) are different',
        'Interlocks',
        'Alarms',
        'OpMode-(Sel|Sts) are different',
        'Reserved',
        'Reserved',
        )

    DIAG_STATUS_LABELS_LI = (
        'PS Disconnected/Comm. Broken',
        'PwrState-Sts Off',
        'Current-(SP|Mon) are different',
        'Interlocks',
        'Reserved',
        'Reserved',
        'Reserved',
        'Reserved',
        )

    DIAG_STATUS_LABELS_FC = (
        'PS Disconnected',
        'PwrState-Sts Off',
        'Current-(SP|Ref-Mon|Mon) are different',
        'Alarms - Instantaneous',
        'Alarms - Latch',
        'OpMode-(Sel|Sts) are different',
        'Reserved',
        'Triggered mode enabled',
        )

    DIAG_STATUS_LABELS_BO = (
        'PS Disconnected/Comm. Broken',
        'PwrState-Sts Off',
        'Current-(SP|Mon) are different',
        'Interlocks',
        'Alarms',
        'OpMode-(Sel|Sts) are different',
        'Wfm error exceeded tolerance',
        'Reserved',
        )


_et = ETypes  # syntactic sugar


def get_ps_diag_status_labels(psname):
    """Return Diag Status Labels enum."""
    psname = _PVName(psname)
    if psname.dev in ['FCH', 'FCV']:
        return _et.DIAG_STATUS_LABELS_FC
    if psname.sec == 'BO':
        return _et.DIAG_STATUS_LABELS_BO
    if psname.sec == 'LI':
        return _et.DIAG_STATUS_LABELS_LI
    return _et.DIAG_STATUS_LABELS_AS


def get_ps_diag_propty_database(psname):
    """Return property database of diagnostics for power supplies."""
    pstype = _PSSearch.conv_psname_2_pstype(psname)
    splims = _PSSearch.conv_pstype_2_splims(pstype)
    dtol = splims['DTOL_CUR']
    enums = get_ps_diag_status_labels(psname)
    dbase = {
        'DiagVersion-Cte': {'type': 'str', 'value': 'UNDEF'},
        'DiagCurrentDiff-Mon': {'type': 'float', 'value': 0.0,
                                'hilim': dtol, 'hihi': dtol, 'high': dtol,
                                'low': -dtol, 'lolo': -dtol, 'lolim': -dtol},
        'DiagStatus-Mon': {'type': 'int', 'value': 0,
                           'hilim': 1, 'hihi': 1, 'high': 1,
                           'low': -1, 'lolo': -1, 'lolim': -1
                           },
        'DiagStatusLabels-Cte': {'type': 'string', 'count': len(enums),
                                 'value': enums}
    }
    dbase = _csdev.add_pvslist_cte(dbase, 'Diag')
    return dbase
