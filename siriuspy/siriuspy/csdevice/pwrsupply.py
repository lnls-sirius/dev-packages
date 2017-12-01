"""Power Supply Control System Devices."""

import copy as _copy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch
from siriuspy.csdevice import ps_properties as _ps_props

default_wfmsize = 4000
default_wfmlabels = _et.enums('PSWfmLabelsTyp')
default_intlklabels = _et.enums('PSIntlkLabelsTyp')
default_ps_current_precision = 4
default_ps_current_unit = _PSSearch.get_splims_unit(ispulsed=False)
default_pu_current_unit = _PSSearch.get_splims_unit(ispulsed=True)


def get_common_propty_database():
    """Return database entries to all power-supply-like devices."""
    db = {
        'CtrlMode-Mon':     {'type': 'enum', 'enums': _et.enums('RmtLocTyp'),
                             'value': _et.idx.Remote},
        'PwrState-Sel':     {'type': 'enum', 'enums': _et.enums('OffOnTyp'),
                             'value': _et.idx.Off},
        'PwrState-Sts':     {'type': 'enum', 'enums': _et.enums('OffOnTyp'),
                             'value': _et.idx.Off},
        'Intlk-Mon':        {'type': 'int',    'value': 0},
        'IntlkLabels-Cte':  {'type': 'string',
                             'count': len(default_intlklabels),
                             'value': default_intlklabels},
    }
    return db


def get_common_ps_propty_database():
    """Return database of commun to all pwrsupply PVs."""
    db = get_common_propty_database()
    db_ps = {
        'OpMode-Sel': {'type': 'enum', 'enums': _et.enums('PSOpModeTyp'),
                       'value': _et.idx.SlowRef},
        'OpMode-Sts': {'type': 'enum', 'enums': _et.enums('PSOpModeTyp'),
                       'value': _et.idx.SlowRef},
        'Reset-Cmd': {'type': 'int', 'value': 0},
        'Abort-Cmd': {'type': 'int', 'value': 0},
        'WfmIndex-Mon': {'type': 'int', 'value': 0},
        'WfmLabels-Mon': {'type': 'string', 'count': len(default_wfmlabels),
                          'value': default_wfmlabels},
        'WfmLabel-SP': {'type': 'string', 'value': default_wfmlabels[0]},
        'WfmLabel-RB': {'type': 'string', 'value': default_wfmlabels[0]},
        'WfmLoad-Sel': {'type': 'enum', 'enums': default_wfmlabels,
                        'value': 0},
        'WfmLoad-Sts': {'type': 'enum', 'enums': default_wfmlabels,
                        'value': 0},
        'WfmData-SP': {'type': 'float', 'count': default_wfmsize,
                       'prec': default_ps_current_precision,
                       'value': [0.0 for datum in range(default_wfmsize)]},
        'WfmData-RB': {'type': 'float', 'count': default_wfmsize,
                       'prec': default_ps_current_precision,
                       'value': [0.0 for datum in range(default_wfmsize)]},
        'WfmSave-Cmd': {'type': 'int', 'value': 0},
        'Current-SP': {'type': 'float', 'value': 0.0,
                       'prec': default_ps_current_precision},
        'Current-RB': {'type': 'float', 'value': 0.0,
                       'prec': default_ps_current_precision},
        'CurrentRef-Mon': {'type': 'float', 'value': 0.0,
                           'prec': default_ps_current_precision},
        'Current-Mon': {'type': 'float',  'value': 0.0,
                        'prec': default_ps_current_precision},
    }
    db.update(db_ps)
    return db


def get_ps_propty_database(pstype):
    """Return property database of a LNLS power supply type device."""
    propty_db = get_common_ps_propty_database()
    current_alarm = ('Current-SP', 'Current-RB',
                     'CurrentRef-Mon', 'Current-Mon', )
    current_pvs = current_alarm + ('WfmData-SP', 'WfmData-RB')
    for propty, db in propty_db.items():
        # set setpoint limits in database
        if propty in current_alarm:
            db['lolo'] = _PSSearch.get_splims(pstype, 'lolo')
            db['low'] = _PSSearch.get_splims(pstype, 'low')
            db['lolim'] = _PSSearch.get_splims(pstype, 'lolim')
            db['hilim'] = _PSSearch.get_splims(pstype, 'hilim')
            db['high'] = _PSSearch.get_splims(pstype, 'high')
            db['hihi'] = _PSSearch.get_splims(pstype, 'hihi')
        # define unit of current
        if propty in current_pvs:
            db['unit'] = default_ps_current_unit

    return propty_db


def get_pu_propty_database(pstype):
    """Return database definition for a pulsed power supply."""
    units = _PSSearch.get_splims_unit()[1]
    precision = 4

    db = {
        # Digital signals
        _ps_props.PwrStateSel: {"type": "enum",
                                "enums": _et.enums("OffOnTyp"),
                                "value": _et.idx.Off},
        _ps_props.PwrStateSts: {"type": "enum",
                                "enums": _et.enums("OffOnTyp"),
                                "value": _et.idx.Off},
        _ps_props.EnablePulsesSel: {"type": "enum",
                                    "enums": _et.enums("DsblEnblTyp"),
                                    "value": _et.idx.Dsbl},
        _ps_props.EnablePulsesSts: {"type": "enum",
                                    "enums": _et.enums("DsblEnblTyp"),
                                    "value": _et.idx.Dsbl},
        _ps_props.ResetCmd: {"type": "int", "value": 0},

        # Waveform

        # Read only digital signals
        _ps_props.CtrlMode: {"type": "enum",
                             "enums": _et.enums('RmtLocTyp'),
                             "value": _et.idx.Remote},
        _ps_props.ExternalInterlock: {"type": "int", "value": 0},

        # Analog signals
        _ps_props.TensionSP: {"type": "float", "unit": units[0],
                              "value": 0.0, "prec": precision},
        _ps_props.TensionRB: {"type": "float", "unit": units[0],
                              "value": 0.0, "prec": precision},
        _ps_props.TensionRefMon: {"type": "float", "unit": units[0],
                                  "value": 0.0, "prec": precision},
        _ps_props.TensionMon: {"type": "float", "unit": units[0],
                               "value": 0.0, "prec": precision}
    }
    # Get tension limits
    analog_signals = [_ps_props.TensionSP, _ps_props.TensionRB,
                      _ps_props.TensionRefMon, _ps_props.TensionMon]

    for signal in analog_signals:
        db[signal]["lolo"] = _PSSearch.get_splim(pstype, "lolo")
        db[signal]["low"] = _PSSearch.get_splim(pstype, "low")
        db[signal]["lolim"] = _PSSearch.get_splim(pstype, "lolim")
        db[signal]["hihi"] = _PSSearch.get_splim(pstype, "hihi")
        db[signal]["high"] = _PSSearch.get_splim(pstype, "high")
        db[signal]["hilim"] = _PSSearch.get_splim(pstype, "hilim")

    return db


def get_ma_propty_database(maname):
    """Return property database of a magnet type device."""
    propty_db = get_common_ps_propty_database()
    units = _MASearch.get_splims_unit()
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    db = {}
    for psname, magfunc in magfunc_dict.items():
        # psnames = _MASearch.conv_maname_2_psnames(maname)
        db[psname] = _copy.deepcopy(propty_db)
        # for propty,pdb in propty_db.items():
        #     # set setpoint limits in database
        #     if propty in ('Current-SP',):
        #         label='lolo';  pdb[label] = _MASearch.get_splim(maname,label)
        #         label='low';   pdb[label] = _MASearch.get_splim(maname,label)
        #         label='lolim'; pdb[label] = _MASearch.get_splim(maname,label)
        #         label='hilim'; pdb[label] = _MASearch.get_splim(maname,label)
        #         label='high';  pdb[label] = _MASearch.get_splim(maname,label)
        #         label='hihi';  pdb[label] = _MASearch.get_splim(maname,label)
        #     # define unit of current
        #     if propty in \
        #           ('Current-SP', 'Current-RB', 'CurrentRef-Mon',
        #            'Current-Mon'):
        #         #db[psname]['unit'] = units[0]
        #         pdb['unit'] = units[0]
        db[psname]["Current-SP"]['lolo'] = _MASearch.get_splim(maname, 'lolo')
        db[psname]["Current-SP"]['low'] = _MASearch.get_splim(maname, 'low')
        db[psname]["Current-SP"]['lolim'] = \
            _MASearch.get_splim(maname, 'lolim')
        db[psname]["Current-SP"]['hilim'] = \
            _MASearch.get_splim(maname, 'hilim')
        db[psname]["Current-SP"]['high'] = _MASearch.get_splim(maname, 'high')
        db[psname]["Current-SP"]['hihi'] = _MASearch.get_splim(maname, 'hihi')
        db[psname]["Current-SP"]['unit'] = units[0]
        db[psname]["Current-RB"]['unit'] = units[0]
        db[psname]["CurrentRef-Mon"]['unit'] = units[0]
        db[psname]["Current-Mon"]['unit'] = units[0]
        # db[psname]["Current-SP"]['prec'] = 6
        # db[psname]["Current-RB"]['prec'] = 6
        # db[psname]["CurrentRef-Mon"]['prec'] = 6
        # db[psname]["Current-Mon"]['prec'] = 6
        if magfunc in ('quadrupole', 'quadrupole-skew'):
            db[psname]['KL-SP'] = _copy.deepcopy(db[psname]['Current-SP'])
            db[psname]['KL-SP']['unit'] = '1/m'
            db[psname]['KL-RB'] = _copy.deepcopy(db[psname]['Current-RB'])
            db[psname]['KL-RB']['unit'] = '1/m'
            db[psname]['KLRef-Mon'] = \
                _copy.deepcopy(db[psname]['CurrentRef-Mon'])
            db[psname]['KLRef-Mon']['unit'] = '1/m'
            db[psname]['KL-Mon'] = _copy.deepcopy(db[psname]['Current-Mon'])
            db[psname]['KL-Mon']['unit'] = '1/m'
        elif magfunc == 'sextupole':
            db[psname]['SL-SP'] = _copy.deepcopy(db[psname]['Current-SP'])
            db[psname]['SL-SP']['unit'] = '1/m^2'
            db[psname]['SL-RB'] = _copy.deepcopy(db[psname]['Current-RB'])
            db[psname]['SL-RB']['unit'] = '1/m^2'
            db[psname]['SLRef-Mon'] = \
                _copy.deepcopy(db[psname]['CurrentRef-Mon'])
            db[psname]['SLRef-Mon']['unit'] = '1/m^2'
            db[psname]['SL-Mon'] = _copy.deepcopy(db[psname]['Current-Mon'])
            db[psname]['SL-Mon']['unit'] = '1/m^2'
        elif magfunc == 'dipole':
            db[psname]['Energy-SP'] = _copy.deepcopy(db[psname]['Current-SP'])
            db[psname]['Energy-SP']['unit'] = 'GeV'
            db[psname]['Energy-RB'] = _copy.deepcopy(db[psname]['Current-RB'])
            db[psname]['Energy-RB']['unit'] = 'GeV'
            db[psname]['EnergyRef-Mon'] = \
                _copy.deepcopy(db[psname]['CurrentRef-Mon'])
            db[psname]['EnergyRef-Mon']['unit'] = 'GeV'
            db[psname]['Energy-Mon'] = \
                _copy.deepcopy(db[psname]['Current-Mon'])
            db[psname]['Energy-Mon']['unit'] = 'GeV'
            # db[psname]['Energy-SP']['prec'] = 6
        elif magfunc in ('corrector-vertical', 'corrector-horizontal'):
            db[psname]['Kick-SP'] = _copy.deepcopy(db[psname]['Current-SP'])
            # db[psname]['Kick-SP']['prec'] = 6
            db[psname]['Kick-SP']['unit'] = 'rad'
            db[psname]['Kick-RB'] = _copy.deepcopy(db[psname]['Current-RB'])
            db[psname]['Kick-RB']['unit'] = 'rad'
            db[psname]['KickRef-Mon'] = \
                _copy.deepcopy(db[psname]['CurrentRef-Mon'])
            db[psname]['KickRef-Mon']['unit'] = 'rad'
            db[psname]['Kick-Mon'] = _copy.deepcopy(db[psname]['Current-Mon'])
            db[psname]['Kick-Mon']['unit'] = 'rad'
    return db


def get_pm_propty_database(maname, psdata):
    """Return database for a pulsed magnet."""
    precision = 6

    db = {}
    for psname, data in psdata.items():
        db[psname] = data.propty_database

        db[psname][_ps_props.StrengthSP] = \
            {"type": "float", "unit": "mrad", "value": 0.0, "prec": precision}
        db[psname][_ps_props.StrengthRB] = \
            {"type": "float", "unit": "mrad", "value": 0.0, "prec": precision}
        db[psname][_ps_props.StrengthRefMon] = \
            {"type": "float", "unit": "mrad", "value": 0.0, "prec": precision}
        db[psname][_ps_props.StrengthMon] = \
            {"type": "float", "unit": "mrad", "value": 0.0, "prec": precision}

        strength_list = [_ps_props.StrengthSP, _ps_props.StrengthRB,
                         _ps_props.StrengthRefMon, _ps_props.StrengthMon]

        for strength in strength_list:
            db[psname][strength]["lolo"] = _MASearch.get_splim(maname, "lolo")
            db[psname][strength]["low"] = _MASearch.get_splim(maname, "low")
            db[psname][strength]["lolim"] = \
                _MASearch.get_splim(maname, "lolim")
            db[psname][strength]["hihi"] = _MASearch.get_splim(maname, "hihi")
            db[psname][strength]["high"] = _MASearch.get_splim(maname, "high")
            db[psname][strength]["hilim"] = \
                _MASearch.get_splim(maname, "hilim")

    return db
