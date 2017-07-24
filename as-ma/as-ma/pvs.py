"""Select sirius dipole PVs and create IOC Database.

get_ma_devices
    Function to get magnet devices belonging to the sirius IOC
get_pvs_database
    Function that builds the IOC database
"""
from siriuspy.search import MASearch as _MASearch
from siriuspy.magnet.model import MagnetFactory
from siriuspy.envars import vaca_prefix as _vaca_prefix


with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

_connection_timeout = None

_PREFIX_VACA = _vaca_prefix
_PREFIX = 'SI-'

_ma_devices = None


def get_ma_devices(args=[]):
    """Create/Return PowerSupplyMA objects for each magnet."""
    global _ma_devices, _PREFIX

    if len(args) > 0:
        _PREFIX = args[1]
        section = args[2]
        sub_section = args[3]
        discipline = args[4]
        device = args[5]

    if _ma_devices is None:
        _ma_devices = {}
        # Create filter, only getting Fam Quads
        filters = [
            dict(
                section=section,
                sub_section=sub_section,
                discipline=discipline,
                device=device
            )
        ]
        # Get magnets
        magnets = _MASearch.get_manames(filters)
        for magnet in magnets:
            _, device = magnet.split(_PREFIX)

            # Get dipole object
            _ma_devices[device] = \
                MagnetFactory.factory(magnet)

    return _ma_devices


def get_pvs_database():
    """Return IOC dagtabase."""
    pv_database = {'IOC:Version-Cte': {'type': 'str', 'value': __version__}}
    ma_devices = get_ma_devices()
    for device_name, ma_device in ma_devices.items():
        # for ps_name in ma_device.ps_names:
        pv_database.update(ma_device._get_database(device_name))
    return pv_database
