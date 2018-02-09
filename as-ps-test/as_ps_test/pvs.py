"""Module to create PV database."""

from siriuspy import envars as _envars
import siriuspy.util as _util
from siriuspy.pwrsupply.beaglebone import BeagleBone as _BeagleBone


_PREFIX = _envars.vaca_prefix


ps_devices = None

_COMMIT_HASH = _util.get_last_commit_hash()


def get_ps_devices(bbblist, simulate=True):
    """Create/Return PowerSupplyMA objects for each magnet."""
    global ps_devices
    bbbs = list()
    if ps_devices is None:
        ps_devices = {}
        # Create objects that'll handle the magnets
        print('creating pv database...')
        for bbbname in bbblist:
            bbb = _BeagleBone(bbbname=bbbname, simulate=simulate)
            bbbs.append(bbb)
            for psname in bbb.psnames:
                ps_devices[psname] = bbb[psname]
        print('finished')

    for bbb in bbbs:
        bbb.scanning = True

    return ps_devices


def get_pvs_database(bbblist, simulate=True):
    """Return PV database."""
    global ps_devices

    ps_devices = get_ps_devices(bbblist)
    db = {bbblist[0] + '-Glob:PS-Test:Version-Cte':
          {'type': 'str', 'value': _COMMIT_HASH}}
    db = {}
    for psname in ps_devices:
        ps_db = ps_devices[psname].get_database()
        props = list(ps_db.keys())
        for i in range(len(props)):
            # if props[i] == 'Current-SP':
            #     ps_db[props[i]]['value'] = 1.0
            db[psname + ':' + props[i]] = ps_db[props[i]]
    return {_PREFIX: db}
