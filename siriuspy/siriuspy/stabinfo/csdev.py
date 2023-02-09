"""Beam stability info database."""

import os as _os

from .. import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    STAB_UNSTAB = ('Stable', 'Unstable')


_et = ETypes


# --- Const class ---

class StabInfoConst(_csdev.Const):
    """Stability Info Const class."""

    StabUnstab = _csdev.Const.register('StabUnstab', _et.STAB_UNSTAB)

    SI_HARMNUM = 864

    CURR_THRES = 5  # [mA]

    DEF_BBBH_CALIBFACTOR = 1.718  # [counts/mA/um]
    DEF_BBBV_CALIBFACTOR = 4.917  # [counts/mA/um]
    DEF_BBBL_CALIBFACTOR = 1000  # [counts/mA/degree]

    BBBH_OSCAMP_THRES = 5  # [um]
    BBBV_OSCAMP_THRES = 1.5  # [um]
    BBBL_OSCAMP_THRES = 0.5  # [degree]

    def __init__(self):
        """Init."""
        ioc_fol = _os.path.join(
            '/home', 'sirius', 'iocs-log', 'si-ap-stabinfo', 'data')
        self.autosave_fname = _os.path.join(ioc_fol, 'autosave.txt')

    def get_propty_database(self):
        """Return property database."""
        dbase = {
            'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
            'Log-Mon': {'type': 'string', 'value': 'Starting...'},

            'BbBHCalibFactor-SP': {
                'type': 'float', 'value': self.DEF_BBBH_CALIBFACTOR, 'prec': 3,
                'unit': 'counts/mA/um', 'lolim': -10.0, 'hilim': 10.0},
            'BbBHCalibFactor-RB': {
                'type': 'float', 'value': self.DEF_BBBH_CALIBFACTOR, 'prec': 3,
                'unit': 'counts/mA/um', 'lolim': -10.0, 'hilim': 10.0},
            'BbBHOscAmpThres-Cte': {
                'type': 'float', 'value': self.BBBH_OSCAMP_THRES, 'prec': 3,
                'unit': 'um'},
            'BbBHOscAmp-Mon': {
                'type': 'float', 'value': 0.0, 'prec': 3, 'unit': 'um'},
            'BbBHStatus-Mon': {
                'type': 'enum', 'value': self.StabUnstab.Stable,
                'enums': _et.STAB_UNSTAB},

            'BbBVCalibFactor-SP': {
                'type': 'float', 'value': self.DEF_BBBV_CALIBFACTOR, 'prec': 3,
                'unit': 'counts/mA/um', 'lolim': -10.0, 'hilim': 10.0},
            'BbBVCalibFactor-RB': {
                'type': 'float', 'value': self.DEF_BBBV_CALIBFACTOR, 'prec': 3,
                'unit': 'counts/mA/um', 'lolim': -10.0, 'hilim': 10.0},
            'BbBVOscAmpThres-Cte': {
                'type': 'float', 'value': self.BBBV_OSCAMP_THRES, 'prec': 3,
                'unit': 'um'},
            'BbBVOscAmp-Mon': {
                'type': 'float', 'value': 0.0, 'prec': 3, 'unit': 'um'},
            'BbBVStatus-Mon': {
                'type': 'enum', 'value': self.StabUnstab.Stable,
                'enums': _et.STAB_UNSTAB},

            'BbBLCalibFactor-SP': {
                'type': 'float', 'value': self.DEF_BBBL_CALIBFACTOR, 'prec': 3,
                'unit': 'counts/mA/degree', 'lolim': 0.0, 'hilim': 10000.0},
            'BbBLCalibFactor-RB': {
                'type': 'float', 'value': self.DEF_BBBL_CALIBFACTOR, 'prec': 3,
                'unit': 'counts/mA/degree', 'lolim': 0.0, 'hilim': 10000.0},
            'BbBLOscAmpThres-Cte': {
                'type': 'float', 'value': self.BBBL_OSCAMP_THRES, 'prec': 3,
                'unit': 'degree'},
            'BbBLOscAmp-Mon': {
                'type': 'float', 'value': 0.0, 'prec': 3, 'unit': 'degree'},
            'BbBLStatus-Mon': {
                'type': 'enum', 'value': self.StabUnstab.Stable,
                'enums': _et.STAB_UNSTAB},
        }
        dbase = _csdev.add_pvslist_cte(dbase)
        return dbase
