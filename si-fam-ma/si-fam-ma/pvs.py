import siriuspy as _siriuspy
from siriuspy.epics import SiriusPVsSet as _SiriusPVsSet
from siriuspy.epics import GroupPVs as _GroupPVs
from siriuspy.epics import GroupPVsDep as _GroupPVsDep

import uuid as _uuid
import siriuspy.naming_system as _ns
import copy as _copy


with open('VERSION','r') as _f:
    __version__ = _f.read().strip()


_PREFIX             = 'SI-Fam:MA-'
_magnet_ps_family_names = (
    'QFA', 'QDA','QDB1','QFB','QDB2','QDP1','QFP','QDP2','Q1','Q2','Q3','Q4',
    'SFA0','SDA0','SDA1','SFA1','SDA2','SDA3',)
_pvs_set  = _siriuspy.epics.SiriusPVsSet()
_magnet_ps_objects = {}

_connection_timeout = 0.05
_PREFIX_VACA        = _siriuspy.envars.vaca_prefix
_PREFIX_PS          =  _PREFIX_VACA + 'SI-Fam:PS-'


class MagnetPSDevice:

    _property_names = (
        'CtrlMode-Mon',
        'PwrState-Sel',
        'PwrState-Sts',
        'OpMode-Sel',
        'OpMode-Sts',
        'Current-SP',
        'Current-RB',)

    def __init__(self,
                 family_name,
                 pvs_prefix,
                 pvs_set,
                 connection_timeout=_connection_timeout,
                 ):

        self._uuid = _uuid.uuid4()                     # unique ID for the class object
        self._family_name = family_name                # family name of the power supply
        self._pvs_prefix = pvs_prefix                  # prefix of PVs used by class object
        self._pvs_set = pvs_set                        # set of Sirius PVs in use.
        self._connection_timeout = connection_timeout  # default connection timeout for the class object
        self._properties = {}

        self._create_properties_dict()
        self._add_all_pvs()

    @property
    def family_name(self):
        return self._family_name

    def device_property(self, propty):
        if propty in self._properties:
            return self._family_name + ':' + propty
        else:
            raise Exception('invalid property name "' + propty + '"!')

    def get_pv_name(self, propty):
        if propty in self._properties:
            return self._pvs_prefix + self._family_name + ':' + propty
        else:
            raise Exception('invalid property name "' + propty + '"!')

    def properties(self):
        properties = _copy.deepcopy(self._properties)
        return properties

    def properties_database(self):
        props_db = _siriuspy.dev_types.get_properties()
        database = {}
        for propty in self._properties:
            db = props_db[propty]
            db['value'] = self._properties[propty]
            database[self.device_property(propty)] = db
        return database

    def __getitem__(self, key):
        return self._properties[key]

    def __setitem__(self, key, value):
        pv_name = self.get_pv_name(key)
        self._pvs_set[pv_name] = value

    def _create_properties_dict(self):
        for propty in MagnetPSDevice._property_names:
            self._properties[propty] = None

    def _add_all_pvs(self):
        for propty in self._properties:
            pv_name = self.get_pv_name(propty)
            self._pvs_set.add(pv_name, connection_timeout=self._connection_timeout)
            self._pvs_set[pv_name].add_callback(callback=self._pvs_callback, index=self._uuid)
            self._properties[propty] = self._pvs_set[pv_name].value

    def _pvs_callback(self, pvname, value, **kwargs):
        names = _siriuspy.naming_system.split_name(pvname)
        self._properties[names['Property']] = value

    def __del__(self):
        for propty in self._properties:
            pv_name = self.get_pv_name(propty)
            self._pvs_set[pv_name].remove_callback(index=self._uuid)


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
        ps = MagnetPSDevice(family_name=magnet_ps_name,
                            pvs_prefix=_PREFIX_PS,
                            pvs_set=_pvs_set,
                            connection_timeout=_connection_timeout)
        _magnet_ps_objects[magnet_ps_name] = ps

def get_magnet_power_supplies():
    if not _magnet_ps_objects:
        _create_magnet_ps_objects()
    return _magnet_ps_objects

def gets_pvs_database():

    # IOC-proper PVs
    database = {
        'IOC:Version-Cte': {'type':'string', 'value':__version__},
        'IOC:Status-Mon':  {'type':'string', 'value':'not connected!'},
    }

    # Add databases corresponding to all magnet power supply objects
    magnet_ps = get_magnet_power_supplies()
    for ps_name, ps_object in magnet_ps:
        ps_database = ps_object.properties_database()
        database.update(ps_database)

    return database


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
