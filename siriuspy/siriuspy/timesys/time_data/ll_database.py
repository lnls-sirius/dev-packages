"""Define properties of all timing devices and their connections."""

from copy import deepcopy as _dcopy
from .hl_types_data import Triggers as _Triggers
from .hl_types_data import Events as _Events
from .hl_types_data import Clocks as _Clocks


class TimingDevDb:
    """TimingDevDb class."""

    @staticmethod
    def get_otp_database(otp_num=0, prefix=None):
        """Metod get_otp_database."""
        def_prefix = 'OTP{0:02d}'.format(otp_num)
        prefix = prefix if prefix is not None else def_prefix
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': _Triggers.STATES}
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
            'hilim': 2**32, 'high': 2**32, 'hihi': 2**32}
        db[prefix+'Width-SP'] = dic_
        db[prefix+'Width-RB'] = _dcopy(dic_)

        dic_ = {'type': 'enum', 'value': 0, 'enums': _Triggers.POLARITIES}
        db[prefix+'Polarity-Sts'] = dic_
        db[prefix+'Polarity-Sel'] = _dcopy(dic_)

        dic_ = {
            'type': 'int', 'value': 1, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**16-1, 'high': 2**16-1, 'hihi': 2**16-1}
        db[prefix+'Pulses-SP'] = dic_
        db[prefix+'Pulses-RB'] = _dcopy(dic_)

        dic_ = {
            'type': 'int', 'value': 1, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**32-1, 'high': 2**32-1, 'hihi': 2**32-1}
        db[prefix+'Delay-SP'] = dic_
        db[prefix+'Delay-RB'] = _dcopy(dic_)

        return db

    @staticmethod
    def get_out_database(out_num=0, equip='EVR', prefix=None):
        """Method get_out_database."""
        def_prefix = 'OUT{0:d}'.format(out_num)
        prefix = prefix if prefix is not None else def_prefix
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': _Triggers.INTLK}
        db[prefix+'Intlk-Sts'] = dic_
        db[prefix+'Intlk-Sel'] = _dcopy(dic_)

        dic_ = {'type': 'enum', 'value': 0, 'enums': _Triggers.SRC_LL}
        db[prefix+'Src-Sts'] = dic_
        db[prefix+'Src-Sel'] = _dcopy(dic_)

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
            'hilim': 31, 'high': 31, 'hihi': 31}
        db[prefix+'RFDelay-SP'] = dic_
        db[prefix+'RFDelay-RB'] = _dcopy(dic_)

        dic_ = {
            'type': 'int', 'value': 1, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 200, 'high': 200, 'hihi': 200}
        db[prefix+'FineDelay-SP'] = dic_
        db[prefix+'FineDelay-RB'] = _dcopy(dic_)

        return db

    @staticmethod
    def get_afc_out_database(out_num=0, out_tp='FMC', prefix=None):
        """Method get_afc_database."""
        def_prefix = (out_tp + '{0:d}'.format(out_num))
        if out_tp == 'FMC':
            fmc = (out_num // 5) + 1
            ch = (out_num % 5) + 1
            def_prefix = (out_tp + '{0:d}CH{1:d}'.format(fmc, ch))

        prefix = prefix if prefix is not None else def_prefix
        db = TimingDevDb.get_otp_database(prefix=prefix)
        dic_ = {'type': 'enum', 'value': 0, 'enums': _Triggers.SRC_LL}
        db[prefix+'Src-Sts'] = dic_
        db[prefix+'Src-Sel'] = _dcopy(dic_)

        return db

    @staticmethod
    def get_evr_database(evr_num=1, prefix=None):
        """Method get_evr_database."""
        def_prefix = 'AS-Glob:TI-EVR-{0:d}:'.format(evr_num)
        prefix = prefix if prefix is not None else def_prefix
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': ('Dsbl', 'Enbl')}
        db[prefix+'DevEnbl-Sts'] = dic_
        db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

        db[prefix+'Los-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 255, 'high': 255, 'hihi': 255}

        db[prefix+'Alive-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**32-1, 'high': 2**32-1, 'hihi': 2**32-1}

        db[prefix+'Network-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        for i in range(24):
            db2 = TimingDevDb.get_otp_database(otp_num=i)
            for k, v in db2.items():
                db[prefix + k] = v

        for i in range(8):
            db2 = TimingDevDb.get_out_database(out_num=i, equip='EVR')
            for k, v in db2.items():
                db[prefix + k] = v

        return db

    @staticmethod
    def get_eve_database(eve_num=1, prefix=None):
        """Method get_eve_database."""
        def_prefix = 'AS-Glob:TI-EVE-{0:d}:'.format(eve_num)
        prefix = prefix if prefix is not None else def_prefix
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': ('Dsbl', 'Enbl')}
        db[prefix+'DevEnbl-Sts'] = dic_
        db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

        RFOUT = ('OFF', '5RF/2', '5RF/4', 'RF', 'RF/2', 'RF/4')
        dic_ = {'type': 'enum', 'value': 0, 'enums': RFOUT}
        db[prefix+'RFOut-Sts'] = dic_
        db[prefix+'RFOut-Sel'] = _dcopy(dic_)

        db[prefix+'Alive-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**32-1, 'high': 2**32-1, 'hihi': 2**32-1}

        db[prefix+'Network-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        for i in range(16):
            db2 = TimingDevDb.get_otp_database(otp_num=i)
            for k, v in db2.items():
                db[prefix + k] = v

        for i in range(8):
            db2 = TimingDevDb.get_out_database(out_num=i, equip='EVE')
            for k, v in db2.items():
                db[prefix + k] = v

        return db

    @staticmethod
    def get_afc_database(afc_sec=1, has_idx=False, idx=1, prefix=None):
        """Method get_adc_database."""
        def_prefix = 'AS-{0:02d}:TI-AFC:'.format(afc_sec)
        if has_idx:
            def_prefix = 'AS-{0:02d}:TI-AFC-{1:d}:'.format(afc_sec, idx)

        prefix = prefix if prefix is not None else def_prefix
        db = dict()
        dic_ = {'type': 'enum', 'value': 0, 'enums': ('Dsbl', 'Enbl')}
        db[prefix+'DevEnbl-Sts'] = dic_
        db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

        db[prefix+'Los-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 255, 'high': 255, 'hihi': 255}

        db[prefix+'Alive-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**32-1, 'high': 2**32-1, 'hihi': 2**32-1}

        db[prefix+'Network-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        for i in range(8):
            db2 = TimingDevDb.get_afc_out_database(out_num=i, out_tp='CRT')
            for k, v in db2.items():
                db[prefix + k] = v

        for i in range(10):
            db2 = TimingDevDb.get_afc_out_database(out_num=i, out_tp='FMC')
            for k, v in db2.items():
                db[prefix + k] = v

        return db

    @staticmethod
    def get_fout_database(fout_num=1, prefix=None):
        """Method get_fout_database."""
        def_prefix = 'AS-Glob:TI-FOUT-{0:d}:'.format(fout_num)
        prefix = prefix if prefix is not None else def_prefix
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': ('Dsbl', 'Enbl')}
        db[prefix+'DevEnbl-Sts'] = dic_
        db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

        db[prefix+'Los-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 255, 'high': 255, 'hihi': 255}

        db[prefix+'Alive-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**32-1, 'high': 2**32-1, 'hihi': 2**32-1}

        db[prefix+'Network-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        return db

    @staticmethod
    def get_event_database(evt_num=0, prefix=None):
        """Method get_event_database."""
        def_prefix = 'Evt{0:02d}'.format(evt_num)
        prefix = prefix if prefix is not None else def_prefix

        db = dict()
        dic_ = {'type': 'int', 'value': 0,
                'lolo': 0, 'low': 0, 'lolim': 0,
                'hilim': 2**32-1, 'high': 2**32-1, 'hihi': 2**32-1}
        db[prefix + 'Delay-SP'] = _dcopy(dic_)
        db[prefix + 'Delay-RB'] = dic_
        dic_ = {'type': 'enum', 'enums': _Events.MODES, 'value': 1}
        db[prefix + 'Mode-Sel'] = _dcopy(dic_)
        db[prefix + 'Mode-Sts'] = dic_
        dic_ = {'type': 'enum', 'enums': _Events.DELAY_TYPES, 'value': 1}
        db[prefix + 'DelayType-Sel'] = _dcopy(dic_)
        db[prefix + 'DelayType-Sts'] = dic_
        dic_ = {'type': 'string', 'value': ''}
        db[prefix + 'Desc-SP'] = _dcopy(dic_)
        db[prefix + 'Desc-RB'] = dic_
        db[prefix + 'ExtTrig-Cmd'] = {'type': 'int', 'value': 0}
        return db

    @staticmethod
    def get_clock_database(clock_num=0, prefix=None):
        """Method get_clock_database."""
        def_prefix = 'Clock{0:d}'.format(clock_num)
        prefix = prefix if prefix is not None else def_prefix
        db = dict()

        dic_ = {'type': 'int', 'value': 124948114,
                'lolo': 2, 'low': 2, 'lolim': 2,
                'hilim': 2**32, 'high': 2**32, 'hihi': 2**32}
        db[prefix + 'MuxDiv-SP'] = _dcopy(dic_)
        db[prefix + 'MuxDiv-RB'] = dic_
        dic_ = {'type': 'enum', 'enums': _Clocks.STATES, 'value': 0}
        db[prefix + 'MuxEnbl-Sel'] = _dcopy(dic_)
        db[prefix + 'MuxEnbl-Sts'] = dic_
        return db

    @staticmethod
    def get_evg_database(prefix=None):
        """Method get_evg_database."""
        def_prefix = 'AS-Glob:TI-EVG:'
        prefix = prefix if prefix is not None else def_prefix
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': ('Dsbl', 'Enbl')}
        db[prefix+'DevEnbl-Sts'] = dic_
        db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

        dic_ = {'type': 'enum', 'enums': ('Dsbl', 'Enbl'), 'value': 0}
        db[prefix + 'ContinuousEvt-Sel'] = _dcopy(dic_)
        db[prefix + 'ContinuousEvt-Sts'] = dic_

        dic_ = {'type': 'int', 'count': 864, 'value': 864*[1],
                # 'lolo': 0, 'low': 0, 'lolim': 0,
                # 'hilim': 864, 'high': 864, 'hihi': 864
                }
        db[prefix + 'BucketList-SP'] = _dcopy(dic_)
        db[prefix + 'BucketList-RB'] = dic_
        db[prefix + 'BucketListLen-Mon'] = {
            'type': 'int', 'value': 864,
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 864, 'high': 864, 'hihi': 864}

        dic_ = {'type': 'enum', 'enums': ('Dsbl', 'Enbl'), 'value': 0}
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
                'hilim': 2**32, 'high': 2**32, 'hihi': 2**32}
        db[prefix + 'RFDiv-SP'] = _dcopy(dic_)
        db[prefix + 'RFDiv-RB'] = dic_

        db[prefix+'Los-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 255, 'high': 255, 'hihi': 255}

        db[prefix+'Alive-Mon'] = {
            'type': 'int', 'value': 0, 'unit': '',
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**32-1, 'high': 2**32-1, 'hihi': 2**32-1}

        db[prefix+'Network-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 1,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        for clc in _Clocks.LL2HL_MAP.keys():
            p = prefix + clc
            db.update(TimingDevDb.get_clock_database(prefix=p))
        for ev in _Events.LL_EVENTS:
            p = prefix + ev
            db.update(TimingDevDb.get_event_database(prefix=p))
        return db
