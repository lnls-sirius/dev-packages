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
    DEFAULT_CONTROL_CH = _csdev.Const.DsblEnbl.Enbl
    DEFAULT_CONTROL_CV = _csdev.Const.DsblEnbl.Dsbl
    DEFAULT_CONTROL_QS = _csdev.Const.DsblEnbl.Enbl
    DEFAULT_CONTROL_LC = _csdev.Const.DsblEnbl.Dsbl
    DEFAULT_CONTROL_QD = _csdev.Const.DsblEnbl.Dsbl
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
        chnames = _IDSearch.conv_idname_2_idff_chnames(idname)
        self.has_chcorrs = True if chnames else False
        cvnames = _IDSearch.conv_idname_2_idff_cvnames(idname)
        self.has_cvcorrs = True if cvnames else False
        qsnames = _IDSearch.conv_idname_2_idff_qsnames(idname)
        self.has_qscorrs = True if qsnames else False
        lcnames = _IDSearch.conv_idname_2_idff_lcnames(idname)
        self.has_lccorrs = True if lcnames else False
        qdnames = _IDSearch.conv_idname_2_idff_qdnames(idname)
        self.has_qdcorrs = True if qdnames else False

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
        }
        if self.has_chcorrs:
            dbase.update({
                'ControlCH-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_CH,
                    'unit': 'If CH are included in loop'},
                'ControlCH-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_CH,
                    'unit': 'If CH are included in loop'},
                'CorrCH1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrCH2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        if self.has_cvcorrs:
            dbase.update({
                'ControlCV-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_CV,
                    'unit': 'If CV are included in loop'},
                'ControlCV-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_CV,
                    'unit': 'If CV are included in loop'},
                'CorrCV1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrCV2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })

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
        if self.has_lccorrs:
            dbase.update({
                'ControlLC-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_LC,
                    'unit': 'If LC are included in loop'},
                'ControlLC-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_LC,
                    'unit': 'If LC are included in loop'},
                'CorrLCHCurrent-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        if self.has_qdcorrs:
            dbase.update({
                'ControlQD-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_QD,
                    'unit': 'If LC are included in loop'},
                'ControlQD-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.DEFAULT_CONTROL_QD,
                    'unit': 'If LC are included in loop'},
                'CorrQA1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQB1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQC1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQA2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQB2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQC2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        dbase = _csdev.add_pvslist_cte(dbase)
        return dbase
