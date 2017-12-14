"""Select sirius dipole PVs and create IOC Database.

get_ma_devices
    Function to get magnet devices belonging to the sirius IOC
get_pvs_database
    Function that builds the IOC database
"""
from siriuspy.search import MASearch as _MASearch
from siriuspy.factory import MagnetFactory as _MagnetFactory
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_PREFIX = None
_IOC_TYPE = None
_PREFIX_SECTOR = None
_MA_DEVICES = None
_IOC = None

_ioc_dict = {
    'tb-ma-dipole-fam':      {'name': 'tb-ma-dipole-fam',
                              'type': 'Glob:AP-MADipoleFam',
                              'prefix_sector': 'TB-',
                              'sec': 'TB',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': 'B.*'},
    'tb-ma-corrector':       {'name': 'tb-ma-corrector',
                              'type': 'Glob:AP-MACorrector',
                              'prefix_sector': 'TB-',
                              'sec': 'TB',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': '(CH|CV).*'},
    'tb-ma-multipole':       {'name': 'tb-ma-multipole',
                              'type': 'Glob:AP-MAMultipole',
                              'prefix_sector': 'TB-',
                              'sec': 'TB',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': '(Q|S).*'},
    'ts-ma-dipole-fam':      {'name': 'ts-ma-dipole-fam',
                              'type': 'Glob:AP-MADipoleFam',
                              'prefix_sector': 'TS-',
                              'sec': 'TS',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': 'B.*'},
    'ts-ma-corrector':       {'name': 'ts-ma-corrector',
                              'type': 'Glob:AP-MACorrector',
                              'prefix_sector': 'TS-',
                              'sec': 'TS',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': '(CH|CV).*'},
    'ts-ma-multipole':       {'name': 'ts-ma-multipole',
                              'type': 'Glob:AP-MAMultipole',
                              'prefix_sector': 'TS-',
                              'sec': 'TS',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': '(Q|S).*'},
    'bo-ma-dipole-fam':      {'name': 'bo-ma-dipole-fam',
                              'type': 'Glob:AP-MADipoleFam',
                              'prefix_sector': 'BO-',
                              'sec': 'BO',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': 'B.*'},
    'bo-ma-corrector':       {'name': 'bo-ma-corrector',
                              'type': 'Glob:AP-CMACorrector',
                              'prefix_sector': 'BO-',
                              'sec': 'BO',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': '(CH|CV).*'},
    'bo-ma-multipole-fam':   {'name': 'bo-ma-multipole-fam',
                              'type': 'Glob:AP-MAMultipoleFam',
                              'prefix_sector': 'BO-',
                              'sec': 'BO',
                              'sub': 'Fam',
                              'dis': 'MA',
                              'dev': '(Q|S).*'},
    'bo-ma-quadrupole-skew': {'name': 'bo-ma-quadrupole-skew',
                              'type': 'Glob:AP-MAQuadrupoleSkew',
                              'prefix_sector': 'BO-',
                              'sec': 'BO',
                              'sub': '\d{2}\w',
                              'dis': 'MA',
                              'dev': 'QS'},
    'si-ma-dipole-fam':      {'name': 'si-ma-dipole-fam',
                              'type': 'Glob:AP-MADipoleFam',
                              'prefix_sector': 'SI-',
                              'sec': 'SI',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': 'B1B2'},
    'si-ma-corrector-slow':  {'name': 'si-ma-corrector-slow',
                              'type': 'Glob:AP-MACorrectorSlow',
                              'prefix_sector': 'SI-',
                              'sec': 'SI',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': '(CH|CV).*'},
    'si-ma-corrector-fast':  {'name': 'si-ma-corrector-fast',
                              'type': 'Glob:Ap-MACorrectorFast',
                              'prefix_sector': 'SI-',
                              'sec': 'SI',
                              'sub': '.*',
                              'dis': 'MA',
                              'dev': '(FCH|FCV).*'},
    'si-ma-multipole-fam':   {'name': 'si-ma-multipole-fam',
                              'type': 'Glob:AP-MAMultipoleFam',
                              'prefix_sector': 'SI-',
                              'sec': 'SI',
                              'sub': 'Fam',
                              'dis': 'MA',
                              'dev': '(Q|S).*'},
    'si-ma-quadrupole-trim': {'name': 'si-ma-quadrupole-trim',
                              'type': 'Glob:AP-MAQuadrupoleTrim',
                              'prefix_sector': 'SI-',
                              'sec': 'SI',
                              'sub': '\d{2}\w\d',
                              'dis': 'MA',
                              'dev': '(QF|QD|Q[0-9]).*'},
    'si-ma-quadrupole-skew': {'name': 'si-ma-quadrupole-skew',
                              'type': 'Glob:AP-MAQuadrupoleSkew',
                              'prefix_sector': 'SI-',
                              'sec': 'SI',
                              'sub': '\d{2}\w\d',
                              'dis': 'MA',
                              'dev': 'QS.*'},
    'as-pm':                 {'name': 'as-pm',
                              'type': 'Glob:PM',
                              'prefix_sector': '',
                              'sec': '.*',
                              'sub': '.*',
                              'dis': 'PM',
                              'dev': '.*'},
}


def select_ioc(ioc_name):
    """Set IOC."""
    global _IOC, _IOC_TYPE, _PREFIX_SECTOR, _PREFIX, _MA_DEVICES
    if ioc_name in _ioc_dict:
        if _IOC is not None and ioc_name != _IOC['name']:
            _MA_DEVICES = None
        _IOC = _ioc_dict[ioc_name]
        _IOC_TYPE = _ioc_dict[ioc_name]['type']
        _PREFIX_SECTOR = _ioc_dict[ioc_name]['prefix_sector']
        _PREFIX = _PREFIX_VACA + _PREFIX_SECTOR
    else:
        raise Exception('IOC name not defined!')


def get_pvs_database():
    """Return IOC database."""
    MA_DEVICES = get_ma_devices()
    if MA_DEVICES:
        pv_database = {_IOC_TYPE + ':Version-Cte':
                       {'type': 'str', 'value': _COMMIT_HASH}}
        for device_name, ma_device in MA_DEVICES.items():
            # for ps_name in ma_device.ps_names:
            # print(device_name)
            db = ma_device.get_database(device_name)
            pv_database.update(db)
        return pv_database
    else:
        return {}


def get_ma_devices():
    """Create/Return PowerSupplyMA objects for each magnet."""
    global _MA_DEVICES
    if _IOC is None:
        return []
    if _MA_DEVICES is None:
        _MA_DEVICES = {}
        magnets = _MASearch.get_manames(_IOC)
        for magnet in magnets:
            if _PREFIX_SECTOR:
                _, device = magnet.split(_PREFIX_SECTOR)
            else:
                device = magnet
            # Get dipole object
            _MA_DEVICES[device] = \
                _MagnetFactory.factory(magnet)

    return _MA_DEVICES
