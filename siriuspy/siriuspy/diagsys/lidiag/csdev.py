"""Linac Diag App."""

from ... import csdev as _csdev


class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    DIAG_STATUS_LABELS_RF = (
        'Disconnected',
        'State Off',
        'Trigger Off',
        'Integral Off',
        'Feedback Off',
        'Amp-(SP|RB) are different',
        'Phase-(SP|RB) are different',
        'IxQ (SP|Mon) are different')

    DIAG_STATUS_LABELS_PU = (
        'Disconnected',
        'Run/Stop not ok',
        'PreHeat not ok',
        'Charge_Allowed not ok',
        'TrigOut_Allowed not ok',
        'Emer_Stop not ok',
        'CPS_ALL not ok',
        'Thy_Heat not ok',
        'Kly_Heat not ok',
        'LV_Rdy_OK not ok',
        'HV_Rdy_OK not ok',
        'TRIG_Rdy_OK not ok',
        'MOD_Self_Fault not ok',
        'MOD_Sys_Ready not ok',
        'TRIG_Norm not ok',
        'Pulse_Current not ok',
        'Voltage-(SP|RB) are different',
        'Current-(SP|RB) are different')

    DIAG_STATUS_LABELS_EG_HVPS = (
        'Disconnected',
        'Swicth Status Off',
        'Enable Status Off',
        'Voltage (SP|Mon) are different')

    DIAG_STATUS_LABELS_EG_FILA = (
        'Disconnected',
        'Swicth Status Off',
        'Current-(SP|Mon) are different')


_et = ETypes  # syntactic sugar


class Const(_csdev.Const):
    """Local constant types."""

    SHB = 'LI-01:RF-SHB'
    KLY1 = 'LI-01:RF-Kly-1'
    KLY2 = 'LI-01:RF-Kly-2'
    RF_DEVICES = [SHB, KLY1, KLY2]
    MOD1 = 'LI-01:PU-Modltr-1'
    MOD2 = 'LI-01:PU-Modltr-2'
    PU_DEVICES = [MOD1, MOD2]
    HVPS = 'LI-01:EG-HVPS'
    FILA = 'LI-01:EG-FilaPS'
    DEV_2_LINAME = {
        HVPS: 'LI-01:EG-HVPS',
        FILA: 'LI-01:EG-FilaPS',
        SHB: 'LA-RF:LLRF:BUN1',
        KLY1: 'LA-RF:LLRF:KLY1',
        KLY2: 'LA-RF:LLRF:KLY2',
        MOD1: 'LI-01:PU-Modltr-1',
        MOD2: 'LI-01:PU-Modltr-2'}
    ALL_DEVICES = DEV_2_LINAME.keys()

    LI_RF_AMP_TOL = 1e-2
    LI_RF_PHS_TOL = 1e-2
    LI_RF_IxQ_TOL = 1e-2
    LI_PU_VOLT_TOL = 1e-1
    LI_PU_CURR_TOL = 1e-1
    LI_HVPS_TOL = 1.5
    LI_FILAPS_TOL = 1e-1


_c = Const  # syntactic sugar


def conv_dev_2_liname(device):
    """Return Linac pvname."""
    return _c.DEV_2_LINAME[device]


def get_li_diag_status_labels(device):
    """Return Diag Status Labels enum."""
    if 'RF' in device:
        return _et.DIAG_STATUS_LABELS_RF
    if 'PU' in device:
        return _et.DIAG_STATUS_LABELS_PU
    if 'HVPS' in device:
        return _et.DIAG_STATUS_LABELS_EG_HVPS
    if 'FilaPS' in device:
        return _et.DIAG_STATUS_LABELS_EG_FILA
    raise ValueError('Labels not defined to '+device+'.')


def get_li_diag_propty_database(device):
    """Return property database of diagnostics for linac devices."""
    enums = get_li_diag_status_labels(device)
    dbase = {
        'DiagVersion-Cte': {'type': 'str', 'value': 'UNDEF'},
        'DiagStatus-Mon': {'type': 'int', 'value': 0,
                           'hilim': 1, 'hihi': 1, 'high': 1,
                           'low': -1, 'lolo': -1, 'lolim': -1
                           },
        'DiagStatusLabels-Cte': {'type': 'string', 'count': len(enums),
                                 'value': enums}
    }
    if 'RF' in device:
        atol = _c.LI_RF_AMP_TOL
        ptol = _c.LI_RF_PHS_TOL
        vtol = _c.LI_RF_IxQ_TOL
        dbase.update({
            'DiagAmpDiff-Mon': {
                'type': 'float', 'value': 0.0,
                'hilim': atol, 'hihi': atol, 'high': atol,
                'low': -atol, 'lolo': -atol, 'lolim': -atol},
            'DiagPhaseDiff-Mon': {
                'type': 'float', 'value': 0.0,
                'hilim': ptol, 'hihi': ptol, 'high': ptol,
                'low': -ptol, 'lolo': -ptol, 'lolim': -ptol},
            'DiagIxQDiff-Mon': {
                'type': 'float', 'value': 0.0,
                'hilim': vtol, 'hihi': vtol, 'high': vtol,
                'low': -vtol, 'lolo': -vtol, 'lolim': -vtol},
        })
    elif 'PU' in device:
        vtol = _c.LI_PU_VOLT_TOL
        ctol = _c.LI_PU_CURR_TOL
        dbase.update({
            'DiagVoltageDiff-Mon': {
                'type': 'float', 'value': 0.0,
                'hilim': vtol, 'hihi': vtol, 'high': vtol,
                'low': -vtol, 'lolo': -vtol, 'lolim': -vtol},
            'DiagCurrentDiff-Mon': {
                'type': 'float', 'value': 0.0,
                'hilim': ctol, 'hihi': ctol, 'high': ctol,
                'low': -ctol, 'lolo': -ctol, 'lolim': -ctol},
        })
    elif 'HVPS' in device:
        dtol = _c.LI_HVPS_TOL
        dbase.update({
            'DiagVoltDiff-Mon': {
                'type': 'float', 'value': 0.0,
                'hilim': dtol, 'hihi': dtol, 'high': dtol,
                'low': -dtol, 'lolo': -dtol, 'lolim': -dtol}})
    elif 'FilaPS' in device:
        dtol = _c.LI_FILAPS_TOL
        dbase.update({
            'DiagCurrentDiff-Mon': {
                'type': 'float', 'value': 0.0,
                'hilim': dtol, 'hihi': dtol, 'high': dtol,
                'low': -dtol, 'lolo': -dtol, 'lolim': -dtol}})
    dbase = _csdev.add_pvslist_cte(dbase, 'Diag')
    return dbase
