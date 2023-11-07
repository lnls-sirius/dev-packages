"""Define PVs, constants and properties of High Level Orbit Interlock app."""

import os as _os

from .. import csdev as _csdev
from ..search import BPMSearch as _BPMSearch
from ..namesys import SiriusPVName as _PVName
from ..diagbeam.bpm.csdev import Const as _csbpm


NR_BPM = 160


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    STS_LBLS_BPM = (
        'Connected',
        'PosEnblSynced', 'AngEnblSynced', 'MinSumEnblSynced', 'GlobEnblSynced',
        'PosLimsSynced', 'AngLimsSynced', 'MinSumLimsSynced',
        'AcqConfigured')
    STS_LBLS_TIMING = (
        'EVGConn', 'EVGIntlkEnblSynced', 'EVGConfig',
        'FoutsConn', 'FoutsConfig',
        'OrbIntlkTrigConn', 'OrbIntlkTrigStatusOK', 'OrbIntlkTrigConfig',
        'LLRFPsMtnTrigConn', 'LLRFPsMtnTrigStatusOK', 'LLRFPsMtnTrigConfig',
        'BPMPsMtnTrigConn', 'BPMPsMtnTrigStatusOK', 'BPMPsMtnTrigConfig',
        )
    STS_LBLS_LLRF = ('Connected', 'Configured')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining Orbit Interlock constants."""

    CONV_UM_2_NM = 1e3

    IOC_PREFIX = _PVName('SI-Glob:AP-OrbIntlk')
    DEF_TIMEOUT = 10  # [s]
    DEF_TIMESLEEP = 0.1  # [s]
    DEF_TIMEWAIT = 3  # [s]

    DEF_TIME2WAIT_INTLKREARM = 10  # [s]

    EVG_CONFIGS = (
        ('IntlkTbl0to15-Sel', 0b010000010000001),
        ('IntlkTbl16to27-Sel', 0),
        ('IntlkCtrlRepeat-Sel', 0),
        ('IntlkCtrlRepeatTime-SP', 0),
        ('IntlkEvtIn0-SP', 117),
        ('IntlkEvtOut-SP', 124),
        ('RxEnbl-SP', 0b00011110),
        )
    FOUTS_CONFIGS = {
        # NOTE: change RxEnbl when unnecessary
        # protection in gateware is removed
        2: (('RxEnbl-SP', 0b01000000), ),
        3: (('RxEnbl-SP', 0b01001011), ),  # 0b01111111
        4: (('RxEnbl-SP', 0b00001111), ),  # 0b01111111
        5: (('RxEnbl-SP', 0b00001111), ),  # 0b00111111
    }
    ORBINTLKTRIG_CONFIG = (
        ('Src-Sel', 4),
        ('DelayRaw-SP', 0),
        ('State-Sel', 1),
        ('WidthRaw-SP', 1),
        ('Direction-Sel', 1),
        )
    LLRFTRIG_CONFIG = (
        ('Src-Sel', 5),
        ('DelayRaw-SP', 0),
        ('State-Sel', 1),
        ('WidthRaw-SP', 9369),
        )
    BPMPSMTNTRIG_CONFIG = (
        ('Src-Sel', 5),
        ('DelayRaw-SP', 0),
        ('State-Sel', 1),
        ('WidthRaw-SP', 6),
        )

    AcqChan = _csbpm.AcqChan
    AcqTrigTyp = _csbpm.AcqTrigTyp
    AcqRepeat = _csbpm.AcqRepeat

    def __init__(self):
        """Class constructor."""

        # bpm names and nicknames
        self.bpm_names = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
        if NR_BPM != len(self.bpm_names):
            raise ValueError('Inconsistent NR_BPM parameter!')
        self.bpm_nicknames = _BPMSearch.get_nicknames(self.bpm_names)

        # bpm position along the ring
        self.bpm_pos = _BPMSearch.get_positions(self.bpm_names)

        # bpm number
        self.nr_bpms = len(self.bpm_names)

        # data folder
        path = _os.path.join(
            '/home', 'sirius', 'iocs-log', 'si-ap-orbintlk', 'data')
        self.pos_enbl_fname = _os.path.join(path, 'pos_enbllist.enbl')
        self.ang_enbl_fname = _os.path.join(path, 'ang_enbllist.enbl')
        self.minsum_enbl_fname = _os.path.join(path, 'minsum_enbllist.enbl')

        self.pos_x_min_lim_fname = _os.path.join(path, 'pos_x_min.lim')
        self.pos_x_max_lim_fname = _os.path.join(path, 'pos_x_max.lim')
        self.pos_y_min_lim_fname = _os.path.join(path, 'pos_y_min.lim')
        self.pos_y_max_lim_fname = _os.path.join(path, 'pos_y_max.lim')
        self.ang_x_min_lim_fname = _os.path.join(path, 'ang_x_min.lim')
        self.ang_x_max_lim_fname = _os.path.join(path, 'ang_x_max.lim')
        self.ang_y_min_lim_fname = _os.path.join(path, 'ang_y_min.lim')
        self.ang_y_max_lim_fname = _os.path.join(path, 'ang_y_max.lim')
        self.minsum_lim_fname = _os.path.join(path, 'minsum.lim')

    def get_database(self):
        """Return Soft IOC database."""
        pvs_database = {
            # Global
            'Version-Cte': {'type': 'string', 'value': 'UNDEF'},
            'Log-Mon': {'type': 'string', 'value': 'Starting...'},

            'Enable-Sel': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Dsbl},
            'Enable-Sts': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Dsbl},
            'BPMStatus-Mon': {'type': 'int', 'value': 0b111111111},
            'TimingStatus-Mon': {'type': 'int', 'value': 0b111111111},
            'LLRFStatus-Mon': {'type': 'int', 'value': 0b11},
            'BPMStatusLabels-Cte': {
                'type': 'string', 'count': len(_et.STS_LBLS_BPM),
                'value': _et.STS_LBLS_BPM},
            'TimingStatusLabels-Cte': {
                'type': 'string', 'count': len(_et.STS_LBLS_TIMING),
                'value': _et.STS_LBLS_TIMING},
            'LLRFStatusLabels-Cte': {
                'type': 'string', 'count': len(_et.STS_LBLS_LLRF),
                'value': _et.STS_LBLS_LLRF},
            'TimingMonitoredDevices-Mon': {
                'type': 'char', 'count': 1000, 'value': ''},

            # Enable lists
            'PosEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit position interlock'},
            'PosEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit position interlock'},

            'AngEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit angle interlock'},
            'AngEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit angle interlock'},

            'MinSumEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used with minimum sum threshold enabled'},
            'MinSumEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used with minimum sum threshold enabled'},

            # Limits
            'PosXMinLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for X'},
            'PosXMinLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for X'},
            'PosXMaxLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for X'},
            'PosXMaxLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for X'},

            'PosYMinLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for Y'},
            'PosYMinLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for Y'},
            'PosYMaxLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for Y'},
            'PosYMaxLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for Y'},

            'AngXMinLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for X'},
            'AngXMinLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for X'},
            'AngXMaxLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for X'},
            'AngXMaxLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for X'},

            'AngYMinLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for Y'},
            'AngYMinLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for Y'},
            'AngYMaxLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for Y'},
            'AngYMaxLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for Y'},

            'MinSumLim-SP': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0], 'unit': 'minimum sum limits'},
            'MinSumLim-RB': {
                'type': 'float', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0], 'unit': 'minimum sum limits'},

            # Reset
            'ResetBPMGen-Cmd': {'type': 'int', 'value': 0},
            'ResetBPMPos-Cmd': {'type': 'int', 'value': 0},
            'ResetBPMAng-Cmd': {'type': 'int', 'value': 0},
            'ResetBPM-Cmd': {'type': 'int', 'value': 0},
            'Reset-Cmd': {'type': 'int', 'value': 0},

            # Acquisition
            'PsMtmAcqChannel-Sel': {
                'type': 'enum', 'value': self.AcqChan.TbT,
                'enums': self.AcqChan._fields},
            'PsMtmAcqChannel-Sts': {
                'type': 'enum', 'value': self.AcqChan.TbT,
                'enums': self.AcqChan._fields},
            'PsMtmAcqSamplesPre-SP': {
                'type': 'int', 'value': 20000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqSamplesPre-RB': {
                'type': 'int', 'value': 20000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqSamplesPost-SP': {
                'type': 'int', 'value': 20000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqSamplesPost-RB': {
                'type': 'int', 'value': 20000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqConfig-Cmd': {'type': 'int', 'value': 0},

            # Config devices
            'IntlkStateConfig-Cmd': {'type': 'int', 'value': 0}
        }
        pvs_database = _csdev.add_pvslist_cte(pvs_database)
        return pvs_database
