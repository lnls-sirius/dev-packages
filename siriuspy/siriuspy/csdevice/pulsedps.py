"""Pulsed power supply database definition."""
from siriuspy.pulsedps import properties as pu_props
from siriuspy.pulsedma import properties as pm_props
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch


def get_pulsed_ps_propty_database(pstype):
    """Return database definition for a pulsed power supply."""
    units = _PSSearch.get_splims_unit()[1]
    precision = 4

    db = {
        # Digital signals
        pu_props.PwrStateSel: {"type": "enum",
                               "enums": _et.enums("OffOnTyp"),
                               "value": _et.idx.Off},
        pu_props.PwrStateSts: {"type": "enum",
                               "enums": _et.enums("OffOnTyp"),
                               "value": _et.idx.Off},
        pu_props.EnablePulsesSel: {"type": "enum",
                                   "enums": _et.enums("DsblEnblTyp"),
                                   "value": _et.idx.Dsbl},
        pu_props.EnablePulsesSts: {"type": "enum",
                                   "enums": _et.enums("DsblEnblTyp"),
                                   "value": _et.idx.Dsbl},
        pu_props.ResetCmd: {"type": "int", "value": 0},

        # Waveform

        # Read only digital signals
        pu_props.CtrlMode: {"type": "enum",
                            "enums": _et.enums('RmtLocTyp'),
                            "value": _et.idx.Remote},
        pu_props.ExternalInterlock: {"type": "int", "value": 0},

        # Analog signals
        pu_props.TensionSP: {"type": "float", "unit": units[0],
                             "value": 0.0, "prec": precision},
        pu_props.TensionRB: {"type": "float", "unit": units[0],
                             "value": 0.0, "prec": precision},
        pu_props.TensionRefMon: {"type": "float", "unit": units[0],
                                 "value": 0.0, "prec": precision},
        pu_props.TensionMon: {"type": "float", "unit": units[0],
                              "value": 0.0, "prec": precision}
    }
    # Get tension limits
    analog_signals = [pu_props.TensionSP, pu_props.TensionRB,
                      pu_props.TensionRefMon, pu_props.TensionMon]

    for signal in analog_signals:
        db[signal]["lolo"] = _PSSearch.get_splim(pstype, "lolo")
        db[signal]["low"] = _PSSearch.get_splim(pstype, "low")
        db[signal]["lolim"] = _PSSearch.get_splim(pstype, "lolim")
        db[signal]["hihi"] = _PSSearch.get_splim(pstype, "hihi")
        db[signal]["high"] = _PSSearch.get_splim(pstype, "high")
        db[signal]["hilim"] = _PSSearch.get_splim(pstype, "hilim")

    return db


def get_pm_propty_database(maname, psdata):
    """Return database for a pulsed magnet."""
    unit = _MASearch.get_splims_unit()[1]
    precision = 6

    db = {}
    print(psdata)
    for psname, data in psdata.items():
        db[psname] = data.propty_database

        db[psname][pm_props.StrengthSP] = \
            {"type": "float", "unit": unit[0], "value": 0.0, "prec": precision}
        db[psname][pm_props.StrengthRB] = \
            {"type": "float", "unit": unit[0], "value": 0.0, "prec": precision}
        db[psname][pm_props.StrengthRefMon] = \
            {"type": "float", "unit": unit[0], "value": 0.0, "prec": precision}
        db[psname][pm_props.StrengthMon] = \
            {"type": "float", "unit": unit[0], "value": 0.0, "prec": precision}

        strength_list = [pm_props.StrengthSP, pm_props.StrengthRB,
                         pm_props.StrengthRefMon, pm_props.StrengthMon]

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
