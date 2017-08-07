"""Pulsed power supply database definition."""
from siriuspy.pulsedps import properties
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch


def get_pulsed_ps_propty_database(pstype):
    """Return database definition for a pulsed power supply."""
    units = _PSSearch.get_splims_unit()[1]
    precision = 4

    db = {
        # Digital signals
        properties.PwrStateSel: {"type": "enum",
                                 "enums": _et.enums("OffOnTyp"),
                                 "value": _et.idx.Off},
        properties.PwrStateSts: {"type": "enum",
                                 "enums": _et.enums("OffOnTyp"),
                                 "value": _et.idx.Off},
        properties.EnablePulsesSel: {"type": "enum",
                                     "enums": _et.enums("DsblEnblTyp"),
                                     "value": _et.idx.Dsbl},
        properties.EnablePulsesSts: {"type": "enum",
                                     "enums": _et.enums("DsblEnblTyp"),
                                     "value": _et.idx.Dsbl},
        properties.ResetCmd: {"type": "int", "value": 0},

        # Waveform

        # Read only digital signals
        properties.CtrlMode: {"type": "enum",
                              "enums": _et.enums('RmtLocTyp'),
                              "value": _et.idx.Remote},
        properties.ExternalInterlock: {"type": "int", "value": 0},

        # Analog signals
        properties.TensionSP: {"type": "float", "unit": units[0],
                               "value": 0.0, "prec": precision},
        properties.TensionRB: {"type": "float", "unit": units[0],
                               "value": 0.0, "prec": precision},
        properties.TensionRefMon: {"type": "float", "unit": units[0],
                                   "value": 0.0, "prec": precision},
        properties.TensionMon: {"type": "float", "unit": units[0],
                                "value": 0.0, "prec": precision}
    }
    # Get tension limits
    analog_signals = [properties.TensionSP, properties.TensionRB,
                      properties.TensionRefMon, properties.TensionMon]

    for signal in analog_signals:
        db[signal]["lolo"] = _PSSearch.get_splim(pstype, "lolo")
        db[signal]["low"] = _PSSearch.get_splim(pstype, "low")
        db[signal]["lolim"] = _PSSearch.get_splim(pstype, "lolim")
        db[signal]["hihi"] = _PSSearch.get_splim(pstype, "hihi")
        db[signal]["hilim"] = _PSSearch.get_splim(pstype, "hilim")
        db[signal]["high"] = _PSSearch.get_splim(pstype, "hihi")

    return db
