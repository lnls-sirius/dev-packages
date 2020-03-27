"""Define PVs, constants and properties of LIEmitMeas IOC."""

from .. import csdev as _csdev


# --- Enumeration Types ---
class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    MEASURESTATE = ('Stopped', 'Measuring')
    PLANE = ('Y', 'X')


_et = ETypes  # syntactic sugar


# --- Const class ---
class Const(_csdev.Const):
    """Const class defining constants."""

    DEFAULT_PROFILE = 'LA-BI:PRF5'

    MeasureState = _csdev.Const.register('MeasureState', _et.MEASURESTATE)
    Plane = _csdev.Const.register('Plane', _et.PLANE)

    @classmethod
    def get_database(cls, prefix=''):
        """Return IOC database."""
        dbase = {
            'MeasureCtrl-Sel': {
                'type': 'enum', 'value': cls.MeasureState.Stopped,
                'enums': cls.MeasureState._fields},
            'MeasureCtrl-Sts': {
                'type': 'enum', 'value': cls.MeasureState.Stopped,
                'enums': cls.MeasureState._fields},
            }
        for val in dbase.values():
            low = val.get('lolim', None)
            hig = val.get('hilim', None)
            if low is not None:
                val['lolo'] = low
                val['low'] = low
            if hig is not None:
                val['hihi'] = hig
                val['high'] = hig
        if prefix:
            dbase = {prefix + k: v for k, v in dbase.items()}
        dbase.update(_csdev.Const.get_database(prefix=prefix))
        return dbase
