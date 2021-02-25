"""RF Diag App."""

from ... import csdev as _csdev


class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    DIAG_STATUS_LABELS_BORF = (
        'Disconnected',
        'Sirius Interlock',
        'LLRF Interlock',
        'Ramp Disabled',
        'Ramp Not Ready',
    )

    DIAG_STATUS_LABELS_SIRF = (
        'Disconnected',
        'Sirius Interlock',
        'LLRF Interlock',
        'Amplitude Error Out Of Tolerance',
        'Phase Error Out Of Tolerance',
        'Detune Error Out of Tolerance',
    )


_et = ETypes  # syntactic sugar


class Const(_csdev.Const):
    """Local constant types."""

    BO_DEV = 'BO-05D:RF-P5Cav'
    SI_DEV = 'SI-02SB:RF-P7Cav'
    ALL_DEVICES = [BO_DEV, SI_DEV]

    SI_SL_ERRTOL_AMP = 1  # [mV]
    SI_SL_ERRTOL_PHS = 1e-1  # [DEG]
    SI_SL_ERRTOL_DTU = 2  # [DEG]


_c = Const  # syntactic sugar


def get_rf_diag_status_labels(device):
    """Return Diag Status Labels enum."""
    if 'BO' in device:
        return _et.DIAG_STATUS_LABELS_BORF
    elif 'SI' in device:
        return _et.DIAG_STATUS_LABELS_SIRF
    raise ValueError('Labels not defined to '+device+'.')


def get_rf_diag_propty_database(device):
    """Return property database of diagnostics for RF devices."""
    enums = get_rf_diag_status_labels(device)
    dbase = {
        'DiagVersion-Cte': {'type': 'str', 'value': 'UNDEF'},
        'DiagStatus-Mon': {'type': 'int', 'value': 0,
                           'hilim': 1, 'hihi': 1, 'high': 1,
                           'low': -1, 'lolo': -1, 'lolim': -1},
        'DiagStatusLabels-Cte': {'type': 'string', 'count': len(enums),
                                 'value': enums},
    }
    if device.startswith('SI'):
        dbase.update({
            'DiagAmpErrSts-Mon': {'type': 'int', 'value': 0,
                                  'hilim': 1, 'hihi': 1, 'high': 1,
                                  'low': -1, 'lolo': -1, 'lolim': -1},
            'DiagPhsErrSts-Mon': {'type': 'int', 'value': 0,
                                  'hilim': 1, 'hihi': 1, 'high': 1,
                                  'low': -1, 'lolo': -1, 'lolim': -1},
            'DiagDTuneErrSts-Mon': {'type': 'int', 'value': 0,
                                    'hilim': 1, 'hihi': 1, 'high': 1,
                                    'low': -1, 'lolo': -1, 'lolim': -1},
        })
    dbase = _csdev.add_pvslist_cte(dbase, 'Diag')
    return dbase
