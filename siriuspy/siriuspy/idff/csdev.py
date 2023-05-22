"""ID feedforward database."""

import os as _os

from .. import csdev as _csdev
from ..namesys import SiriusPVName as _PVName


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    OPEN_CLOSED = ('Open', 'Closed')
    STS_LBLS_CORR = (
        'Connected', 'PwrStateOn', 'OpModeConfigured',
        'SOFBModeConfigured')


_et = ETypes


# --- Const class ---

class IDFFConst(_csdev.Const):
    """ID Feedforward Const class."""

    LoopState = _csdev.Const.register('LoopState', _et.OPEN_CLOSED)
    StsLblsCorr = _csdev.Const.register(
        'StsLblsCorr', _et.STS_LBLS_CORR)

    DEFAULT_LOOP_FREQ = 5  # [Hz]

    def __init__(self, idname):
        """Init."""
        self.idname = _PVName(idname)
        self.idffname = 'SI-' + self.idname.sub + ':AP-IDFF'
        ioc_fol = _os.path.join(
            '/home', 'sirius', 'iocs-log', 'si-ap-idff', 'data')
        fname = '_'.join([self.idname.sec, self.idname.sub, self.idname.dev])
        fname = fname.lower()
        self.autosave_fname = _os.path.join(ioc_fol, fname+'.txt')

    def get_propty_database(self):
        """Return property database."""
        dbase = {
            'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
            'Log-Mon': {'type': 'string', 'value': 'Starting...'},

            'LoopState-Sel': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.LoopState.Open},
            'LoopState-Sts': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.LoopState.Open},

            'LoopFreq-SP': {
                'type': 'float', 'value': self.DEFAULT_LOOP_FREQ,
                'unit': 'Hz', 'prec': 3, 'lolim': 1e-3, 'hilim': 60},
            'LoopFreq-RB': {
                'type': 'float', 'value': self.DEFAULT_LOOP_FREQ,
                'unit': 'Hz', 'prec': 3, 'lolim': 1e-3, 'hilim': 60},

            'ControlQS-Sel': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Enbl,
                'unit': 'If QS are included in loop'},
            'ControlQS-Sts': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Enbl,
                'unit': 'If QS are included in loop'},

            'Polarization-Mon': {'type': 'string', 'value': 'none'},

            'ConfigName-SP': {'type': 'string', 'value': ''},
            'ConfigName-RB': {'type': 'string', 'value': ''},
            'SOFBMode-Sel': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Dsbl, 'unit': 'sofbmode'},
            'SOFBMode-Sts': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Dsbl, 'unit': 'sofbmode'},
            'CorrConfig-Cmd': {'type': 'int', 'value': 0},
            'CorrStatus-Mon': {'type': 'int', 'value': 0b1111},
            'CorrStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsCorr._fields),
                'value': self.StsLblsCorr._fields}
        }
        dbase = _csdev.add_pvslist_cte(dbase)
        return dbase
