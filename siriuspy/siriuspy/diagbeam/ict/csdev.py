"""Define ICT device high level PVs database.

This is not a primary source database. Primary sources can be found in:
 - Digital Multimeter: https://github.com/lnls-dig/dmm7510-epics-ioc
"""

from ... import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    RANGESEL = ('40 nC', '20 nC', '10 nC', '8 nC', '4 nC', '2 nC', '0.8 nC')
    RANGESTS = ('UNKNOWN', '40 nC', '20 nC', '10 nC', '8 nC', '4 nC', '2 nC',
                '0.8 nC')
    IMPED = ('AUTO', '10MOhm')
    SAMPLETRGSEL = ('None', 'External', 'InLevel')
    SAMPLETRGSTS = ('Unknown', 'External', 'InLevel', 'None')
    CALCHARGE = ('1 nC', '100 pC', '10 pC', '1 pC')


_et = ETypes  # syntactic sugar


# --- Database ---

def get_ict_database():
    """Return ICT device database."""
    pvs_database = {
        # Charge Measurement
        'Charge-Mon':      {'type': 'float', 'unit': 'nC', 'prec': 6},
        'ChargeHstr-Mon':  {'type': 'float', 'count': 1000, 'unit': 'nC'},

        # Measurement Reliability
        'ReliableMeas-Mon': {'type': 'int', 'hihi': 7, 'high': 1, 'hilim': 7,
                             'lolim': 0, 'low': 0, 'lolo': 0},
        'ReliableMeasLabels-Cte': {'type': 'string', 'count': 3},

        # Digitize Trigger source
        'SampleTrg-Sel': {'type': 'enum', 'enums': _et.SAMPLETRGSEL},
        'SampleTrg-Sts': {'type': 'enum', 'enums': _et.SAMPLETRGSTS},

        # Level Threshold
        'Threshold-SP': {'type': 'float', 'unit': 'nC', 'prec': 6,
                         'hihi': 40, 'high': 40, 'hilim': 40,
                         'lolim': 0, 'low': 0, 'lolo': 0},
        'Threshold-RB': {'type': 'float', 'unit': 'nC', 'prec': 6,
                         'hihi': 40, 'high': 40, 'hilim': 40,
                         'lolim': 0, 'low': 0, 'lolo': 0},
        'HFReject-Sel': {'type': 'enum', 'enums': _et.OFF_ON},
        'HFReject-Sts': {'type': 'enum', 'enums': _et.OFF_ON},

        # Measure timer configuration
        '2ndReadDly-SP': {'type': 'float', 'unit': 's', 'prec': 6,
                          'hihi': 100000, 'high': 100000,
                          'hilim': 100000, 'lolim': 0.000008,
                          'low': 0.000008, 'lolo': 0.000008},
        '2ndReadDly-RB': {'type': 'float', 'unit': 's', 'prec': 6,
                          'hihi': 100000, 'high': 100000,
                          'hilim': 100000, 'lolim': 0.000008,
                          'low': 0.000008, 'lolo': 0.000008},

        # Raw Charge Measurement
        'RawReadings-Mon': {'type': 'float', 'count': 1000, 'unit': 'nC'},
        'RawPulse-Mon':    {'type': 'float', 'count': 1000, 'unit': 'nC'},
        'RawNoise-Mon':    {'type': 'float', 'count': 1000, 'unit': 'nC'},

        # Digitize Settings
        'SampleCnt-SP':  {'type': 'int',
                          'hihi': 1000000, 'high': 1000000, 'hilim': 1000000,
                          'lolim': 1, 'low': 1, 'lolo': 1},
        'SampleCnt-RB':  {'type': 'int',
                          'hihi': 1000000, 'high': 1000000, 'hilim': 1000000,
                          'lolim': 1, 'low': 1, 'lolo': 1},
        'Aperture-SP':   {'type': 'int', 'unit': 'us', 'value': 1,
                          'hihi': 1000, 'high': 1000, 'hilim': 1000,
                          'lolim': 1, 'low': 1, 'lolo': 1},
        'Aperture-RB':   {'type': 'int', 'unit': 'us', 'value': 1,
                          'hihi': 1000, 'high': 1000, 'hilim': 1000,
                          'lolim': 1, 'low': 1, 'lolo': 1},
        'SampleRate-SP': {'type': 'int', 'unit': 'readings/s',
                          'hihi': 1000000, 'high': 1000000, 'hilim': 1000000,
                          'lolim': 1000, 'low': 1000, 'lolo': 1000},
        'SampleRate-RB': {'type': 'int', 'unit': 'readings/s',
                          'hihi': 1000000, 'high': 1000000, 'hilim': 1000000,
                          'lolim': 1000, 'low': 1000, 'lolo': 1000},
        'Imped-Sel':     {'type': 'enum', 'enums': _et.IMPED, 'value': 0},
        'Imped-Sts':     {'type': 'enum', 'enums': _et.IMPED, 'value': 0},

        # Charge Digitize Range
        'BCMRange-SP': {'type': 'float', 'unit': 'V', 'prec': 6,
                        'hihi': 10, 'high': 10, 'hilim': 10,
                        'lolim': 1, 'low': 1, 'lolo': 1},
        'Range-Sel':   {'type': 'enum', 'enums': _et.RANGESEL},
        'Range-Sts':   {'type': 'enum', 'enums': _et.RANGESTS},

        # BCM Calibration Settings
        'CalEnbl-Sel':   {'type': 'enum', 'enums': _et.OFF_ON},
        'CalEnbl-Sts':   {'type': 'enum', 'enums': _et.OFF_ON},
        'CalCharge-Sel': {'type': 'enum', 'enums': _et.CALCHARGE, 'value': 0},
        'CalCharge-Sts': {'type': 'enum', 'enums': _et.CALCHARGE, 'value': 0},

        # Multimeter Setup
        'Download-Cmd': {'type': 'int', 'value': 0}
    }
    return pvs_database
