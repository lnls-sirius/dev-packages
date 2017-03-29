import copy as _copy
import siriuspy as _siriuspy
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply import ControllerEpics as _ControllerEpics
from siriuspy.pwrsupply import PowerSupplyMA as _PowerSupplyMA
from siriuspy.pwrsupply.psdata import get_setpoint_limits as _get_setpoint_limits

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

# quadrupole_families = ('QDA',)

families = quadrupole_families + sextupole_families


_csdevices = None


def get_csdevices():

    global _csdevices
    if _csdevices is not None:
        return _csdevices

    _csdevices = {}
    for family in families:
        ps_name = 'SI-Fam:PS-' + family
        ma_name = 'SI-Fam:MA-' + family
        sp_lims = _get_setpoint_limits(ps_name)
        controller = _ControllerEpics(ps_name = _PREFIX_VACA_PS + family,
                                      connection_timeout = _connection_timeout,
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
