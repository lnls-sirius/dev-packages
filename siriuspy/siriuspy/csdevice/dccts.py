"""Define DCCT device high level PVs database.

This is not a primary source database. Primary sources can be found in:
 - Digital Multimeter: https://github.com/lnls-dig/dmm7510-epics-ioc
"""

from siriuspy.util import get_namedtuple as _get_namedtuple

# Enum types
StoredEBeam = _get_namedtuple('StoredEBeam', ('False', 'True'))
MeasModeSel = _get_namedtuple('MeasModeSel', ('Normal', 'Fast'))
MeasModeSts = _get_namedtuple('MeasModeSts', ('Unknown', 'Normal', 'Fast'))
MeasTrgSel = _get_namedtuple(
    'MeasTrgSel', ('None', 'External', 'InLevel', 'Software'))
MeasTrgSts = _get_namedtuple(
    'MeasTrgSts', ('Unknown', 'External', 'InLevel', 'Software', 'None'))
Imped = _get_namedtuple('Imped', ('AUTO', '10MOhm'))
OffOnType = _get_namedtuple('OffOnType', ('Off', 'On'))
AvgFilterTyp = _get_namedtuple('AvgFilterTyp', ('Repeat', 'Moving'))
Range = _get_namedtuple('Range', ('20 A', '2 A', '200 mA', '20 mA'))


def get_ict_database():
    """Return ICT device database."""
    pvs_database = {
        # Average Current Measurement
        'Current-Mon':     {'type': 'float', 'unit': 'mA', 'prec': 6},
        'CurrHstr-Mon':    {'type': 'float', 'count': 1000, 'unit': 'mA'},
        'RawReadings-Mon': {'type': 'float', 'count': 1000000, 'unit': 'mA'},
        'StoredEBeam-Mon': {'type': 'enum', 'enums': StoredEBeam},

        # Measurement Reliability
        'ReliableMeas-Mon':       {'type': 'int',
                                   'hihi': 7, 'high': 1, 'hilim': 7,
                                   'lolim': 0, 'low': 0, 'lolo': 0},
        'ReliableMeasLabels-Cte': {'type': 'string', 'count': 3},

        # Measurement Trigger Source and Timer Configuration
        'MeasTrg-Sel': {'type': 'enum', 'enums': MeasTrgSel},
        'MeasTrg-Sts': {'type': 'enum', 'enums': MeasTrgSts},
        'TrgDelay-SP': {'type': 'float', 'unit': 's', 'prec': 6,
                        'hihi': 100000, 'high': 100000,
                        'hilim': 100000, 'lolim': 0.000008,
                        'low': 0.000008, 'lolo': 0.000008},
        'TrgDelay-RB': {'type': 'float', 'unit': 's', 'prec': 6,
                        'hihi': 100000, 'high': 100000,
                        'hilim': 100000, 'lolim': 0.000008,
                        'low': 0.000008, 'lolo': 0.000008},

        # Measurement Mode Selection
        'MeasMode-Sel': {'type': 'enum', 'enums': MeasModeSel},
        'MeasMode-Sts': {'type': 'enum', 'enums': MeasModeSts},

        # Measurement and Filter Settings | Normal Mode
        'SampleCnt-SP':      {'type': 'float', 'hihi': 5000, 'high': 5000,
                              'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'SampleCnt-RB':      {'type': 'float', 'hihi': 5000, 'high': 5000,
                              'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'MeasPeriod-SP':     {'type': 'float', 'unit': 's', 'prec': 7,
                              'value': 0.01667, 'hihi': 10, 'high': 10,
                              'hilim': 10, 'lolim': 0.0000084,
                              'low': 0.0000084, 'lolo': 0.0000084},
        'MeasPeriod-RB':     {'type': 'float', 'unit': 's', 'prec': 7,
                              'value': 0.01667, 'hihi': 10, 'high': 10,
                              'hilim': 10, 'lolim': 0.0000084,
                              'low': 0.0000084, 'lolo': 0.0000084},
        'Imped-Sel':         {'type': 'enum', 'enums': Imped, 'value': 0},
        'Imped-Sts':         {'type': 'enum', 'enums': Imped, 'value': 0},
        'LineSync-Sel':      {'type': 'enum', 'enums': OffOnType, 'value': 0},
        'LineSync-Sts':      {'type': 'enum', 'enums': OffOnType, 'value': 0},
        'RelEnbl-Sel':       {'type': 'enum', 'enums': OffOnType, 'value': 0},
        'RelEnbl-Sts':       {'type': 'enum', 'enums': OffOnType, 'value': 0},
        'RelLvl-SP':         {'type': 'float', 'prec': 16,
                              'high': 1000000, 'hihi': 1000000,
                              'hilim': 1000000, 'lolim': -1000000,
                              'low': -1000000, 'lolo': -1000000},
        'RelLvl-RB':         {'type': 'float', 'prec': 16,
                              'high': 1000000, 'hihi': 1000000,
                              'hilim': 1000000, 'lolim': -1000000,
                              'low': -1000000, 'lolo': -1000000},
        'RelAcq-Cmd':        {'type': 'int', 'value': 0},
        'AvgFilterEnbl-Sel': {'type': 'enum', 'enums': OffOnType},
        'AvgFilterEnbl-Sts': {'type': 'enum', 'enums': OffOnType},
        'AvgFilterCnt-SP':   {'type': 'float', 'hihi': 100, 'high': 100,
                              'hilim': 100, 'lolim': 1, 'low': 1, 'lolo': 1},
        'AvgFilterCnt-RB':   {'type': 'float', 'hihi': 100, 'high': 100,
                              'hilim': 100, 'lolim': 1, 'low': 1, 'lolo': 1},
        'AvgFilterTyp-Sel':  {'type': 'enum', 'enums': AvgFilterTyp},
        'AvgFilterTyp-Sts':  {'type': 'enum', 'enums': AvgFilterTyp},
        'AvgFilterWind-SP':  {'type': 'float', 'unit': '%',
                              'hihi': 10, 'high': 10, 'hilim': 10,
                              'lolim': 0, 'low': 0, 'lolo': 0},
        'AvgFilterWind-RB':  {'type': 'float', 'unit': '%',
                              'hihi': 10, 'high': 10, 'hilim': 10,
                              'lolim': 0, 'low': 0, 'lolo': 0},

        # Measurement Settings | Fast Mode
        'FastSampleCnt-SP':  {'type': 'float', 'hihi': 5000, 'high': 5000,
                              'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'FastSampleCnt-RB':  {'type': 'float', 'hihi': 5000, 'high': 5000,
                              'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'FastMeasPeriod-SP': {'type': 'float', 'unit': 's', 'prec': 7,
                              'value': 0.001, 'hihi': 5, 'high': 5,
                              'hilim': 5, 'lolim': 0.000001,
                              'low': 0.000001, 'lolo': 0.000001},
        'FastMeasPeriod-RB': {'type': 'float', 'unit': 's', 'prec': 7,
                              'value': 0.001, 'hihi': 5, 'high': 5,
                              'hilim': 5, 'lolim': 0.000001,
                              'low': 0.000001, 'lolo': 0.000001},
        'FastImped-Sel':     {'type': 'enum', 'enums': Imped, 'value': 0},
        'FastImped-Sts':     {'type': 'enum', 'enums': Imped, 'value': 0},
        'FastRelEnbl-Sel':   {'type': 'enum', 'enums': OffOnType, 'value': 0},
        'FastRelEnbl-Sts':   {'type': 'enum', 'enums': OffOnType, 'value': 0},
        'FastRelLvl-SP':     {'type': 'float', 'prec': 16,
                              'high': 1000000, 'hihi': 1000000,
                              'hilim': 1000000, 'lolim': -1000000,
                              'low': -1000000, 'lolo': -1000000},
        'FastRelLvl-RB':     {'type': 'float', 'prec': 16,
                              'high': 1000000, 'hihi': 1000000,
                              'hilim': 1000000, 'lolim': -1000000,
                              'low': -1000000, 'lolo': -1000000},
        'FastRelAcq-Cmd':    {'type': 'int', 'value': 0},

        # Current Measurement Range and Threshold Detection | Both Modes
        'Range-Sel':      {'type': 'enum', 'enums': Range},
        'Range-Sts':      {'type': 'enum', 'enums': Range},
        'LowLimEnbl-Sel': {'type': 'enum', 'enums': OffOnType},
        'LowLimEnbl-Sts': {'type': 'enum', 'enums': OffOnType},
        'CurrThold-SP':   {'type': 'float', 'unit': 'mA', 'prec': 6,
                           'hihi': 2000, 'high': 2000, 'hilim': 2000,
                           'lolim': -2000, 'low': -2000, 'lolo': -2000},
        'CurrThold-RB':   {'type': 'float', 'unit': 'mA', 'prec': 6,
                           'hihi': 2000, 'high': 2000, 'hilim': 2000,
                           'lolim': -2000, 'low': -2000, 'lolo': -2000},
        'HFReject-Sel':   {'type': 'enum', 'enums': OffOnType},
        'HFReject-Sts':   {'type': 'enum', 'enums': OffOnType},

        # DCCT Calibration Setting
        'Test-Sel': {'type': 'enum', 'enums': OffOnType},
        'Test-Sts': {'type': 'enum', 'enums': OffOnType},

        # Multimeter Setup
        'Download-Cmd': {'type': 'int', 'value': 0}
    }
    return pvs_database
