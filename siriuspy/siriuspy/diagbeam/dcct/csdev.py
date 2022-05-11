"""Define DCCT device high level PVs database.

This is not a primary source database. Primary sources can be found in:
 - Digital Multimeter: https://github.com/lnls-dig/dmm7510-epics-ioc
"""

from ... import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    STOREDEBEAM = ('False', 'True')
    MEASMODE_SEL = ('Normal', 'Fast')
    MEASMODE_STS = ('Unknown', 'Normal', 'Fast')
    MEASTRG_SEL = ('None', 'External', 'InLevel', 'Software')
    MEASTRG_STS = ('Unknown', 'External', 'InLevel', 'Software', 'None')
    IMPED = ('AUTO', '10MOhm')
    AVGFILTERTYP = ('Repeat', 'Moving')
    RANGE = ('20 A', '2 A', '200 mA', '20 mA')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining DCCTs constants and Enum types."""

    MeasModeSel = _csdev.Const.register('MeasModeSel', _et.MEASMODE_SEL)
    MeasModeSts = _csdev.Const.register('MeasModeSts', _et.MEASMODE_STS)
    AvgFilterTyp = _csdev.Const.register('AvgFilterTyp', _et.AVGFILTERTYP)


_c = Const  # syntactic sugar


# --- Database ---

def get_dcct_database():
    """Return DCCT device database."""
    pvs_database = {
        # Average Current Measurement
        'Current-Mon': {'type': 'float', 'unit': 'mA', 'prec': 6},
        'Timestamp-Mon': {'type': 'float', 'unit': 's', 'prec': 6},
        'CurrHstr-Mon': {'type': 'float', 'count': 1000, 'unit': 'mA'},
        'TimestampHstr-Mon': {'type': 'float', 'count': 1000, 'unit': 's'},
        'ClearHstr-Cmd': {'type': 'int', 'value': 0},
        'RawReadings-Mon': {'type': 'float', 'count': 1000000, 'unit': 'mA'},
        'StoredEBeam-Mon': {'type': 'enum', 'enums': _et.STOREDEBEAM},

        # Measurement Reliability
        'ReliableMeas-Mon': {'type': 'int',
                             'hihi': 15, 'high': 1, 'hilim': 15,
                             'lolim': 0, 'low': 0, 'lolo': 0},
        'ReliableMeasLabels-Cte': {'type': 'string', 'count': 4},

        # Measurement Trigger Source and Timer Configuration
        'Enbl-Sel': {'type': 'enum', 'enums': _et.OFF_ON},
        'Enbl-Sts': {'type': 'enum', 'enums': _et.OFF_ON},
        'Abort-Cmd': {'type': 'int', 'value': 0},
        'MeasTrg-Sel': {'type': 'enum', 'enums': _et.MEASTRG_SEL},
        'MeasTrg-Sts': {'type': 'enum', 'enums': _et.MEASTRG_STS},

        # Measurement Mode Selection
        'MeasMode-Sel': {'type': 'enum', 'enums': _et.MEASMODE_SEL},
        'MeasMode-Sts': {'type': 'enum', 'enums': _et.MEASMODE_STS},

        # Measurement and Filter Settings | Normal Mode
        'SampleCnt-SP': {'type': 'float', 'hihi': 5000, 'high': 5000,
                         'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'SampleCnt-RB': {'type': 'float', 'hihi': 5000, 'high': 5000,
                         'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'MeasPeriod-SP': {'type': 'float', 'unit': 's', 'prec': 7,
                          'value': 0.01667, 'hihi': 10, 'high': 10,
                          'hilim': 10, 'lolim': 0.0000084,
                          'low': 0.0000084, 'lolo': 0.0000084},
        'MeasPeriod-RB': {'type': 'float', 'unit': 's', 'prec': 7,
                          'value': 0.01667, 'hihi': 10, 'high': 10,
                          'hilim': 10, 'lolim': 0.0000084,
                          'low': 0.0000084, 'lolo': 0.0000084},
        'MeasUpdatePeriod-Mon': {'type': 'float', 'unit': 's', 'prec': 7},
        'Imped-Sel': {'type': 'enum', 'enums': _et.IMPED, 'value': 0},
        'Imped-Sts': {'type': 'enum', 'enums': _et.IMPED, 'value': 0},
        'LineSync-Sel': {'type': 'enum', 'enums': _et.OFF_ON, 'value': 0},
        'LineSync-Sts': {'type': 'enum', 'enums': _et.OFF_ON, 'value': 0},
        'RelEnbl-Sel': {'type': 'enum', 'enums': _et.OFF_ON, 'value': 0},
        'RelEnbl-Sts': {'type': 'enum', 'enums': _et.OFF_ON, 'value': 0},
        'RelLvl-SP': {'type': 'float', 'prec': 16,
                      'high': 1000000, 'hihi': 1000000,
                      'hilim': 1000000, 'lolim': -1000000,
                      'low': -1000000, 'lolo': -1000000},
        'RelLvl-RB': {'type': 'float', 'prec': 16,
                      'high': 1000000, 'hihi': 1000000,
                      'hilim': 1000000, 'lolim': -1000000,
                      'low': -1000000, 'lolo': -1000000},
        'RelAcq-Cmd': {'type': 'int', 'value': 0},
        'AvgFilterEnbl-Sel': {'type': 'enum', 'enums': _et.OFF_ON},
        'AvgFilterEnbl-Sts': {'type': 'enum', 'enums': _et.OFF_ON},
        'AvgFilterCnt-SP': {'type': 'float', 'hihi': 100, 'high': 100,
                            'hilim': 100, 'lolim': 1, 'low': 1, 'lolo': 1},
        'AvgFilterCnt-RB': {'type': 'float', 'hihi': 100, 'high': 100,
                            'hilim': 100, 'lolim': 1, 'low': 1, 'lolo': 1},
        'AvgFilterTyp-Sel': {'type': 'enum', 'enums': _et.AVGFILTERTYP},
        'AvgFilterTyp-Sts': {'type': 'enum', 'enums': _et.AVGFILTERTYP},
        'AvgFilterWind-SP': {'type': 'float', 'unit': '%',
                             'hihi': 10, 'high': 10, 'hilim': 10,
                             'lolim': 0, 'low': 0, 'lolo': 0},
        'AvgFilterWind-RB': {'type': 'float', 'unit': '%',
                             'hihi': 10, 'high': 10, 'hilim': 10,
                             'lolim': 0, 'low': 0, 'lolo': 0},

        # Measurement Settings | Fast Mode
        'FastSampleCnt-SP': {'type': 'float', 'hihi': 5000, 'high': 5000,
                             'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'FastSampleCnt-RB': {'type': 'float', 'hihi': 5000, 'high': 5000,
                             'hilim': 5000, 'lolim': 1, 'low': 1, 'lolo': 1},
        'FastMeasPeriod-SP': {'type': 'float', 'unit': 's', 'prec': 7,
                              'value': 0.001, 'hihi': 5, 'high': 5,
                              'hilim': 5, 'lolim': 0.000001,
                              'low': 0.000001, 'lolo': 0.000001},
        'FastMeasPeriod-RB': {'type': 'float', 'unit': 's', 'prec': 7,
                              'value': 0.001, 'hihi': 5, 'high': 5,
                              'hilim': 5, 'lolim': 0.000001,
                              'low': 0.000001, 'lolo': 0.000001},
        'FastImped-Sel': {'type': 'enum', 'enums': _et.IMPED, 'value': 0},
        'FastImped-Sts': {'type': 'enum', 'enums': _et.IMPED, 'value': 0},
        'FastRelEnbl-Sel': {'type': 'enum', 'enums': _et.OFF_ON, 'value': 0},
        'FastRelEnbl-Sts': {'type': 'enum', 'enums': _et.OFF_ON, 'value': 0},
        'FastRelLvl-SP': {'type': 'float', 'prec': 16,
                          'high': 1000000, 'hihi': 1000000,
                          'hilim': 1000000, 'lolim': -1000000,
                          'low': -1000000, 'lolo': -1000000},
        'FastRelLvl-RB': {'type': 'float', 'prec': 16,
                          'high': 1000000, 'hihi': 1000000,
                          'hilim': 1000000, 'lolim': -1000000,
                          'low': -1000000, 'lolo': -1000000},
        'FastRelAcq-Cmd': {'type': 'int', 'value': 0},

        # Current Measurement Range and Threshold Detection | Both Modes
        'Range-Sel': {'type': 'enum', 'enums': _et.RANGE},
        'Range-Sts': {'type': 'enum', 'enums': _et.RANGE},
        'LowLimEnbl-Sel': {'type': 'enum', 'enums': _et.OFF_ON},
        'LowLimEnbl-Sts': {'type': 'enum', 'enums': _et.OFF_ON},
        'CurrThold-SP': {'type': 'float', 'unit': 'mA', 'prec': 6,
                         'hihi': 2000, 'high': 2000, 'hilim': 2000,
                         'lolim': -2000, 'low': -2000, 'lolo': -2000},
        'CurrThold-RB': {'type': 'float', 'unit': 'mA', 'prec': 6,
                         'hihi': 2000, 'high': 2000, 'hilim': 2000,
                         'lolim': -2000, 'low': -2000, 'lolo': -2000},
        'HFReject-Sel': {'type': 'enum', 'enums': _et.OFF_ON},
        'HFReject-Sts': {'type': 'enum', 'enums': _et.OFF_ON},

        # DCCT Calibration Setting
        'Test-Sel': {'type': 'enum', 'enums': _et.OFF_ON},
        'Test-Sts': {'type': 'enum', 'enums': _et.OFF_ON},

        # Multimeter Setup
        'Download-Cmd': {'type': 'int', 'value': 0}
    }
    return pvs_database
