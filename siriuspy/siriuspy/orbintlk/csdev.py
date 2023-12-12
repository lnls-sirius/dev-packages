"""Define PVs, constants and properties of High Level Orbit Interlock app."""

import os as _os
import numpy as _np

from .. import csdev as _csdev
from ..util import ClassProperty as _classproperty
from ..search import BPMSearch as _BPMSearch, LLTimeSearch as _LLTimeSearch, \
    HLTimeSearch as _HLTimeSearch
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
        'AcqConfigured', 'LogTrigConfig')
    STS_LBLS_TIMING = (
        'EVGConn', 'EVGIntlkEnblSynced', 'EVGConfig',
        'FoutsConn', 'FoutsConfig',
        'AFCTimingConn', 'AFCTimingConfig',
        'AFCPhysTrigsConn', 'AFCPhysTrigsConfig',
        'OrbIntlkTrigConn', 'OrbIntlkTrigStatusOK', 'OrbIntlkTrigConfig',
        'OrbIntlkRedTrigConn', 'OrbIntlkRedTrigStatusOK',
        'OrbIntlkRedTrigConfig',
        'LLRFPsMtmTrigConn', 'LLRFPsMtmTrigStatusOK', 'LLRFPsMtmTrigConfig',
        'BPMPsMtmTrigConn', 'BPMPsMtmTrigStatusOK', 'BPMPsMtmTrigConfig',
        'DCCT13C4PsMtmTrigConn', 'DCCT13C4PsMtmTrigStatusOK',
        'DCCT13C4PsMtmTrigConfig', 'DCCT14C4PsMtmTrigConn',
        'DCCT14C4PsMtmTrigStatusOK', 'DCCT14C4PsMtmTrigConfig',
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

    DEF_TIME2WAIT_INTLKREARM = 30  # [s]

    HLTRIG_2_CONFIG = [
        ('SI-Fam:TI-BPM-OrbIntlk', (
            ('Src-Sel', 4),
            ('DelayRaw-SP', 0),
            ('State-Sel', 1),
            ('WidthRaw-SP', 1),
            ('Direction-Sel', 1))),
        ('SI-Fam:TI-OrbIntlkRedundancy', (
            ('Src-Sel', 0),
            ('State-Sel', 1),
            ('Polarity-Sel', 0),
            ('Log-Sel', 1))),
        ('SI-Glob:TI-LLRF-PsMtm', (
            ('Src-Sel', 5),
            ('DelayRaw-SP', 0),
            ('State-Sel', 1),
            ('WidthRaw-SP', 9369))),
        ('SI-Fam:TI-BPM-PsMtm', (
            ('Src-Sel', 5),
            ('DelayRaw-SP', 0),
            ('State-Sel', 1),
            ('WidthRaw-SP', 6))),
        ('SI-13C4:TI-DCCT-PsMtm', (
            ('Src-Sel', 0),
            ('State-Sel', 1),
            ('Polarity-Sel', 0),
            ('Log-Sel', 0))),
        ('SI-14C4:TI-DCCT-PsMtm', (
            ('Src-Sel', 0),
            ('State-Sel', 1),
            ('Polarity-Sel', 0),
            ('Log-Sel', 0))),
    ]
    FOUTSFIXED_RXENBL = {
        'CA-RaTim:TI-Fout-2': 0b01000001,
    }
    AFCTI_CONFIGS = (
        ('DevEnbl-Sel', 1),
        ('RTMPhasePropGain-SP', 100),
        ('RTMPhaseIntgGain-SP', 1),
        ('RTMFreqPropGain-SP', 1),
        ('RTMFreqIntgGain-SP', 128),
        ('RTMPhaseNavg-SP', 0),
        ('RTMPhaseDiv-SP', 0),
    )
    AFCPHYTRIG_CONFIGS = (
        ('Dir-Sel', 0),
        ('DirPol-Sel', 1),
        ('TrnLen-SP', 20),
    )
    SIBPMLOGTRIG_CONFIGS = (
        ('TRIGGER4TrnSrc-Sel', 1),
        ('TRIGGER4TrnOutSel-SP', 2),
        ('TRIGGER_PM0RcvSrc-Sel', 0),
        ('TRIGGER_PM0RcvInSel-SP', 2),
        ('TRIGGER_PM1RcvSrc-Sel', 0),
        ('TRIGGER_PM1RcvInSel-SP', 2),
        ('TRIGGER_PM6RcvSrc-Sel', 0),
        ('TRIGGER_PM6RcvInSel-SP', 2),
        ('TRIGGER_PM7RcvSrc-Sel', 0),
        ('TRIGGER_PM7RcvInSel-SP', 2),
        ('TRIGGER_PM11RcvSrc-Sel', 0),
        ('TRIGGER_PM11RcvInSel-SP', 2),
        ('TRIGGER_PM12RcvSrc-Sel', 0),
        ('TRIGGER_PM12RcvInSel-SP', 2),
        ('TRIGGER_PM14RcvSrc-Sel', 0),
        ('TRIGGER_PM14RcvInSel-SP', 2),
    )
    REDUNDANCY_TABLE = {
        'IA-10RaBPM:TI-AMCFPGAEVR': 'IA-10RaBPM:TI-EVR',
    }

    __EVG_CONFIGS = None
    __FOUTS_2_MON = None

    @_classproperty
    def EVG_CONFIGS(cls):
        """EVG configurations"""
        if cls.__EVG_CONFIGS is not None:
            return cls.__EVG_CONFIGS

        fouts = set()
        evgchans = set()
        evgrxenbl = list()
        for ch in _LLTimeSearch.get_connections_twds_evg():
            if ch.dev != 'BPM':
                continue
            if ch.sec != 'SI':
                continue
            if ch.dev == 'BPM' and ch.sub.endswith(('SA', 'SB', 'SP')):
                continue
            fch = _LLTimeSearch.get_fout_channel(ch)
            fouts.add(fch.device_name)
            evgch = _LLTimeSearch.get_evg_channel(fch)
            if evgch in evgchans:
                continue
            evgchans.add(evgch)
            evgrxenbl.append(int(evgch.propty[3:]))

        hlevts = _HLTimeSearch.get_hl_events()
        evtin0 = int(hlevts['Intlk'].strip('Evt'))
        evtin1 = int(hlevts['ItlkR'].strip('Evt'))
        evtin2 = int(hlevts['DCT13'].strip('Evt'))
        evtin3 = int(hlevts['DCT14'].strip('Evt'))
        evtout = int(hlevts['RFKll'].strip('Evt'))
        evgconfigs = [
            ('IntlkTbl0to15-Sel', 0b000000010000001),
            ('IntlkTbl16to27-Sel', 0),
            ('IntlkCtrlRepeat-Sel', 0),
            ('IntlkCtrlRepeatTime-SP', 0),
            ('IntlkEvtIn0-SP', evtin0),
            ('IntlkEvtIn1-SP', evtin1),
            ('IntlkEvtIn2-SP', evtin2),
            ('IntlkEvtIn3-SP', evtin3),
            ('IntlkEvtOut-SP', evtout),
            ('IntlkLogEnbl-SP', 0b11111111),
            ]
        evgconfigs.extend([(f'RxEnbl-SP.B{b}', 1) for b in evgrxenbl])

        cls.__FOUTS_2_MON = fouts
        cls.__EVG_CONFIGS = evgconfigs

        return cls.__EVG_CONFIGS

    @_classproperty
    def FOUTS_2_MON(cls):
        """Fouts to be monitored."""
        cls.EVG_CONFIGS
        return cls.__FOUTS_2_MON

    AcqChan = _csbpm.AcqChan
    AcqTrigTyp = _csbpm.AcqTrigTyp
    AcqRepeat = _csbpm.AcqRepeat
    AcqStates = _csbpm.AcqStates

    def __init__(self):
        """Class constructor."""
        # crates mapping
        self.crates_map = _LLTimeSearch.get_crates_mapping()

        # trigger source to fout out mapping
        self.trigsrc2fout_map = _LLTimeSearch.get_trigsrc2fout_mapping()

        # interlock redundancy table for fout outs
        self.intlkr_fouttable = {
            self.trigsrc2fout_map[k]: self.trigsrc2fout_map[v]
            for k, v in self.REDUNDANCY_TABLE.items()}
        self.intlkr_fouttable.update(
            {v: k for k, v in self.intlkr_fouttable.items()})

        # bpm names and nicknames
        self.bpm_names = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
        if NR_BPM != len(self.bpm_names):
            raise ValueError('Inconsistent NR_BPM parameter!')
        self.bpm_nicknames = _BPMSearch.get_nicknames(self.bpm_names)

        # bpm position along the ring
        self.bpm_pos = _BPMSearch.get_positions(self.bpm_names)

        # bpm distance for each BPM pair
        aux_pos = _np.roll(self.bpm_pos, 1)
        bpm_dist = _np.diff(aux_pos)[::2]
        # copy same distance from next high beta section to injection section
        bpm_dist[0] = bpm_dist[4*4]
        bpm_dist = _np.repeat(bpm_dist, 2)
        self.bpm_dist = _np.roll(bpm_dist, -1)

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
            'TimingStatus-Mon': {'type': 'int', 'value': (1 << 19) - 1},
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
            'BPMMonitoredDevices-Mon': {
                'type': 'char', 'count': 1000, 'value': ''},
            'TimingMonitoredDevices-Mon': {
                'type': 'char', 'count': 1000, 'value': ''},

            # Enable lists
            'PosEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'BPM used in orbit position interlock'},
            'PosEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'BPM used in orbit position interlock'},

            'AngEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'BPM used in orbit angle interlock'},
            'AngEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'BPM used in orbit angle interlock'},

            'MinSumEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
                'unit': 'BPM used with minimum sum threshold enabled'},
            'MinSumEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0],
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
            'ResetTimingLockLatches-Cmd': {'type': 'int', 'value': 0},
            'ResetAFCTimingRTMClk-Cmd': {'type': 'int', 'value': 0},

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
            'ConfigEVG-Cmd': {'type': 'int', 'value': 0},
            'ConfigFouts-Cmd': {'type': 'int', 'value': 0},
            'ConfigAFCTiming-Cmd': {'type': 'int', 'value': 0},
            'ConfigHLTriggers-Cmd': {'type': 'int', 'value': 0},
            'ConfigLLRFIntlk-Cmd': {'type': 'int', 'value': 0},
            'ConfigBPMs-Cmd': {'type': 'int', 'value': 0},
            'ConfigAFCPhyTrigs-Cmd': {'type': 'int', 'value': 0},
        }
        pvs_database = _csdev.add_pvslist_cte(pvs_database)
        return pvs_database
