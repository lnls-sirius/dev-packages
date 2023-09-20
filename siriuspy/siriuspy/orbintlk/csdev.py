"""Define PVs, contants and properties of High Level FOFB."""

import os as _os

from .. import csdev as _csdev
from ..search import BPMSearch as _BPMSearch
from ..diagbeam.bpm.csdev import Const as _csbpm


NR_BPM = 160


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    STS_LBLS_BPMS = (
        'Connected',
        'PosEnblSynced', 'AngEnblSynced', 'MinSumSynced', 'GlobEnblSynced',
        'PosLimsSynced', 'PosLimsSynced', 'MinSumLimsSynced')
    STS_LBLS_EVG = (
        'Connected', 'IntlkEnblSynced')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining Orbit Interlock constants."""

    CONV_UM_2_NM = 1e3

    DEF_TIMEOUT = 10  # [s]
    DEF_TIMESLEEP = 0.1  # [s]
    DEF_TIMEWAIT = 3  # [s]

    DEF_TIME2WAIT_DRYRUN = 10  # [s]

    State = _csdev.Const.register('State', _et.OFF_ON)

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

        self.limits = _os.path.join(path, 'limits.txt')

    def get_database(self):
        """Return Soft IOC database."""
        pvs_database = {
            # Global
            'Version-Cte': {'type': 'string', 'value': 'UNDEF'},
            'Log-Mon': {'type': 'string', 'value': 'Starting...'},

            'State-Sel': {
                'type': 'enum', 'enums': _et.OFF_ON,
                'value': self.OffOn.Off},
            'State-Sts': {
                'type': 'enum', 'enums': _et.OFF_ON,
                'value': self.OffOn.Off},
            'BPMStatus-Mon': {'type': 'int', 'value': 0b1111111},
            'EVGStatus-Mon': {'type': 'int', 'value': 0b11},

            # Enable lists
            'BPMPosEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit position interlock'},
            'BPMPosEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit position interlock'},

            'BPMAngEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit angle interlock'},
            'BPMAngEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used in orbit angle interlock'},

            'BPMMinSumEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used with minimum sum threshold enabled'},
            'BPMMinSumEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPM used with minimum sum threshold enabled'},

            # Limits
            'PosMinLimX-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for X'},
            'PosMinLimX-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for X'},
            'PosMaxLimX-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for X'},
            'PosMaxLimX-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for X'},

            'PosMinLimY-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for Y'},
            'PosMinLimY-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position minimum limits for Y'},
            'PosMaxLimY-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for Y'},
            'PosMaxLimY-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'position maximum limits for Y'},

            'AngMinLimX-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for X'},
            'AngMinLimX-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for X'},
            'AngMaxLimX-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for X'},
            'AngMaxLimX-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for X'},

            'AngMinLimY-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for Y'},
            'AngMinLimY-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle minimum limits for Y'},
            'AngMaxLimY-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for Y'},
            'AngMaxLimY-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'angle maximum limits for Y'},

            'MinSumLim-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0], 'unit': 'minimum sum limits'},
            'MinSumLim-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0], 'unit': 'minimum sum limits'},

            # Reset
            'ResetBPMGen-Cmd': {'type': 'int', 'value': 0},
            'ResetBPMPos-Cmd': {'type': 'int', 'value': 0},
            'ResetBPMAng-Cmd': {'type': 'int', 'value': 0},
            'ResetBPM-Cmd': {'type': 'int', 'value': 0},
            'Reset-Cmd': {'type': 'int', 'value': 0},

            # Acquisition
            'PsMtmAcqChannel-Sel': {
                'type': 'enum', 'value': _csbpm.AcqChan.FAcq,
                'enums': Const.AcqChan._fields},
            'PsMtmAcqChannel-Sts': {
                'type': 'enum', 'value': _csbpm.AcqChan.FAcq,
                'enums': Const.AcqChan._fields},
            'PsMtmAcqSamplesPre-SP': {
                'type': 'int', 'value': 5000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqSamplesPre-RB': {
                'type': 'int', 'value': 5000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqSamplesPost-SP': {
                'type': 'int', 'value': 5000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqSamplesPost-RB': {
                'type': 'int', 'value': 5000, 'lolim': 0, 'hilim': 1_000_000},
            'PsMtmAcqConfig-Cmd': {'type': 'int', 'value': 0},

            # TODO:
            # add commands to sync enable status and limits
        }
        pvs_database = _csdev.add_pvslist_cte(pvs_database)
        return pvs_database
