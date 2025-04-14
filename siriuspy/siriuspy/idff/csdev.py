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

    DEFAULT_AUTOSAVE_FOLDER = \
        _os.path.join('/home', 'sirius', 'iocs-log', 'si-ap-idff', 'data')
    DEFAULT_CORR_STATUS = 0b11111111
    DEFAULT_LOOP_FREQ_MIN = 0.001  # [Hz]
    DEFAULT_LOOP_FREQ_MAX = 100  # [Hz]
    DEFAULT_LOOP_FREQ = 10  # [Hz]
    DEFAULT_LOOP_STATE = LoopState.Open
    DEFAULT_CORR_PREC = 4

    def __init__(self, idname,
                 enbl_chcorrs=False, enbl_cvcorrs=False,
                 enbl_qscorrs=False, enbl_lccorrs=False,
                 enbl_qncorrs=False, enbl_cccorrs=False):
        """Init."""
        self.idname = _PVName(idname)
        self.idffname = 'SI-' + self.idname.sub + ':AP-IDFF'
        cname = '_'.join([self.idname.sec, self.idname.sub, self.idname.dev])
        self.configname = cname.lower()
        ioc_fol = IDFFConst.DEFAULT_AUTOSAVE_FOLDER
        self.autosave_fname = _os.path.join(ioc_fol, self.configname + '.txt')

        chnames = _IDSearch.conv_idname_2_idff_chnames(idname)
        self.enbl_chcorrs = enbl_chcorrs and len(chnames) > 0
        cvnames = _IDSearch.conv_idname_2_idff_cvnames(idname)
        self.enbl_cvcorrs = enbl_cvcorrs and len(cvnames) > 0
        qsnames = _IDSearch.conv_idname_2_idff_qsnames(idname)
        self.enbl_qscorrs = enbl_qscorrs and len(qsnames) > 0
        lcnames = _IDSearch.conv_idname_2_idff_lcnames(idname)
        self.enbl_lccorrs = enbl_lccorrs and len(lcnames) > 0
        qnnames = _IDSearch.conv_idname_2_idff_qnnames(idname)
        self.enbl_qncorrs = enbl_qncorrs and len(qnnames) > 0
        ccnames = _IDSearch.conv_idname_2_idff_ccnames(idname)
        self.enbl_cccorrs = enbl_cccorrs and len(ccnames) > 0

    def get_propty_database(self):
        """Return property database."""
        dbase = {
            'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
            'Log-Mon': {'type': 'string', 'value': 'Starting...'},
            'LoopState-Sel': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.DEFAULT_LOOP_STATE,
                'unit': 'open_closed'},
            'LoopState-Sts': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.DEFAULT_LOOP_STATE,
                'unit': 'open_closed'},
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
            'CorrSaveOffsets-Cmd': {'type': 'int', 'value': 0},
            'CorrStatus-Mon': {
                'type': 'int', 'value': self.DEFAULT_CORR_STATUS},
            'CorrStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsCorr._fields),
                'value': self.StsLblsCorr._fields},
        }
        if self.enbl_chcorrs:
            dbase.update({
                'ControlCH-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_chcorrs,
                    'unit': 'dsbl_enbl'},
                'ControlCH-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_chcorrs,
                    'unit': 'dsbl_enbl'},
                'CorrCH_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrCH_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        if self.enbl_cvcorrs:
            dbase.update({
                'ControlCV-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_cvcorrs,
                    'unit': 'dsbl_enbl'},
                'ControlCV-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_cvcorrs,
                    'unit': 'dsbl_enbl'},
                'CorrCV_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrCV_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        if self.enbl_qscorrs:
            dbase.update({
                'ControlQS-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_qscorrs,
                    'unit': 'dsbl_enbl'},
                'ControlQS-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_qscorrs,
                    'unit': 'dsbl_enbl'},
                'CorrQS_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQS_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        if self.enbl_lccorrs:
            dbase.update({
                'ControlLC-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_lccorrs,
                    'unit': 'dsbl_enbl'},
                'ControlLC-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_lccorrs,
                    'unit': 'If LC are included in loop'},
                'CorrLCHCurrent-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrLCVCurrent-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        if self.enbl_qncorrs:
            dbase.update({
                'ControlQN-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_qncorrs,
                    'unit': 'dsbl_enbl'},
                'ControlQN-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_qncorrs,
                    'unit': 'dsbl_enbl'},
                'CorrQD1_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQF_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQD2_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQD2_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQF_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrQD1_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        if self.enbl_cccorrs:
            dbase.update({
                'ControlCC-Sel': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_cccorrs,
                    'unit': 'dsbl_enbl'},
                'ControlCC-Sts': {
                    'type': 'enum', 'enums': _et.DSBL_ENBL,
                    'value': self.enbl_cccorrs,
                    'unit': 'dsbl_enbl'},
                'CorrCC1_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrCC2_1Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrCC1_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
                'CorrCC2_2Current-Mon': {
                    'type': 'float', 'value': 0,
                    'unit': 'A', 'prec': self.DEFAULT_CORR_PREC},
            })
        dbase = _csdev.add_pvslist_cte(dbase)
        return dbase
