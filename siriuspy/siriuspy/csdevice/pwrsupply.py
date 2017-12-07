"""Power Supply Control System Devices."""

import copy as _copy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch
# from siriuspy.csdevice import ps_properties as _ps_props

default_wfmsize = 4000
default_wfmlabels = _et.enums('PSWfmLabelsTyp')
default_intlklabels = _et.enums('PSIntlkLabelsTyp')
default_ps_current_precision = 4
default_pu_current_precision = 4

_default_ps_current_unit = None
_default_pu_current_unit = None


def get_ps_current_unit():
    """Return power supply current unit."""
    global _default_ps_current_unit
    if _default_ps_current_unit is None:
        _default_ps_current_unit = _PSSearch.get_splims_unit(ispulsed=False)
    return _default_ps_current_unit


def get_pu_current_unit():
    """Return pulsed power supply 'current' unit."""
    global _default_pu_current_unit
    if _default_pu_current_unit is None:
        _default_pu_current_unit = _PSSearch.get_splims_unit(ispulsed=True)
    return _default_pu_current_unit


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


def get_common_pu_propty_database():
    """Return database of commun to all pulsed pwrsupply PVs."""
    db = get_common_propty_database()
    db_p = {'type': 'enum', 'enums': _et.enums('DsblEnblTyp'),
            'value': _et.idx.Dsbl}
    db_v = {'type': 'float', 'value': 0.0,
            'prec': default_pu_current_precision}
    db_pu = {
        'Pulsed-Sel': _copy.deepcopy(db_p),
        'Pulsed-Sts': _copy.deepcopy(db_p),
        'Voltage-SP': _copy.deepcopy(db_v),
        'Voltage-RB': _copy.deepcopy(db_v),
        'Voltage-Mon': _copy.deepcopy(db_v),
    }
    db.update(db_pu)
    return db


def get_ps_propty_database(pstype):
    """Return property database of a LNLS power supply type device."""
    propty_db = get_common_ps_propty_database()
    signals_lims = ('Current-SP', 'Current-RB',
                    'CurrentRef-Mon', 'Current-Mon', )
    signals_unit = signals_lims + ('WfmData-SP', 'WfmData-RB')
    for propty, db in propty_db.items():
        # set setpoint limits in database
        if propty in signals_lims:
            db['lolo'] = _PSSearch.get_splims(pstype, 'lolo')
            db['low'] = _PSSearch.get_splims(pstype, 'low')
            db['lolim'] = _PSSearch.get_splims(pstype, 'lolim')
            db['hilim'] = _PSSearch.get_splims(pstype, 'hilim')
            db['high'] = _PSSearch.get_splims(pstype, 'high')
            db['hihi'] = _PSSearch.get_splims(pstype, 'hihi')
        # define unit of current
        if propty in signals_unit:
            db['unit'] = get_ps_current_unit()
    return propty_db


def get_pu_propty_database(pstype):
    """Return database definition for a pulsed power supply type."""
    propty_db = get_common_pu_propty_database()
    signals_lims = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon')
    signals_unit = signals_lims
    for propty, db in propty_db.items():
        # set setpoint limits in database
        if propty in signals_lims:
            db['lolo'] = _PSSearch.get_splims(pstype, 'lolo')
            db['low'] = _PSSearch.get_splims(pstype, 'low')
            db['lolim'] = _PSSearch.get_splims(pstype, 'lolim')
            db['hilim'] = _PSSearch.get_splims(pstype, 'hilim')
            db['high'] = _PSSearch.get_splims(pstype, 'high')
            db['hihi'] = _PSSearch.get_splims(pstype, 'hihi')
        # define unit of current
        if propty in signals_unit:
            db['unit'] = get_ps_current_unit()
    return propty_db


def get_ma_propty_database(maname):
    """Return property database of a magnet type device."""
    current_alarm = ('Current-SP', 'Current-RB',
                     'CurrentRef-Mon', 'Current-Mon', )
    current_pvs = current_alarm + ('WfmData-SP', 'WfmData-RB')
    propty_db = get_common_ps_propty_database()
    unit = _MASearch.get_splims_unit(ispulsed=False)
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    db = {}

    for psname, magfunc in magfunc_dict.items():
        db[psname] = _copy.deepcopy(propty_db)
        # set appropriate PS limits and unit
        for field in ["-SP", "-RB", "Ref-Mon", "-Mon"]:
            db[psname]['Current' + field]['lolo'] = \
                _MASearch.get_splims(maname, 'lolo')
            db[psname]['Current' + field]['low'] = \
                _MASearch.get_splims(maname, 'low')
            db[psname]['Current' + field]['lolim'] = \
                _MASearch.get_splims(maname, 'lolim')
            db[psname]['Current' + field]['hilim'] = \
                _MASearch.get_splims(maname, 'hilim')
            db[psname]['Current' + field]['high'] = \
                _MASearch.get_splims(maname, 'high')
            db[psname]['Current' + field]['hihi'] = \
                _MASearch.get_splims(maname, 'hihi')
        for propty in current_pvs:
            db[psname][propty]['unit'] = unit[0]
        # set approriate MA limits and unit
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
        elif magfunc in ('corrector-vertical', 'corrector-horizontal'):
            db[psname]['Kick-SP'] = _copy.deepcopy(db[psname]['Current-SP'])
            db[psname]['Kick-SP']['unit'] = 'rad'
            db[psname]['Kick-RB'] = _copy.deepcopy(db[psname]['Current-RB'])
            db[psname]['Kick-RB']['unit'] = 'rad'
            db[psname]['KickRef-Mon'] = \
                _copy.deepcopy(db[psname]['CurrentRef-Mon'])
            db[psname]['KickRef-Mon']['unit'] = 'rad'
            db[psname]['Kick-Mon'] = _copy.deepcopy(db[psname]['Current-Mon'])
            db[psname]['Kick-Mon']['unit'] = 'rad'
    return db


def get_pm_propty_database(maname):
    """Return property database of a pulsed magnet type device."""
    propty_db = get_common_pu_propty_database()
    current_alarm = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon', )
    unit = _MASearch.get_splims_unit(ispulsed=True)
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    db = {}
    for psname, magfunc in magfunc_dict.items():
        db[psname] = _copy.deepcopy(propty_db)
        # set appropriate PS limits and unit
        for field in ["-SP", "-RB", "-Mon"]:
            db[psname]['Voltage' + field]['lolo'] = \
                _MASearch.get_splims(maname, 'lolo')
            db[psname]['Voltage' + field]['low'] = \
                _MASearch.get_splims(maname, 'low')
            db[psname]['Voltage' + field]['lolim'] = \
                _MASearch.get_splims(maname, 'lolim')
            db[psname]['Voltage' + field]['hilim'] = \
                _MASearch.get_splims(maname, 'hilim')
            db[psname]['Voltage' + field]['high'] = \
                _MASearch.get_splims(maname, 'high')
            db[psname]['Voltage' + field]['hihi'] = \
                _MASearch.get_splims(maname, 'hihi')
        for propty in current_alarm:
            db[psname][propty]['unit'] = unit[0]
        # set approriate MA limits and unit
        if magfunc in ('corrector-vertical', 'corrector-horizontal'):
            db[psname]['Kick-SP'] = _copy.deepcopy(db[psname]['Voltage-SP'])
            db[psname]['Kick-SP']['unit'] = 'rad'
            db[psname]['Kick-RB'] = _copy.deepcopy(db[psname]['Voltage-RB'])
            db[psname]['Kick-RB']['unit'] = 'rad'
            db[psname]['Kick-Mon'] = _copy.deepcopy(db[psname]['Voltage-Mon'])
            db[psname]['Kick-Mon']['unit'] = 'rad'
        else:
            raise ValueError('Invalid pulsed magnet power supply type!')
    return db

# def get_pm_propty_database(maname, psdata):
#     """Return database for a pulsed magnet."""
#     db = {}
#     for psname, data in psdata.items():
#         db[psname] = data.propty_database
#
#         db[psname][_ps_props.StrengthSP] = \
#             {"type": "float", "unit": "mrad", "value": 0.0,
#              "prec": default_pu_current_precision}
#         db[psname][_ps_props.StrengthRB] = \
#             {"type": "float", "unit": "mrad", "value": 0.0,
#              "prec": default_pu_current_precision}
#         db[psname][_ps_props.StrengthRefMon] = \
#             {"type": "float", "unit": "mrad", "value": 0.0,
#              "prec": default_pu_current_precision}
#         db[psname][_ps_props.StrengthMon] = \
#             {"type": "float", "unit": "mrad", "value": 0.0,
#              "prec": default_pu_current_precision}
#
#         strength_list = [_ps_props.StrengthSP, _ps_props.StrengthRB,
#                          _ps_props.StrengthRefMon, _ps_props.StrengthMon]
#
#         for strength in strength_list:
#             db[psname][strength]["lolo"] = _MASearch.get_splims(maname, "lolo")
#             db[psname][strength]["low"] = _MASearch.get_splims(maname, "low")
#             db[psname][strength]["lolim"] = \
#                 _MASearch.get_splims(maname, "lolim")
#             db[psname][strength]["hihi"] = _MASearch.get_splims(maname, "hihi")
#             db[psname][strength]["high"] = _MASearch.get_splims(maname, "high")
#             db[psname][strength]["hilim"] = \
#                 _MASearch.get_splims(maname, "hilim")
#
#     return db
