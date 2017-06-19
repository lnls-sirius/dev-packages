from siriuspy.pwrsupply import PowerSupplySim as _PowerSupplySim
from siriuspy import envars as _envars
from siriuspy.search import PSSearch as _PSSearch


_prefix = _envars.vaca_prefix


ps_devices = None


try:
    with open('VERSION','r') as _f:
        __version__ = _f.read().strip()
except:
    __version__ = 'not defined'


def get_ps_devices():
    ''' Create/Returns PowerSupplyMA objects for each magnet. '''
    global ps_devices
    if ps_devices is None:
        ps_devices = {}
        #Create filter, only getting Fam Quads
        filters = []
        #Get magnets
        pwr_supplies = _PSSearch.get_psnames()
        #Create objects that'll handle the magnets
        for ps in pwr_supplies:
            ps_devices[ps] = _PowerSupplySim(psname=ps)

    return ps_devices

def get_database():

    #global ps_devices

    ps_devices = get_ps_devices()

    db = {}
    for psname in ps_devices:
        ps_db = ps_devices[psname].database
        props = list(ps_db.keys())
        for i in range(len(props)):
            db[psname + ':' + props[i]] = ps_db[props[i]]
    return {_prefix:db}
