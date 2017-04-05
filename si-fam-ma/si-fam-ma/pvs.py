import copy as _copy
import siriuspy as _siriuspy
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply import ControllerEpics as _ControllerEpics
from siriuspy.pwrsupply import PowerSupplyMA as _PowerSupplyMA
from siriuspy.pwrsupply.psdata import get_setpoint_limits as _get_setpoint_limits
from siriuspy.magnet import Magnet as _Magnet


with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

_connection_timeout = 0.05

_PREFIX             = 'SI-Fam:MA-'
_PREFIX_VACA        = _siriuspy.envars.vaca_prefix
_PREFIX_PS          =  'SI-Fam:PS-'
_PREFIX_VACA_PS     =  _PREFIX_VACA + _PREFIX_PS

quadrupole_families = (
    'QFA','QDA','QDB1','QFB','QDB2','QDP1','QFP','QDP2','Q1','Q2','Q3','Q4',)

sextupole_families = (
    'SDA0','SDA1','SDA2','SDA3',
    'SDB0','SDB1','SDB2','SDB3',
    'SDP0','SDP1','SDP2','SDP3',
    'SFA0','SFA1','SFA2',
    'SFB0','SFB1','SFB2',
    'SFP0','SFP1','SFP2',)

families = quadrupole_families + sextupole_families


_ps_devices = None
_ma_devices = None

def get_ps_devices():

    global _ps_devices
    if _ps_devices is not None:
        return _ps_devices

    _ps_devices = {}
    for family in families:
        ps_name = 'SI-Fam:PS-' + family
        sp_lims = _get_setpoint_limits(ps_name)
        controller = _ControllerEpics(ps_name = _PREFIX_VACA_PS + family,
                                      connection_timeout = _connection_timeout,
                                      current_min = sp_lims['DRVL'],
                                      current_max = sp_lims['DRVH'])
        psdev = _PowerSupplyMA(ps_name = ps_name,
                               controller=controller,
                               enum_keys=False)
        _ps_devices[family] = psdev
    return _ps_devices


def get_ma_devices():

    global _ma_devices
    if _|ma_devices is not None:
        return _ma_devices

    ps_devices = get_ps_devices()
    ma_devices = {}
    for family in families:
        ma_name = 'SI-Fam:MA-' + family
        madev = _Magnet(name = ma_name,
                        power_supplies=None,
                        left=None,
                        right=None)
        ps_names = madev.list_exc_ps_names()
        psdevs = [ps_devices[ps_name] for ps_name in ps_names]
        madev.add_power_supplies(ps_names)
        ma_devices[ma_name] = madev
    return ma_devices

def get_pvs_database():

    pv_database = {}
    pv_database[_PREFIX] = {}
    ps_devices = get_ps_devices()
    for ps_name, ps_device in ps_devices.items():
        pv_database[_PREFIX].update(ps_device.database)
    return pv_database
