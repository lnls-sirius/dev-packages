import copy as _copy
import siriuspy as _siriuspy
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply import ControllerEpicsPS as _ControllerEpicsPS
from siriuspy.pwrsupply import PowerSupplyMA as _PowerSupplyMA
from siriuspy.pwrsupply.psdata import get_setpoint_limits as _get_setpoint_limits

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

_PREFIX             = 'SI-Fam:MA-'
# _magnet_quadrupole_ps_family_names = (
#     'QFA','QDA','QDB1','QFB','QDB2','QDP1','QFP','QDP2','Q1','Q2','Q3','Q4',)
# _magnet_sextupole_ps_family_names = (
#     'SDA0','SDA1','SDA2','SDA3',
#     'SDB0','SDB1','SDB2','SDB3',
#     'SDP0','SDP1','SDP2','SDP3',
#     'SFA0','SFA1','SFA2',
#     'SFB0','SFB1','SFB2',
#     'SFP0','SFP1','SFP2',)
# _magnet_ps_family_names = _magnet_quadrupole_ps_family_names + _magnet_sextupole_ps_family_names
# _pvsset  = _siriuspy.epics.SiriusPVsSet()
# _magnet_ps_objects = {}
_connection_timeout = 0.05
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


_csdevices = None



def get_csdevices():
    global _csdevices
    if _csdevices is not None:
        return _csdevices

    _csdevices = {}
    for family in quadrupole_families:
        ps_name = 'SI-Fam:PS-' + family
        ma_name = 'SI-Fam:MA-' + family
        sp_lims = _get_setpoint_limits(ps_name)
        controller = _ControllerEpicsPS(prefix = _PREFIX_VACA,
                                        ps_name = ps_name,
                                        fluctuation_rms = 0.050,
                                        current_min = sp_lims['DRVL'],
                                        current_max = sp_lims['DRVH'])
        psdev = _PowerSupplyMA(ps_name = ps_name,
                               controller=controller,
                               enum_keys=False)
        _csdevices[family] = psdev
    return _csdevices


def get_pvs_database():

    pv_database = {}
    pv_database[_PREFIX] = {}
    csdevices = get_csdevices()
    for ps_name, csdevice in csdevices.items():
        pv_database[_PREFIX].update(csdevice.database)
    return pv_database








#
#
#
# def get_prefix():
#     """Return prefix of the machine application PVs."""
#     return _PREFIX
#
#
# def get_magnet_ps_family_names():
#     """Return tupple with power supply family names."""
#     return _magnet_ps_family_names
#
#
# def _create_magnet_ps_objects():
#     global _magnet_ps_objects
#     _magnet_ps_objects = {}
#     for magnet_ps_name in _magnet_ps_family_names:
#         ps = _MagnetPSDevice(ps_name = _PREFIX_PS + magnet_ps_name,
#                              pvsset =_pvsset,
#                              connection_timeout=_connection_timeout)
#         _magnet_ps_objects[magnet_ps_name] = ps
#
#
# def get_magnet_power_supplies():
#     """Return dictionary with all magnet power supply objects used by the machine applicaiton."""
#     if not _magnet_ps_objects:
#         _create_magnet_ps_objects()
#     return _magnet_ps_objects
#
#
# def get_pvs_database():
#     """Return a database with all PVs provided by the machine application."""
#
#     database = {}
#     # IOC-proper PVs
#     database[_PREFIX] = {
#         'IOC:Version-Cte': {'type':'string', 'value':__version__},
#         'IOC:Status-Mon':  {'type':'string', 'value':'PVs not connected!'},
#     }
#
#     # Add databases corresponding to all magnet power supply objects
#     magnet_ps = get_magnet_power_supplies()
#     for ps_name, ps_object in magnet_ps.items():
#         ps_database = ps_object.database
#         database[_PREFIX].update(ps_database)
#
#     return database
