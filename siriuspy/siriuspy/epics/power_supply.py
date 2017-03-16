
import uuid as _uuid
import copy as _copy
from siriuspy import dev_types as _dev_types
from siriuspy.epics import SiriusPVsSet as _SiriusPVsSet
from siriuspy import naming_system as _naming_system

class MagnetPSDevice:
    """Power supply device of magnets.

    This class represent magnet power supply devices with properties associated
    with EPICS PVs that are grouped within the class for convenience.
    """

    _connection_timeout = None

    _properties_names = (
        'CtrlMode-Mon',
        'PwrState-Sel',
        'PwrState-Sts',
        'OpMode-Sel',
        'OpMode-Sts',
        'Current-SP',
        'Current-RB',)

    _properties_database = _dev_types.get_device_database(_dev_types.dev_ps_magnet)

    def __init__(self,
                 family_name,
                 pvs_prefix,
                 pvs_set=None,
                 connection_timeout=_connection_timeout,
                 ):
        self._uuid = _uuid.uuid4()                     # unique ID for the class object
        self._family_name = family_name                # family name of the power supply
        self._pvs_prefix = pvs_prefix                  # prefix of PVs used by class object
        if pvs_set:
            self._pvs_set = pvs_set                    # set of Sirius PVs in use.
        else:
            self._pvs_set = _SiriusPVsSet(connection_timeout=connection_timeout)
        self._connection_timeout = connection_timeout  # default connection timeout for the class object
        self._properties_values = {}                   # a dctionary with properties current values
        self._callback_functions = {}

        self._create_properties_dict()
        self._add_all_pvs()

    @property
    def pvs_prefix(self):
        """Return prefix of connected PVs"""
        return self._pvs_prefix

    @property
    def family_name(self):
        """Return family name associated with class object."""
        return self._family_name

    def get_pv_name(self, propty):
        """Return connected PV name associated with the power supply property given as argument."""
        if propty in self._properties_values:
            return self._pvs_prefix + self._family_name + ':' + propty
        else:
            raise Exception('invalid property name "' + propty + '"!')

    @property
    def properties_names(self):
        """Return tuple with properties names."""
        return MagnetPSDevice._properties_names

    @property
    def properties_values(self):
        """Return dictionary with current values of PS properties."""
        properties = _copy.deepcopy(self._properties_values)
        return properties

    @property
    def properties_database(self):
        """Return a dictionary with databases for all PS properties, with their current values."""
        database = {}
        for propty in self.properties_names:
            db = _copy.deepcopy(MagnetPSDevice._properties_database[propty])
            db['value'] = self._properties_values[propty]
            database[self._device_property(propty)] = db
        return database

    @property
    def connected(self):
        for propty in MagnetPSDevice._properties_names:
            pv_name = self.get_pv_name(propty)
            if not self._pvs_set[pv_name].connected:
                return False
        return True

    def add_callback(self, callback, index):
        self._callback_functions[index] = callback

    def __getitem__(self, key):

        if isinstance(key, str):
            return self._properties_values[key]
        elif isinstance(key, int):
            return self._properties_values[MagnetPSDevice._properties_names[key]]
        else:
            raise KeyError

    def __setitem__(self, key, value):
        if isinstance(key, str):
            pv_name = self.get_pv_name(key)
            self._properties_values[key] = value
            self._pvs_set[pv_name] = value
        elif isinstance(key, int):
            propty = MagnetPSDevice._properties_names[key]
            pv_name = self.get_pv_name(propty)
            self._properties_values[propty] = value
            self._pvs_set[pv_name] = value
        else:
            raise KeyError

    def _device_property(self, propty):
        if propty in self._properties_values:
            return self._family_name + ':' + propty
        else:
            raise Exception('invalid property name "' + propty + '"!')

    def _create_properties_dict(self):
        for propty in MagnetPSDevice._properties_names:
            self._properties_values[propty] = MagnetPSDevice._properties_database[propty]['value']

    def _add_all_pvs(self):
        for propty in MagnetPSDevice._properties_names:
            pv_name = self.get_pv_name(propty)
            self._pvs_set.add(pv_name, connection_timeout=self._connection_timeout)
            self._pvs_set[pv_name].add_callback(callback=self._pvs_callback, index=self._uuid)

    def _pvs_callback(self, pvname, value, **kwargs):
        names = _naming_system.split_name(pvname)
        propty = names['Property']
        propty_db = MagnetPSDevice._properties_database[propty]
        self._properties_values[propty] = value
        for index,function in self._callback_functions.items():
            function(family_name=self._family_name,
                     propty=propty,
                     value=value,
                     pvname=pvname,
                     **kwargs)


    def __del__(self):
        for propty in self._properties_values:
            pv_name = self.get_pv_name(propty)
            if pv_name in self._pvs_set: # the PV object may have been garbage collected previouslly.
                self._pvs_set[pv_name].remove_callback(index=self._uuid)
