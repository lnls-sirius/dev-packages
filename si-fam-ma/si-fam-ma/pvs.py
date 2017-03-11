
import siriuspy as _siriuspy
from siriuspy.epics import SiriusPVsSet as _SiriusPVsSet
from siriuspy.epics import GroupPVs as _GroupPVs
from siriuspy.epics import GroupPVsDep as _GroupPVsDep


with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

_PREFIX             = 'SI-Fam:MA-'
_connection_timeout = 0.05
_PREFIX_VACA        = _siriuspy.envars.vaca_prefix
_PREFIX_PS          =  _PREFIX_VACA + 'SI-Fam:PS-'

_ps_families = (
    'QFA', 'QDA','QDB1','QFB','QDB2','QDP1','QFP','QDP2','Q1','Q2','Q3','Q4',
    'SFA0','SDA0','SDA1','SFA1','SDA2','SDA3',)
_ps_properties = (
    'CtrlMode-Mon',
    'PwrState-Sel',
    'PwrState-Sts',
    'OpMode-Sel',
    'OpMode-Sts',
    'Current-SP',
    'Current-RB',)
_primitive_pvs_set  = None
_macapp_pvs = None


def _MacAppGroupPVsDep(_GroupPVsDep):

    def __init__(self, pv_database, group_pvs):
        super().__init__(pv_database, group_pvs)

    def update(self):
        self._database['value'] = group_pvs[0].value


def get_prefix():
    """Return prefix of the machine application PVs."""
    return _PREFIX

def get_ps_families():
    """Return tupple with power supply family names."""
    return _ps_families

def get_ps_properties():
    """Return tupple with power supply properties."""
    return _ps_properties

def get_primitive_pvs_set():
    """Return set of SiriusPVs corresponding to all power supplies used in
    the machine application.
    """
    def get_properties_database_dict():
        database = {}
        for prop in ps_properties:
            database[prop] = _siriuspy.dev_types.enum_types[prop]
        return database
    def primitive_pvs_set_clear():
        global _primitive_pvs_set
        if _primitive_pvs_set:
            _primitive_pvs_set.__del__()
    def primitive_pvs_set_create():
        global _primitive_pvs_set
        primitive_pvs_set_clear()
        _primitive_pvs_set = _SiriusPVsSet(connection_timeout=_connection_timeout)
        for family in _ps_families:
            for propty in _ps_properties:
                pv_name = family + ':' + propty
                ps_pv_name = _PREFIX_PS + pv_name
                _primitive_pvs_set.add(ps_pv_name)

    if not _primitive_pvs_set:
        primitive_pvs_set_create()
    return _primitive_pvs_set

def get_macapp_pvs():
    """Return a dictionary with PVs corresponding to power supplies provided
    in the machine application.
    """
    def macapp_pvs_clear():
        global _macapp_pvs
        _macapp_pvs = None
    def macapp_pvs_create():
        global _macapp_pvs
        macapp_pvs_clear()
        pvs_set = get_primitive_pvs_set()
        _macapp_pvs = {}
        for family in _ps_families:
            for propty in _ps_properties:
                pv_name = family + ':' + propty
                ps_pv_name = _PREFIX_PS + pv_name
                ma_pv_name = _PREFIX + pv_name
                pvs_group = _GroupPVs((ps_pv_name,), pvs_set)
                _macapp_pvs[ma_pv_name] = _GroupPVsDep(database, pvs_group)


    if not _macapp_pvs:
        macapp_pvs_create()
    return _macapp_pvs



def gets_pvs_database():

    # IOC-proper PVs
    database = {
        'IOC:Version-Cte': {'type':'string', 'value':__version__},
        'IOC:Status-Mon':  {'type':'string', 'value':'not connected!'},
    }

    global origin_pvs_set

    family = 'QDA'

    for propty in ps_property:

        pv_name = family + ':' + propty
        pv_name_origin = PREFIX_ORIGIN + pv_name

        _GroupPVs((pv_name_origin, ), connection_callback=None, connection_timeout=None)

    # loop over all mirrored devices pvs, one for each ps family
    AllMirroredDevicesPVs = get_AllMirroredDevicesPVs()
    for family, mirrored_device_PVs in AllMirroredDevicesPVs.items():

        pass

#
# pvs_database[PREFIX] = {
#
#     'IOC:Version-Cte': {'type':'string', 'value':__version__},
#     'IOC:Status-Mon':  {'type':'string', 'value':'not connected!'},
#
#     'QFA:Reset-Cmd':   {'type':'int', 'value':0},
#     'QFA:State-Sel':   {'type':'enum', 'enums':_enum_types['OffOnTyp'], 'value':1, 'unit': ''},
#     'QFA:State-Sts':   {'type':'enum', 'enums':_enum_types['OffOnTyp'], 'value':1, 'unit': ''},
#     'QFA:Current-RB':  {'type':'float', 'value':0.0, 'prec':6, 'unit': 'A'},
#     'QFA:Current-SP':  {'type':'float', 'value':0.0, 'prec':6, 'unit': 'A'},
#
#     'QDA:Reset-Cmd':   {'type':'int', 'value':0},
#     'QDA:State-Sel':   {'type':'enum', 'enums':_enum_types['OffOnTyp'], 'value':1, 'unit': ''},
#     'QDA:State-Sts':   {'type':'enum', 'enums':_enum_types['OffOnTyp'], 'value':1, 'unit': ''},
#     'QDA:Current-RB':  {'type':'float', 'value':0.0, 'prec':6, 'unit': 'A'},
#     'QDA:Current-SP':  {'type':'float', 'value':0.0, 'prec':6, 'unit': 'A'},
#
# }
