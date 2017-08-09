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
                              'type': 'Glob:MA-B',
                              'prefix_sector': 'TB-',
                              'section': 'TB',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': 'B.*'},
    'tb-ma-corrector':       {'name': 'tb-ma-corrector',
                              'type': 'Glob:MA-CHCV',
                              'prefix_sector': 'TB-',
                              'section': 'TB',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(CH|CV).*'},
    'tb-ma-multipole':       {'name': 'tb-ma-multipole',
                              'type': 'Glob:MA-Mpole',
                              'prefix_sector': 'TB-',
                              'section': 'TB',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(Q|S).*'},
    'ts-ma-dipole-fam':      {'name': 'ts-ma-dipole-fam',
                              'type': 'Glob:MA-B',
                              'prefix_sector': 'TS-',
                              'section': 'TS',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': 'B.*'},
    'ts-ma-corrector':       {'name': 'ts-ma-corrector',
                              'type': 'Glob:MA-CHCV',
                              'prefix_sector': 'TS-',
                              'section': 'TS',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(CH|CV).*'},
    'ts-ma-multipole':       {'name': 'ts-ma-multipole',
                              'type': 'Glob:MA-Mpole',
                              'prefix_sector': 'TS-',
                              'section': 'TS',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(Q|S).*'},
    'bo-ma-dipole-fam':      {'name': 'bo-ma-dipole-fam',
                              'type': 'Glob:MA-B',
                              'prefix_sector': 'BO-',
                              'section': 'BO',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': 'B.*'},
    'bo-ma-corrector':       {'name': 'bo-ma-corrector',
                              'type': 'Glob:MA-CHCV',
                              'prefix_sector': 'BO-',
                              'section': 'BO',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(CH|CV).*'},
    'bo-ma-multipole-fam':   {'name': 'bo-ma-multipole',
                              'type': 'Glob:MA-Mpole',
                              'prefix_sector': 'BO-',
                              'section': 'BO',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(Q|S).*'},
    'si-ma-dipole-fam':      {'name': 'si-ma-dipole-fam',
                              'type': 'Glob:MA-B1B2',
                              'prefix_sector': 'SI-',
                              'section': 'SI',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': 'B1B2'},
    'si-ma-corrector-slow':  {'name': 'si-ma-corrector-slow',
                              'type': 'Glob:MA-CHCV',
                              'prefix_sector': 'SI-',
                              'section': 'SI',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(CH|CV).*'},
    'si-ma-corrector-fast':  {'name': 'si-ma-corrector-fast',
                              'type': 'Glob:MA-FCHCV',
                              'prefix_sector': 'SI-',
                              'section': 'SI',
                              'sub_section': '.*',
                              'discipline': 'MA',
                              'device': '(FCH|FCV).*'},
    'si-ma-multipole-fam':   {'name': 'si-ma-multipole-fam',
                              'type': 'Glob:MA-Mpole',
                              'prefix_sector': 'SI-',
                              'section': 'SI',
                              'sub_section': 'Fam',
                              'discipline': 'MA',
                              'device': '(Q|S).*'},
    'si-ma-quadrupole-trim': {'name': 'si-ma-quadrupole-trim',
                              'type': 'Glob:MA-QuadTrim',
                              'prefix_sector': 'SI-',
                              'section': 'SI',
                              'sub_section': '\d\d.*',
                              'discipline': 'MA',
                              'device': 'Q.*'},
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
            pv_database.update(ma_device._get_database(device_name))
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
            _, device = magnet.split(_PREFIX_SECTOR)
            # Get dipole object
            _MA_DEVICES[device] = \
                _MagnetFactory.factory(magnet)

    return _MA_DEVICES
