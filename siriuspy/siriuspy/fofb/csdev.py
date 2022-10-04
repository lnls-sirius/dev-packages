"""Define PVs, contants and properties of High Level FOFB."""

import os as _os

from .. import csdev as _csdev
from ..search import PSSearch as _PSSearch, MASearch as _MASearch, \
    BPMSearch as _BPMSearch


NR_BPM = 160


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    OPEN_CLOSED = ('Open', 'Closed')

    GLOB_INDIV = ('Global', 'Individual')

    MEAS_RMAT_CMD = ('Start', 'Stop', 'Reset')
    MEAS_RMAT_MON = ('Idle', 'Measuring', 'Completed', 'Aborted')

    STS_LBLS_CORR = (
        'Connected', 'PwrStateOn', 'OpModeConfigured', 'AccFreezeConfigured',
        'InvRespMatRowSynced', 'AccGainSynced')
    STS_LBLS_FOFBCTRL = (
        'Connected', 'BPMIdsConfigured', 'NetSynced', 'LinkPartnerConnected',
        'RefOrbSynced', 'TimeFrameLenSynced', 'BPMLogTrigsConfigured')


_et = ETypes  # syntactic sugar


# --- Const class ---

class HLFOFBConst(_csdev.Const):
    """Const class defining High Level FOFB constants."""

    MIN_SING_VAL = 0.2
    TIKHONOV_REG_CONST = 0
    SINGVALHW_THRS = 1e-14

    CONV_UM_2_NM = 1e3
    ACCGAIN_RESO = 2**-12

    LoopState = _csdev.Const.register('LoopState', _et.OPEN_CLOSED)
    GlobIndiv = _csdev.Const.register('GlobIndiv', _et.GLOB_INDIV)
    UseRF = _csdev.Const.register('UseRF', _et.DSBL_ENBL)
    MeasRespMatCmd = _csdev.Const.register('MeasRespMatCmd', _et.MEAS_RMAT_CMD)
    MeasRespMatMon = _csdev.Const.register('MeasRespMatMon', _et.MEAS_RMAT_MON)

    def __init__(self):
        """Class constructor."""

        # device names and nicknames
        self.bpm_names = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
        if NR_BPM != len(self.bpm_names):
            raise ValueError('Inconsistent NR_BPM parameter!')
        self.ch_names = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCH'})
        self.cv_names = _PSSearch.get_psnames({'sec': 'SI', 'dev': 'FCV'})

        self.bpm_nicknames = _BPMSearch.get_nicknames(self.bpm_names)
        self.ch_nicknames = _PSSearch.get_psnicknames(self.ch_names)
        self.cv_nicknames = _PSSearch.get_psnicknames(self.cv_names)

        # device position along the ring
        self.bpm_pos = _BPMSearch.get_positions(self.bpm_names)
        self.ch_pos = _MASearch.get_mapositions(map(
            lambda x: x.substitute(dis='MA'), self.ch_names))
        self.cv_pos = _MASearch.get_mapositions(map(
            lambda x: x.substitute(dis='MA'), self.cv_names))

        # total number of devices
        self.nr_bpms = NR_BPM
        self.nr_ch = len(self.ch_names)
        self.nr_cv = len(self.cv_names)
        self.nr_chcv = self.nr_ch + self.nr_cv
        self.nr_corrs = self.nr_chcv + 1  # include RF

        # data folder
        ioc_fol = _os.path.join(
            '/home', 'sirius', 'iocs-log', 'si-ap-fofb', 'data')
        self.reforb_fname = _os.path.join(ioc_fol, 'reforbit.orb')
        self.respmat_fname = _os.path.join(ioc_fol, 'respmat.respmat')

        # reforb and matrix parameters
        self.reforb_size = self.nr_bpms
        self.matrix_size = self.nr_corrs * (2 * self.nr_bpms)
        self.nr_svals = min(self.nr_corrs, 2 * self.nr_bpms)
        self.corrcoeffs_size = self.nr_chcv * (2 * self.nr_bpms)
        self.corrgains_size = self.nr_chcv

    def get_hlfofb_database(self):
        """Return Soft IOC database."""
        pvs_database = {
            # Global
            'Version-Cte': {'type': 'string', 'value': 'UNDEF'},
            'Log-Mon': {'type': 'string', 'value': 'Starting...'},

            'LoopState-Sel': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.LoopState.Open},
            'LoopState-Sts': {
                'type': 'enum', 'enums': _et.OPEN_CLOSED,
                'value': self.LoopState.Open},
            'LoopGain-SP': {
                'type': 'float', 'value': 1, 'prec': 4,
                'lolim': -2**3, 'hilim': 2**3-1,
                'unit': 'Global FOFB pre-accumulator gain.'},
            'LoopGain-RB': {
                'type': 'float', 'value': 1, 'prec': 4,
                'lolim': -2**3, 'hilim': 2**3-1,
                'unit': 'Global FOFB pre-accumulator gain.'},

            # Correctors
            'CHPosS-Cte': {
                'type': 'float', 'unit': 'm', 'count': self.nr_ch,
                'value': self.ch_pos},
            'CVPosS-Cte': {
                'type': 'float', 'unit': 'm', 'count': self.nr_cv,
                'value': self.cv_pos},
            'CHNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the chs.',
                'count': self.nr_ch, 'value': self.ch_nicknames},
            'CVNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the cvs.',
                'count': self.nr_cv, 'value': self.cv_nicknames},
            'CorrStatus-Mon': {'type': 'int', 'value': 0b111111},
            'CorrStatusLabels-Cte': {
                'type': 'string', 'count': len(_et.STS_LBLS_CORR),
                'value': _et.STS_LBLS_CORR},
            'CorrConfig-Cmd': {'type': 'int', 'value': 0},
            'CorrSetOpModeManual-Cmd': {'type': 'int', 'value': 0},
            'CorrSetAccFreezeDsbl-Cmd': {'type': 'int', 'value': 0},
            'CorrSetAccFreezeEnbl-Cmd': {'type': 'int', 'value': 0},
            'CorrSetAccClear-Cmd': {'type': 'int', 'value': 0},

            # FOFB Controllers
            'FOFBCtrlStatus-Mon': {'type': 'int', 'value': 0b1111111},
            'FOFBCtrlStatusLabels-Cte': {
                'type': 'string', 'count': len(_et.STS_LBLS_FOFBCTRL),
                'value': _et.STS_LBLS_FOFBCTRL},
            'FOFBCtrlSyncNet-Cmd': {'type': 'int', 'value': 0},
            'FOFBCtrlSyncRefOrb-Cmd': {'type': 'int', 'value': 0},
            'FOFBCtrlConfTFrameLen-Cmd': {'type': 'int', 'value': 0},
            'FOFBCtrlConfBPMLogTrg-Cmd': {'type': 'int', 'value': 0},

            # Reference Orbit (same order os SOFB)
            'RefOrbX-SP': {
                'type': 'float', 'unit': 'um', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0]},
            'RefOrbX-RB': {
                'type': 'float', 'unit': 'um', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0]},
            'RefOrbY-SP': {
                'type': 'float', 'unit': 'um', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0]},
            'RefOrbY-RB': {
                'type': 'float', 'unit': 'um', 'count': self.nr_bpms,
                'value': self.nr_bpms*[0]},
            'GetRefOrbFromSlowOrb-Cmd': {'type': 'int', 'value': 0},

            # Response Matrix
            'BPMXEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1], 'unit': 'BPMX used in correction'},
            'BPMXEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1], 'unit': 'BPMX used in correction'},
            'BPMYEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1], 'unit': 'BPMY used in correction'},
            'BPMYEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1], 'unit': 'BPMY used in correction'},
            'CHEnblList-SP': {
                'type': 'int', 'count': self.nr_ch, 'value': self.nr_ch*[1],
                'unit': 'CHs used in correction'},
            'CHEnblList-RB': {
                'type': 'int', 'count': self.nr_ch, 'value': self.nr_ch*[1],
                'unit': 'CHs used in correction'},
            'CVEnblList-SP': {
                'type': 'int', 'count': self.nr_cv, 'value': self.nr_cv*[1],
                'unit': 'CVs used in correction'},
            'CVEnblList-RB': {
                'type': 'int', 'count': self.nr_cv, 'value': self.nr_cv*[1],
                'unit': 'CVs used in correction'},
            'UseRF-Sel': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.UseRF.Enbl,
                'unit': 'If RF is used in inverse matrix calculation'},
            'UseRF-Sts': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.UseRF.Enbl,
                'unit': 'If RF is used in inverse matrix calculation'},
            'MinSingValue-SP': {
                'type': 'float', 'value': self.MIN_SING_VAL, 'prec': 5,
                'lolim': 0, 'hilim': 1e9,
                'unit': 'Maximum value of SV to use'},
            'MinSingValue-RB': {
                'type': 'float', 'value': self.MIN_SING_VAL, 'prec': 5,
                'lolim': 0, 'hilim': 1e9,
                'unit': 'Maximum value of SV to use'},
            'TikhonovRegConst-SP': {
                'type': 'float', 'value': self.TIKHONOV_REG_CONST, 'prec': 5,
                'lolim': 0, 'hilim': 1e9,
                'unit': 'Tikhonov regularization constant'},
            'TikhonovRegConst-RB': {
                'type': 'float', 'value': self.TIKHONOV_REG_CONST, 'prec': 5,
                'lolim': 0, 'hilim': 1e9,
                'unit': 'Tikhonov regularization constant'},
            'SingValuesRaw-Mon': {
                'type': 'float', 'count': self.nr_svals,
                'value': self.nr_svals*[0],
                'unit': 'Singular values of the matrix'},
            'SingValues-Mon': {
                'type': 'float', 'count': self.nr_svals,
                'value': self.nr_svals*[0],
                'unit': 'Singular values of the matrix in use'},
            'NrSingValues-Mon': {
                'type': 'int', 'value': self.nr_svals,
                'lolim': 1, 'hilim': self.nr_svals,
                'unit': 'Number of used SVs'},
            'RespMat-SP': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(BH, BV)(nm) x (CH, CV, RF)(A, Hz)'},
            'RespMat-RB': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(BH, BV)(nm) x (CH, CV, RF)(A, Hz)'},
            'RespMat-Mon': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'InvRespMat-Mon': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(CH, CV, RF)(urad, Hz) x (BH, BV)(um)'},
            'SingValuesHw-Mon': {
                'type': 'float', 'count': self.nr_svals,
                'value': self.nr_svals*[0],
                'unit': 'Singular values of the matrix in hardware units'},
            'RespMatHw-Mon': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(BH, BV)(nm) x (CH, CV, RF)(counts, Hz)'},
            'InvRespMatHw-Mon': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(CH, CV, RF)(counts, Hz) x (BH, BV)(nm)'},
            'InvRespMatNormMode-Sel': {
                'type': 'enum', 'enums': _et.GLOB_INDIV,
                'value': self.GlobIndiv.Global},
            'InvRespMatNormMode-Sts': {
                'type': 'enum', 'enums': _et.GLOB_INDIV,
                'value': self.GlobIndiv.Global},
            'CorrCoeffs-Mon': {
                'type': 'float', 'count': self.corrcoeffs_size,
                'value': self.corrcoeffs_size*[0],
                'unit': '(CH, CV) x (BH, BV)'},
            'CorrGains-Mon': {
                'type': 'float', 'count': self.corrgains_size,
                'value': self.corrgains_size*[0],
                'unit': '(CH, CV)'},

            # Response Matrix Measurement
            'MeasRespMat-Cmd': {
                'type': 'enum', 'enums': _et.MEAS_RMAT_CMD,
                'value': self.MeasRespMatCmd.Start},
            'MeasRespMat-Mon': {
                'type': 'enum', 'enums': _et.MEAS_RMAT_MON,
                'value': self.MeasRespMatMon.Idle},
            'MeasRespMatKickCH-SP': {
                'type': 'float', 'value': 15, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 30},
            'MeasRespMatKickCH-RB': {
                'type': 'float', 'value': 15, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 30},
            'MeasRespMatKickCV-SP': {
                'type': 'float', 'value': 15, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 30},
            'MeasRespMatKickCV-RB': {
                'type': 'float', 'value': 15, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 30},
            'MeasRespMatKickRF-SP': {
                'type': 'float', 'value': 80, 'unit': 'Hz', 'prec': 2,
                'lolim': 1, 'hilim': 1000},
            'MeasRespMatKickRF-RB': {
                'type': 'float', 'value': 80, 'unit': 'Hz', 'prec': 2,
                'lolim': 1, 'hilim': 1000},
            'MeasRespMatWait-SP': {
                'type': 'float', 'value': 1, 'unit': 's', 'prec': 3,
                'lolim': 0.005, 'hilim': 100},
            'MeasRespMatWait-RB': {
                'type': 'float', 'value': 1, 'unit': 's', 'prec': 3,
                'lolim': 0.005, 'hilim': 100},
        }
        pvs_database = _csdev.add_pvslist_cte(pvs_database)
        return pvs_database
