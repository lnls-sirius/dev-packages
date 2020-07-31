"""Define PVs, constants and properties of SI AP Manaca IOC."""
from .. import csdev as _csdev


# --- Enumeration Types ---
class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    MEASURESTATE = ('Stopped', 'Measuring')


_et = ETypes  # syntactic sugar


# --- Const class ---
class Const(_csdev.Const):
    """Const class defining constants."""

    DEF_COEFX = 10.00 * 1e-3  # [mm/px] (source: Sergio Lordano from OPT)
    DEF_COEFY = 10.04 * 1e-3  # [mm/px] (source: Sergio Lordano from OPT)
    DEF_PROFILE = 'MNC:A:BASLER02:'
    DEF_RATE = 2  # [Hz]
    IP_IOC = '10.31.74.45'
    PREFIX_IOC = 'SI-09SABL:AP-Manaca-MVS2:'

    MeasureState = _csdev.Const.register('MeasureState', _et.MEASURESTATE)

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
            'MeasureRate-SP': {
                'type': 'float', 'prec': 4, 'unit': 'Hz',
                'value': cls.DEF_RATE, 'lolim': 0.1, 'hilim': 30},
            'MeasureRate-RB': {
                'type': 'float', 'prec': 4, 'unit': 'Hz',
                'value': cls.DEF_RATE, 'lolim': 0.1, 'hilim': 30},
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

        dbase.pop(prefix + 'Px2mmScaleX-SP')
        info = dbase.pop(prefix + 'Px2mmScaleX-RB')
        info['value'] = cls.DEF_COEFX
        dbase[prefix + 'Px2mmScaleX-Cte'] = info

        dbase.pop(prefix + 'Px2mmScaleY-SP')
        info = dbase.pop(prefix + 'Px2mmScaleY-RB')
        info['value'] = cls.DEF_COEFY
        dbase[prefix + 'Px2mmScaleY-Cte'] = info
        return dbase
