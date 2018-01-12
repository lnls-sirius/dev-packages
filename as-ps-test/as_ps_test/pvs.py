"""Module to create PV database."""

import os as _os
from siriuspy import envars as _envars
from siriuspy.search import PSSearch as _PSSearch
import siriuspy.util as _util
from siriuspy.pwrsupply.controller import ControllerSim as _ControllerSim
# from siriuspy.pwrsupply.controller import PUControllerSim as _PUControllerSim
from siriuspy.pwrsupply.model import PowerSupply as _PowerSupply


_PREFIX = _envars.vaca_prefix


ps_devices = None

_COMMIT_HASH = _util.get_last_commit_hash()


def get_ps_devices():
    """Create/Return PowerSupplyMA objects for each magnet."""
    global ps_devices
    if ps_devices is None:
        ps_exc_list = _os.environ.get('PS_EXCLUSION_LIST', '').split()
        print('PS_EXCLUSION_LIST: ', ps_exc_list)
        ps_devices = {}
        # Get magnets
        pwr_supplies = _PSSearch.get_psnames({'dis': 'PS', 'dev': 'B.*'})
        # Create objects that'll handle the magnets
        print('creating pv database...')
        for ps in pwr_supplies:
            if ps in ps_exc_list:
                continue
            # if 'B1B2' not in ps:
            #     continue
            if 'PU' in ps:
                # c = _PUControllerSim(psname=ps)
                pass
            else:
                c = _ControllerSim(model=0)
            ps_devices[ps] = _PowerSupply(controller=c, psname=ps)
        print('finished')

    return ps_devices


def get_pvs_database():
    """Return PV database."""
    global ps_devices

    ps_devices = get_ps_devices()
    db = {'AS-Glob:PS-Test:Version-Cte':
          {'type': 'str', 'value': _COMMIT_HASH}}
    for psname in ps_devices:
        ps_db = ps_devices[psname].get_database()
        props = list(ps_db.keys())
        for i in range(len(props)):
            # if props[i] == 'Current-SP':
            #     ps_db[props[i]]['value'] = 1.0
            db[psname + ':' + props[i]] = ps_db[props[i]]
    return {_PREFIX: db}
