"""Define properties of all Linac PVs."""

from copy import deepcopy as _dcopy
from mathphys import constants as _c
import siriuspy.csdevice.util as _cutil
from siriuspy.optics import constants as _oc
from siriuspy.search import HLTimeSearch as _HLTimeSearch


# --- Enumeration Types ---

class ETypes(_cutil.ETypes):
    """Local enumerate types."""
    pass


_et = ETypes  # syntactic sugar


class Const(_cutil.Const):
    """Constants important for the timing system."""

    # FINE_DELAY = 5e-12  # [s] (five picoseconds)

    # TrigSrcLL = _cutil.Const.register('TrigSrcLL', _et.TRIG_SRC_LL)
    PSConvDict = {
        'LA-CN:H1RCPS-1': 'LI-01:PS-RevLens',
        'LA-CN:H1MLPS-1': 'LI-01:PS-Lens-1',
        'LA-CN:H1MLPS-2': 'LI-01:PS-Lens-2',
        'LA-CN:H1MLPS-3': 'LI-01:PS-Lens-3',
        'LA-CN:H1MLPS-4': 'LI-01:PS-Lens-4',
        'LA-CN:H1SLPS-1': 'LI-01:PS-Slnd-1',
        'LA-CN:H1SLPS-2': 'LI-01:PS-Slnd-2',
        'LA-CN:H1SLPS-3': 'LI-01:PS-Slnd-3',
        'LA-CN:H1SLPS-4': 'LI-01:PS-Slnd-4',
        'LA-CN:H1SLPS-5': 'LI-01:PS-Slnd-5',
        'LA-CN:H1SLPS-6': 'LI-01:PS-Slnd-6',
        'LA-CN:H1SLPS-7': 'LI-01:PS-Slnd-7',
        'LA-CN:H1SLPS-8': 'LI-01:PS-Slnd-8',
        'LA-CN:H1SLPS-9': 'LI-01:PS-Slnd-9',
        'LA-CN:H1SLPS-10': 'LI-01:PS-Slnd-10',
        'LA-CN:H1SLPS-11': 'LI-01:PS-Slnd-11',
        'LA-CN:H1SLPS-12': 'LI-01:PS-Slnd-12',
        'LA-CN:H1SLPS-13': 'LI-01:PS-Slnd-13',
        'LA-CN:H1SLPS-14': 'LI-01:PS-Slnd-14',
        'LA-CN:H1SLPS-15': 'LI-01:PS-Slnd-15',
        'LA-CN:H1SLPS-16': 'LI-01:PS-Slnd-16',
        'LA-CN:H1SLPS-17': 'LI-01:PS-Slnd-17',
        'LA-CN:H1SLPS-18': 'LI-01:PS-Slnd-18',
        'LA-CN:H1SLPS-19': 'LI-01:PS-Slnd-19',
        'LA-CN:H1SLPS-20': 'LI-01:PS-Slnd-20',
        'LA-CN:H1SLPS-21': 'LI-01:PS-Slnd-21',
        'LA-CN:H1SCPS-1': 'LI-01:PS-CH-1',
        'LA-CN:H1SCPS-2': 'LI-01:PS-CH-2',
        'LA-CN:H1SCPS-3': 'LI-01:PS-CV-1',
        'LA-CN:H1SCPS-4': 'LI-01:PS-CV-2',
        'LA-CN:H1LCPS-1': 'LI-01:PS-CH-3',
        'LA-CN:H1LCPS-2': 'LI-01:PS-CH-4',
        'LA-CN:H1LCPS-3': 'LI-01:PS-CH-5',
        'LA-CN:H1LCPS-4': 'LI-01:PS-CH-6',
        'LA-CN:H1LCPS-5': 'LI-01:PS-CH-7',
        'LA-CN:H1LCPS-6': 'LI-01:PS-CV-3',
        'LA-CN:H1LCPS-7': 'LI-01:PS-CV-4',
        'LA-CN:H1LCPS-8': 'LI-01:PS-CV-5',
        'LA-CN:H1LCPS-9': 'LI-01:PS-CV-6',
        'LA-CN:H1LCPS-10': 'LI-01:PS-CV-7',
        'LA-CN:H1FQPS-1': 'LI-01:PS-QF-1',
        'LA-CN:H1FQPS-2': 'LI-01:PS-QF-2',
        'LA-CN:H1FQPS-3': 'LI-01:PS-QF-3',
        'LA-CN:H1DQPS-1': 'LI-01:PS-QD-1',
        'LA-CN:H1DQPS-2': 'LI-01:PS-QD-2',
        'LA-CN:H1DPPS-1': 'LI-01:PS-Spect-1',
    }
    LLRFConvDict = {
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:BUN1:',
        'LA-RF:LLRF:KLY1:',
        'LA-RF:LLRF:KLY2:',
        }

def get_llrf_convpropty(device):
    dic = {
        'SET_STREAM': 'Stream-SP',
        'SET_AMP': 'Amp-SP',
        'SET_PHASE': 'Phase-SP',
        'SET_INTEGRAL_ENABLE': 'Integral-Sel',
        'SET_KP': 'KP-SP',
        'SET_KI': 'KI-SP',
        'SET_EXTERNAL_TRIGGER_ENABLE': 'ExtTrig-Sel',
        'SET_TRIGGER_DELAY': 'DelayTrig-SP',
        'SET_FB_MODE': 'FdBckMode-Sel',
        'SET_FBLOOP_PHASE_CORR': 'FdBckPhase-SP',
        'SET_FBLOOP_AMP_CORR': 'FdBckAmp-SP',
        'SET_VM_ADT': 'VMADT-SP',
        'SET_CH1_DELAY': 'Ch1Delay-SP',
        'SET_CH2_DELAY': 'Ch2Delay-SP',
        'SET_CH3_DELAY': 'Ch3Delay-SP',
        'SET_CH4_DELAY': 'Ch4Delay-SP',
        'SET_CH5_DELAY': 'Ch5Delay-SP',
        'SET_CH6_DELAY': 'Ch6Delay-SP',
        'SET_CH7_DELAY': 'Ch7Delay-SP',
        'SET_CH8_DELAY': 'Ch8Delay-SP',
        'SET_CH9_DELAY': 'Ch9Delay-SP',
        'SET_CH1_PHASE_CORR': 'Ch1Phase-SP',
        'SET_CH2_PHASE_CORR': 'Ch2Phase-SP',
        'SET_CH3_PHASE_CORR': 'Ch3Phase-SP',
        'SET_CH4_PHASE_CORR': 'Ch4Phase-SP',
        'SET_CH5_PHASE_CORR': 'Ch5Phase-SP',
        'SET_CH6_PHASE_CORR': 'Ch6Phase-SP',
        'SET_CH7_PHASE_CORR': 'Ch7Phase-SP',
        'SET_CH8_PHASE_CORR': 'Ch8Phase-SP',
        'SET_CH9_PHASE_CORR': 'Ch9Phase-SP',
        'SET_CH1_ADT': 'Ch1ADT-SP',
        'SET_CH2_ADT': 'Ch2ADT-SP',
        'SET_CH3_ADT': 'Ch3ADT-SP',
        'SET_CH4_ADT': 'Ch4ADT-SP',
        'SET_CH5_ADT': 'Ch5ADT-SP',
        'SET_CH6_ADT': 'Ch6ADT-SP',
        'SET_CH7_ADT': 'Ch7ADT-SP',
        'SET_CH8_ADT': 'Ch8ADT-SP',
        'SET_CH9_ADT': 'Ch9ADT-SP',
        'SET_CH1_ATT': 'Ch1ATT-SP',
        'SET_CH2_ATT': 'Ch2ATT-SP',
        'SET_CH3_ATT': 'Ch3ATT-SP',
        'SET_CH4_ATT': 'Ch4ATT-SP',
        'SET_CH5_ATT': 'Ch5ATT-SP',
        'SET_CH6_ATT': 'Ch6ATT-SP',
        'SET_CH7_ATT': 'Ch7ATT-SP',
        'SET_CH8_ATT': 'Ch8ATT-SP',
        'SET_CH9_ATT': 'Ch9ATT-SP',
    }
    if device.dev.endswith('Kly1'):
        dic['SET_SHIF_MOTOR_ANGLE'] = ''
    elif device.dev.endswith('SHB'):
        chans = tuple(['CH{0:d}'.format(i) for i in [3, 4, 5, 6, 9]])
        dic = {k: v for k, v in dic.items() if not k[4:].startswith(chans)}
        dic = {
            'SET_PID_MODE': '',
            'SET_PID_KP': '',
            'SET_PID_KI': '',
        }
    return dic

def get_otp_database(otp_num=0, prefix=None):
    """Return otp_database."""
    def_prefix = 'OTP{0:02d}'.format(otp_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'State-Sts'] = dic_
    db[prefix+'State-Sel'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 63, 'high': 63, 'hihi': 63}
    db[prefix+'Evt-SP'] = dic_
    db[prefix+'Evt-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix+'Width-SP'] = dic_
    db[prefix+'Width-RB'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.NORM_INV}
    db[prefix+'Polarity-Sts'] = dic_
    db[prefix+'Polarity-Sel'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix+'NrPulses-SP'] = dic_
    db[prefix+'NrPulses-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix+'Delay-SP'] = dic_
    db[prefix+'Delay-RB'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.BYPASS}
    db[prefix+'ByPassIntlk-Sts'] = dic_
    db[prefix+'ByPassIntlk-Sel'] = _dcopy(dic_)

    return db


def get_out_database(out_num=0, equip='EVR', prefix=None):
    """Return out_database."""
    def_prefix = 'OUT{0:d}'.format(out_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.TRIG_SRC_LL}
    db[prefix+'Src-Sts'] = dic_
    db[prefix+'Src-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DLYTYP}
    db[prefix+'RFDelayType-Sts'] = dic_
    db[prefix+'RFDelayType-Sel'] = _dcopy(dic_)

    max_trig = 23 if equip == 'EVR' else 15
    num_trig = out_num + 12 if equip == 'EVR' else out_num
    dic_ = {
        'type': 'int', 'value': num_trig, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': max_trig, 'high': max_trig, 'hihi': max_trig}
    db[prefix+'SrcTrig-SP'] = dic_
    db[prefix+'SrcTrig-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 30, 'high': 30, 'hihi': 30}
    db[prefix+'RFDelay-SP'] = dic_
    db[prefix+'RFDelay-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 200, 'high': 200, 'hihi': 200}
    db[prefix+'FineDelay-SP'] = dic_
    db[prefix+'FineDelay-RB'] = _dcopy(dic_)

    return db


def get_afc_out_database(out_num=0, out_tp='FMC', prefix=None):
    """Return afc_database."""
    def_prefix = (out_tp + '{0:d}'.format(out_num))
    if out_tp == 'FMC':
        fmc = (out_num // 5) + 1
        ch = (out_num % 5) + 1
        def_prefix = (out_tp + '{0:d}CH{1:d}'.format(fmc, ch))

    prefix = def_prefix if prefix is None else prefix
    db = get_otp_database(prefix=prefix)
    db.pop(prefix + 'ByPassIntlk-Sel')
    db.pop(prefix + 'ByPassIntlk-Sts')
    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.TRIG_SRC_LL}
    db[prefix+'Src-Sts'] = dic_
    db[prefix+'Src-Sel'] = _dcopy(dic_)

    return db


def get_evr_database(prefix=None):
    """Return evr_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'Link-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'Intlk-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    for i in range(24):
        db2 = get_otp_database(otp_num=i)
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(8):
        db2 = get_out_database(out_num=i, equip='EVR')
        for k, v in db2.items():
            db[prefix + k] = v
    return db


def get_eve_database(eve_num=1, prefix=None):
    """Return eve_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.RFOUT}
    db[prefix+'RFOut-Sts'] = dic_
    db[prefix+'RFOut-Sel'] = _dcopy(dic_)

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'Link-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'Intlk-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    for i in range(24):
        db2 = get_otp_database(otp_num=i)
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(8):
        db2 = get_out_database(out_num=i, equip='EVE')
        for k, v in db2.items():
            db[prefix + k] = v

    return db


def get_afc_database(prefix=None):
    """Return adc_database."""
    prefix = prefix or ''
    db = dict()
    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'LinkStatus-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'Intlk-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    for i in range(8):
        db2 = get_afc_out_database(out_num=i, out_tp='AMC')
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(10):
        db2 = get_afc_out_database(out_num=i, out_tp='FMC')
        for k, v in db2.items():
            db[prefix + k] = v

    return db


def get_fout_database(prefix=None):
    """Return fout_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'Link-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'Intlk-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}
    return db


def get_event_database(evt_num=0, prefix=None):
    """Return event_database."""
    def_prefix = 'Evt{0:02d}'.format(evt_num)
    prefix = def_prefix if prefix is None else prefix

    db = dict()
    dic_ = {'type': 'int', 'value': 0,
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix + 'Delay-SP'] = _dcopy(dic_)
    db[prefix + 'Delay-RB'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.EVT_MODES, 'value': 1}
    db[prefix + 'Mode-Sel'] = _dcopy(dic_)
    db[prefix + 'Mode-Sts'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.FIXED_INCR, 'value': 1}
    db[prefix + 'DelayType-Sel'] = _dcopy(dic_)
    db[prefix + 'DelayType-Sts'] = dic_
    dic_ = {'type': 'string', 'value': ''}
    db[prefix + 'Desc-SP'] = _dcopy(dic_)
    db[prefix + 'Desc-RB'] = dic_
    db[prefix + 'ExtTrig-Cmd'] = {'type': 'int', 'value': 0}
    return db


def get_clock_database(clock_num=0, prefix=None):
    """Return clock_database."""
    def_prefix = 'Clk{0:d}'.format(clock_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'int', 'value': 124948114,
            'lolo': 2, 'low': 2, 'lolim': 2,
            'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix + 'MuxDiv-SP'] = _dcopy(dic_)
    db[prefix + 'MuxDiv-RB'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    db[prefix + 'MuxEnbl-Sel'] = _dcopy(dic_)
    db[prefix + 'MuxEnbl-Sts'] = dic_
    return db


def get_evg_database(prefix=None, only_evg=False):
    """Return evg_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    db[prefix + 'ContinuousEvt-Sel'] = _dcopy(dic_)
    db[prefix + 'ContinuousEvt-Sts'] = dic_

    dic_ = {'type': 'int', 'count': 864, 'value': 864*[1],
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 864, 'high': 864, 'hihi': 864
            }
    db[prefix + 'BucketList-SP'] = _dcopy(dic_)
    db[prefix + 'BucketList-RB'] = dic_
    db[prefix + 'BucketListLen-Mon'] = {
        'type': 'int', 'value': 864,
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 864, 'high': 864, 'hihi': 864}

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    db[prefix + 'InjectionEvt-Sel'] = _dcopy(dic_)
    db[prefix + 'InjectionEvt-Sts'] = dic_

    dic_ = {'type': 'int', 'value': 0,
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 100, 'high': 100, 'hihi': 100}
    db[prefix + 'RepeatBucketList-SP'] = _dcopy(dic_)
    db[prefix + 'RepeatBucketList-RB'] = dic_

    dic_ = {'type': 'int', 'value': 30,
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 60, 'high': 60, 'hihi': 60}
    db[prefix + 'ACDiv-SP'] = _dcopy(dic_)
    db[prefix + 'ACDiv-RB'] = dic_

    dic_ = {'type': 'int', 'value': 4,
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix + 'RFDiv-SP'] = _dcopy(dic_)
    db[prefix + 'RFDiv-RB'] = dic_

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'RFStatus-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': ('Loss or Out of Range', 'Normal')}

    db[prefix+'StateMachine-Mon'] = {
            'type': 'enum', 'value': 4,
            'enums': (
                'Initializing', 'Stopped', 'Continuous', 'Injection',
                'Preparing Continuous', 'Preparing Injection'
                )}

    if only_evg:
        return db

    for clc in Const.ClkLL2HLMap:
        db.update(get_clock_database(prefix=prefix+clc))
    for ev in Const.EvtLL._fields:
        db.update(get_event_database(prefix=prefix+ev))
    return db


def get_hl_clock_database(prefix='Clock0'):
    """Return database of a high level Clock."""
    db = dict()

    dic_ = {
        'type': 'float', 'value': 1.0,
        'unit': 'kHz', 'prec': 6,
        'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
        'hilim': 125000000, 'high': 125000000, 'hihi': 125000000}
    db[prefix + 'Freq-RB'] = _dcopy(dic_)
    db[prefix + 'Freq-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    db[prefix + 'State-Sel'] = _dcopy(dic_)
    db[prefix + 'State-Sts'] = dic_
    return db


def get_hl_event_database(prefix='Linac'):
    """Return database of a high level event."""
    db = dict()

    dic_ = {'type': 'float', 'unit': 'us', 'prec': 4, 'value': 0,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    db[prefix + 'Delay-RB'] = _dcopy(dic_)
    db[prefix + 'Delay-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.EVT_MODES,
            'value': 1,
            'states': ()}
    db[prefix + 'Mode-Sts'] = _dcopy(dic_)
    db[prefix + 'Mode-Sel'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.FIXED_INCR, 'value': 1}
    db[prefix + 'DelayType-Sts'] = _dcopy(dic_)
    db[prefix + 'DelayType-Sel'] = dic_

    db[prefix + 'ExtTrig-Cmd'] = {
        'type': 'int', 'value': 0,
        'unit': 'When in External Mode generates Event.'}
    return db


def get_hl_evg_database(prefix=None, only_evg=False):
    """Return database of the high level PVs associated with the EVG."""
    def_prefix = 'AS-Glob:TI-EVG:'
    pre = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'float', 'value': 2.0,
            'unit': 'Hz', 'prec': 6,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 60, 'high': 60, 'hihi': 60}
    db[pre + 'RepRate-RB'] = _dcopy(dic_)
    db[pre + 'RepRate-SP'] = dic_

    if only_evg:
        return db

    for ev in Const.EvtHL2LLMap.keys():
        db.update(get_hl_event_database(prefix=prefix+ev))
    for clc in Const.ClkHL2LLMap.keys():
        db.update(get_hl_clock_database(prefix=prefix+clc))
    return db


def get_hl_trigger_database(hl_trigger, prefix=''):
    """Return database of the specified hl_trigger."""
    db = dict()
    trig_db = _HLTimeSearch.get_hl_trigger_predef_db(hl_trigger)

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL}
    dic_.update(trig_db['State'])
    db['State-Sts'] = _dcopy(dic_)
    db['State-Sel'] = dic_

    dic_ = {'type': 'enum'}
    dic_.update(trig_db['Src'])
    if _HLTimeSearch.has_clock(hl_trigger):
        clocks = tuple(sorted(Const.ClkHL2LLMap))
        dic_['enums'] += clocks
    dic_['enums'] += ('Invalid', )  # for completeness
    db['Src-Sts'] = _dcopy(dic_)
    db['Src-Sel'] = dic_

    dic_ = {'type': 'float', 'unit': 'us', 'prec': 3,
            'lolo': 0.008, 'low': 0.008, 'lolim': 0.008,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    dic_.update(trig_db['Duration'])
    db['Duration-RB'] = _dcopy(dic_)
    db['Duration-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.NORM_INV}
    dic_.update(trig_db['Polarity'])
    db['Polarity-Sts'] = _dcopy(dic_)
    db['Polarity-Sel'] = dic_

    dic_ = {'type': 'int', 'unit': 'numer of pulses',
            # 'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 2001, 'high': 10000, 'hihi': 100000}
    dic_.update(trig_db['NrPulses'])
    db['NrPulses-RB'] = _dcopy(dic_)
    db['NrPulses-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.BYPASS}
    dic_.update(trig_db['ByPassIntlk'])
    db['ByPassIntlk-Sts'] = _dcopy(dic_)
    db['ByPassIntlk-Sel'] = dic_
    if not _HLTimeSearch.has_bypass_interlock(hl_trigger):
        db.pop('ByPassIntlk-Sts')
        db.pop('ByPassIntlk-Sel')

    dic_ = {'type': 'float', 'unit': 'us', 'prec': 6,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    dic_.update(trig_db['Delay'])
    db['Delay-RB'] = _dcopy(dic_)
    db['Delay-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.DLYTYP}
    dic_.update(trig_db['RFDelayType'])
    db['RFDelayType-Sts'] = _dcopy(dic_)
    db['RFDelayType-Sel'] = dic_
    if not _HLTimeSearch.has_delay_type(hl_trigger):
        db.pop('RFDelayType-Sts')
        db.pop('RFDelayType-Sel')

    dic_ = {'type': 'int', 'value': 0b1111111111}
    db['Status-Mon'] = _dcopy(dic_)

    db['StatusLabels-Cte'] = {
        'type': 'char', 'count': 1000,
        'value': '\n'.join(Const.HLTrigStatusLabels)
        }
    ll_trigs = '\n'.join(_HLTimeSearch.get_ll_trigger_names(hl_trigger))
    db['LowLvlTriggers-Cte'] = {
        'type': 'char', 'count': 5000, 'value': ll_trigs}
    channels = '\n'.join(_HLTimeSearch.get_hl_trigger_channels(hl_trigger))
    db['CtrldChannels-Cte'] = {
        'type': 'char', 'count': 5000, 'value': channels}

    return {prefix + pv: dt for pv, dt in db.items()}
