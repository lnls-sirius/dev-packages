"""ID feedforward database."""

import os as _os

from .. import csdev as _csdev
from ..namesys import SiriusPVName as _PVName
from ..search import IDSearch as _IDSearch


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    OPEN_CLOSED = ('Open', 'Closed')
    STS_LBLS_CORR = (
        'Connected', 'PwrStateOn', 'OpModeConfigured')


_et = ETypes


# --- Const class ---

class IDFFConst(_csdev.Const):
    """ID Feedforward Const class."""

    LoopState = _csdev.Const.register('LoopState', _et.OPEN_CLOSED)
    StsLblsCorr = _csdev.Const.register(
        'StsLblsCorr', _et.STS_LBLS_CORR)

    DEFAULT_CORR_STATUS = 0b11111111
    DEFAULT_LOOP_FREQ_MIN = 0.001  # [Hz]
    DEFAULT_LOOP_FREQ_MAX = 100  # [Hz]
    DEFAULT_LOOP_FREQ = 10  # [Hz]
    DEFAULT_LOOP_STATE = LoopState.Open
    DEFAULT_CONTROL_QS = _csdev.Const.DsblEnbl.Enbl
    DEFAULT_CORR_PREC = 4

    def __init__(self, idname):
        """Init."""
        self.idname = _PVName(idname)
        self.idffname = 'SI-' + self.idname.sub + ':AP-IDFF'
        ioc_fol = _os.path.join(
            '/home', 'sirius', 'iocs-log', 'si-ap-idff', 'data')
        fname = '_'.join([self.idname.sec, self.idname.sub, self.idname.dev])
        fname = fname.lower()
        self.autosave_fname = _os.path.join(ioc_fol, fname+'.txt')
        qsnames = _IDSearch.conv_idname_2_idff_qsnames(idname)
        self.has_qscorrs = True if qsnames else False

    def get_propty_database(self):
        """Return property database."""
        dbase = {
            'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
            'Log-Mon': {'type': 'string', 'value': 'Starting...'},
            'LoopState-Sel': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.DEFAULT_LOOP_STATE},
            'LoopState-Sts': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.DEFAULT_LOOP_STATE},
            'LoopFreq-SP': {
                'type': 'float', 'value': self.DEFAULT_LOOP_FREQ,
                'unit': 'Hz', 'prec': 3,
                'lolim': self.DEFAULT_LOOP_FREQ_MIN,
                'hilim': self.DEFAULT_LOOP_FREQ_MAX},
            'LoopFreq-RB': {
                'type': 'float', 'value': self.DEFAULT_LOOP_FREQ,
                'unit': 'Hz', 'prec': 3,
                'lolim': self.DEFAULT_LOOP_FREQ_MIN,
                'hilim': self.DEFAULT_LOOP_FREQ_MAX},
            'Polarization-Mon': {'type': 'string', 'value': 'none'},
            'ConfigName-SP': {'type': 'string', 'value': ''},
            'ConfigName-RB': {'type': 'string', 'value': ''},
            'CorrConfig-Cmd': {'type': 'int', 'value': 0},
            'CorrStatus-Mon': {
                'type': 'int', 'value': self.DEFAULT_CORR_STATUS},
            'CorrStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsCorr._fields),
                'value': self.StsLblsCorr._fields},
            'CorrCH1Current-Mon': {
                'type': 'float', 'value': 0,
                'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            'CorrCH2Current-Mon': {
                'type': 'float', 'value': 0,
                'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            'CorrCV1Current-Mon': {
                'type': 'float', 'value': 0,
                'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            'CorrCV2Current-Mon': {
                'type': 'float', 'value': 0,
                'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
        }
        if self.has_qscorrs:
            dbase.update({
                'ControlQS-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_QS,
                    'unit': 'If QS are included in loop'},
                'ControlQS-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_QS,
                    'unit': 'If QS are included in loop'},
                'CorrQS1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQS2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        dbase = _csdev.add_pvslist_cte(dbase)
        return dbase
