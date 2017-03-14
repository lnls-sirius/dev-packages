import siriuspy as _siriuspy
from siriuspy.epics import SiriusPVsSet as _SiriusPVsSet
from siriuspy.epics import MagnetPSDevice as _MagnetPSDevice


with open('VERSION','r') as _f:
    __version__ = _f.read().strip()


_PREFIX             = 'SI-Fam:MA-'
_magnet_quadrupole_ps_family_names = (
    'QFA','QDA','QDB1','QFB','QDB2','QDP1','QFP','QDP2','Q1','Q2','Q3','Q4',)
_magnet_sextupole_ps_family_names = (
    'SDA0','SDA1','SDA2','SDA3',
    'SDB0','SDB1','SDB2','SDB3',
    'SDP0','SDP1','SDP2','SDP3',
    'SFA0','SFA1','SFA2',
    'SFB0','SFB1','SFB2',
    'SFP0','SFP1','SFP2',)
_magnet_ps_family_names = _magnet_quadrupole_ps_family_names + _magnet_sextupole_ps_family_names
_pvs_set  = _siriuspy.epics.SiriusPVsSet()
_magnet_ps_objects = {}
_connection_timeout = 0.05
_PREFIX_VACA        = _siriuspy.envars.vaca_prefix
_PREFIX_PS          =  _PREFIX_VACA + 'SI-Fam:PS-'


def get_prefix():
    """Return prefix of the machine application PVs."""
    return _PREFIX


def get_magnet_ps_family_names():
    """Return tupple with power supply family names."""
    return _magnet_ps_family_names


def _create_magnet_ps_objects():
    global _magnet_ps_objects
    _magnet_ps_objects = {}
    for magnet_ps_name in _magnet_ps_family_names:
        ps = _MagnetPSDevice(family_name=magnet_ps_name,
                             pvs_prefix=_PREFIX_PS,
                             pvs_set=_pvs_set,
                             connection_timeout=_connection_timeout)
        _magnet_ps_objects[magnet_ps_name] = ps



def get_magnet_power_supplies():
    """Return dictionary with all magnet power supply objects used by the machine applicaiton."""
    if not _magnet_ps_objects:
        _create_magnet_ps_objects()
    return _magnet_ps_objects


def get_pvs_database():
    """Return a database with all PVs provided by the machine application."""

    database = {}
    # IOC-proper PVs
    database[_PREFIX] = {
        'IOC:Version-Cte': {'type':'string', 'value':__version__},
        'IOC:Status-Mon':  {'type':'string', 'value':'PVs not connected!'},
    }

    # Add databases corresponding to all magnet power supply objects
    magnet_ps = get_magnet_power_supplies()
    for ps_name, ps_object in magnet_ps.items():
        ps_database = ps_object.properties_database
        database[_PREFIX].update(ps_database)

    return database
