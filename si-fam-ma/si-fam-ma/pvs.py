from siriuspy.search import MASearch as _MASearch
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.magnet.model import PowerSupplyMA
from siriuspy.envars import vaca_prefix as _vaca_prefix


with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

_connection_timeout = None

_PREFIX         = 'SI-'
_PREFIX_VACA    = _vaca_prefix

_ma_devices = None

def get_ma_devices():
    ''' Create/Returns PowerSupplyMA objects for each magnet. '''
    global _ma_devices, _PREFIX
    if _ma_devices is None:
        _ma_devices = {}
        #Create filter, only getting Fam Quads
        '''filters = [
            dict(
                section="SI",
                sub_section="Fam",
                discipline="MA",
            )
        ]
        #Get magnets
        magnets = _MASearch.get_manames(filters)

        #Trim quadrupole
        trim_filter = [
            dict(
                section="SI",
                subsection="\d{2}\w{0,2}",
                discipline="PS",
                device="(QD|QD|Q[0-9]).*"
            )
        ]
        trims = _PSSearch.get_psnames(trim_filter)'''
        magnets = ["SI-Fam:MA-QDA"]
        trims = ['SI-01M1:PS-QDA', 'SI-01M2:PS-QDA', 'SI-05M1:PS-QDA', 'SI-05M2:PS-QDA', 'SI-09M1:PS-QDA', 'SI-09M2:PS-QDA', 'SI-13M1:PS-QDA', 'SI-13M2:PS-QDA', 'SI-17M1:PS-QDA', 'SI-17M2:PS-QDA']

        #trims = map(trims, lambda x: x.replace(":PS", ":MA"))
        trims = [x.replace(":PS", ":MA") for x in trims]
        #Create objects that'll handle the magnets
        magnets += trims
        for magnet in magnets:
            _, device = magnet.split(_PREFIX)
            _ma_devices[device] = PowerSupplyMA(
                maname=magnet, use_vaca=True)

    return _ma_devices

def get_pvs_database():
    """ """
    pv_database = {'IOC:Version-Cte':{'type':'str', 'value':__version__}}
    ma_devices = get_ma_devices()
    for device_name, ma_device in ma_devices.items():
        #for ps_name in ma_device.ps_names:
        pv_database.update(ma_device._get_database(device_name))
    return pv_database
