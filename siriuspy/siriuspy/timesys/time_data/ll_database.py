"""Define properties of all timing devices and their connections."""

from copy import deepcopy as _dcopy
from .hl_types_data import Triggers


class TimingDevDb:

    @staticmethod
    def get_otp_database(otp_num=0):
        prefix = 'OTP{0:02d}'.format(otp_num)
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': Triggers.STATES}
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

        dic_ = {'type': 'enum', 'value': 0, 'enums': Triggers.POLARITIES}
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
    def get_out_database(out_num=0, equip='EVR'):
        prefix = 'OUT{0:d}'.format(out_num)
        db = dict()

        dic_ = {'type': 'enum', 'value': 0, 'enums': Triggers.INTLK}
        db[prefix+'Intlk-Sts'] = dic_
        db[prefix+'Intlk-Sel'] = _dcopy(dic_)

        dic_ = {'type': 'enum', 'value': 0, 'enums': Triggers.SRC_LL}
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
    def get_afc_out_database(out_num=0, out_tp='FMC'):
        prefix = out_tp + '{0:d}'.format(out_num)
        if out_tp == 'FMC':
            fmc = (out_num // 5) + 1
            ch = (out_num % 5) + 1
            prefix = out_tp + '{0:d}CH{1:d}'.format(fmc, ch)

        db = TimingDevDb.get_otp_database(otp_num=out_num)
        db2 = dict()
        for k, v in db.items():
            k2 = prefix + k[5:]
            db2[k2] = v

        dic_ = {'type': 'enum', 'value': 0, 'enums': Triggers.SRC_LL}
        db2[prefix+'Src-Sts'] = dic_
        db2[prefix+'Src-Sel'] = _dcopy(dic_)

        return db2

    @staticmethod
    def get_evr_database(evr_num=1):
        prefix = 'AS-Glob:TI-EVR-{1:d}:'.format(evr_num)
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
                'type': 'enum', 'value': 0,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        for i in range(24):
            db2 = TimingDevDb.get_otp_database(otp_num=i)
            for k, v in db2:
                db[prefix + k] = v

        for i in range(8):
            db2 = TimingDevDb.get_out_database(out_num=i, equip='EVR')
            for k, v in db2:
                db[prefix + k] = v

        return db

    @staticmethod
    def get_eve_database(eve_num=1):
        prefix = 'AS-Glob:TI-EVE-{1:d}:'.format(eve_num)
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
                'type': 'enum', 'value': 0,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        for i in range(16):
            db2 = TimingDevDb.get_otp_database(otp_num=i)
            for k, v in db2:
                db[prefix + k] = v

        for i in range(8):
            db2 = TimingDevDb.get_out_database(out_num=i, equip='EVE')
            for k, v in db2:
                db[prefix + k] = v

        return db

    @staticmethod
    def get_afc_database(afc_sec=1, has_idx=False, idx=1):
        prefix = 'AS-{0:02d}:TI-AFC:'.format(afc_sec)
        if has_idx:
            prefix = 'AS-{0:02d}:TI-AFC-{1:d}:'.format(afc_sec, idx)
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
                'type': 'enum', 'value': 0,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        for i in range(8):
            db2 = TimingDevDb.get_afc_out_database(out_num=i, out_tp='CRT')
            for k, v in db2:
                db[prefix + k] = v

        for i in range(10):
            db2 = TimingDevDb.get_afc_out_database(out_num=i, out_tp='FMC')
            for k, v in db2:
                db[prefix + k] = v

        return db

    @staticmethod
    def get_fout_database(evr_num=1):
        prefix = 'AS-Glob:TI-FOUT-{1:d}:'.format(evr_num)
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
                'type': 'enum', 'value': 0,
                'enums': ('Disconnected', 'Connected')}

        db[prefix+'Link-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Unlink', 'Link')}

        db[prefix+'Intlk-Mon'] = {
                'type': 'enum', 'value': 0,
                'enums': ('Dsbl', 'Enbl')}

        return db
