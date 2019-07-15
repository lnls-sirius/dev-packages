"""Select sirius dipole PVs and create IOC Database.

get_ma_devices
    Function to get magnet devices belonging to the sirius IOC
get_pvs_database
    Function that builds the IOC database
"""
from siriuspy import util as _util
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.pwrsupply.maepics import MAEpics as _MAEpics


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_MA_DEVICES = None


def get_pvs_database(manames):
    """Return IOC database."""
    MA_DEVICES = get_ma_devices(manames)
    if MA_DEVICES:
        pv_database = {}
        for device_name, ma_device in MA_DEVICES.items():
            db = ma_device.get_database(device_name)
            for k in db:
                if 'Version-Cte' in k:
                    db[k]['value'] = _COMMIT_HASH
            pv_database.update(db)
        return pv_database
    else:
        return {}


def get_ma_devices(manames):
    """Create/Return PowerSupplyMA objects for each magnet."""
    global _MA_DEVICES

    if _MA_DEVICES is None:
        _MA_DEVICES = {}
        for maname in manames:
            # Get dipole object
            _MA_DEVICES[maname] = _MAEpics(maname, lock=False)

    return _MA_DEVICES
