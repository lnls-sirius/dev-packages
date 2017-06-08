#import copy as _copy
#import siriuspy as _siriuspy
#from siriuspy.namesys import SiriusPVName as _SiriusPVName
#from siriuspy.pwrsupply import ControllerEpics as _ControllerEpics
#from siriuspy.pwrsupply import PowerSupplyMAFam as _PowerSupplyMAFam
#from siriuspy.pwrsupply.psdata import get_setpoint_limits as _get_setpoint_limits
#from siriuspy.magnet import MagnetFam as _MagnetFam

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.search import MASearch as _MASearch
from siriuspy.pwrsupply import PowerSupplyMA


with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

_connection_timeout = 0.05

_PREFIX         = 'SI-Fam:MA-'
_PREFIX_VACA    = _vaca_prefix
# _PREFIX_PS          =  'SI-Fam:PS-'
# _PREFIX_VACA_PS     =  _PREFIX_VACA + _PREFIX_PS
#
# quadrupole_families = (
#     'QFA','QDA','QDB1','QFB','QDB2','QDP1','QFP','QDP2','Q1','Q2','Q3','Q4',)
#
# sextupole_families = (
#     'SDA0','SDA1','SDA2','SDA3',
#     'SDB0','SDB1','SDB2','SDB3',
#     'SDP0','SDP1','SDP2','SDP3',
#     'SFA0','SFA1','SFA2',
#     'SFB0','SFB1','SFB2',
#     'SFP0','SFP1','SFP2',)
#
# families = quadrupole_families + sextupole_families

_ps_devices = None
_ma_devices = None

# def get_ps_devices():
#
#     global _ps_devices
#     if _ps_devices is not None:
#         return _ps_devices
#
#     _ps_devices = {}
#     for family in families:
#         ps_name = 'SI-Fam:PS-' + family
#         sp_lims = _get_setpoint_limits(ps_name)
#         controller = _ControllerEpics(ps_name = _PREFIX_VACA_PS + family,
#                                       connection_timeout = _connection_timeout,
#                                       current_min = sp_lims['DRVL'],
#                                       current_max = sp_lims['DRVH'])
#         psdev = _PowerSupplyMAFam(ps_name = ps_name,
#                                   controller=controller,
#                                   enum_keys=False)
#         _ps_devices[family] = psdev
#     return _ps_devices

def get_ma_devices():
    ''' Create/Returns PowerSupplyMA objects for each magnet. '''
    global _ma_devices
    if _ma_devices is None:
        _ma_devices = {}
        #Create filter, only getting Fam Quads
        filters = [
            dict(
                section='SI',
                sub_section='Fam',
                discipline='MA',
                device='(?:QD|QF|Q[0-9]).*'
            ),
        ]
        #Get magnets
        magnets = _MASearch.get_manames(filters)
        #Create objects that'll handle the magnets
        for magnet in magnets:
            _, device = magnet.split('SI-Fam:MA-')
            _ma_devices[device] = PowerSupplyMA(
                maname=magnet, use_vaca=True, vaca_prefix=_PREFIX_VACA)

    return _ma_devices

    '''
    ps_devices = get_ps_devices()
    _ma_devices = {}

    for family in quadrupole_families:
        ma_name = 'SI-Fam:MA-' + family
        madev = _MagnetFam(name = ma_name,
                           magnet_type = 'normal_quadrupole',
                           power_supplies=None,
                           left=None,
                           right=None)
        madev.add_power_supplies((ps_devices[family],))
        _ma_devices[family] = madev

    for family in sextupole_families:
        ma_name = 'SI-Fam:MA-' + family
        madev = _MagnetFam(name = ma_name,
                           magnet_type = 'normal_sextupole',
                           power_supplies=None,
                           left=None,
                           right=None)
        madev.add_power_supplies((ps_devices[family],))
        _ma_devices[family] = madev
    '''

def get_pvs_database():
    ''' '''
    pv_database = {'IOC:Version-Cte':{'type':'str', 'value':__version__}}
    ma_devices = get_ma_devices()
    for device_name, ma_device in ma_devices.items():
        #for ps_name in ma_device.ps_names:
        pv_database.update(ma_device._get_database(device_name))
    return pv_database
