"""Deprecated module?!."""

#
# import uuid as _uuid
# import copy as _copy
# import siriuspy.csdevice as _csdevice
# from siriuspy.epics import SiriusPVsSet as _SiriusPVsSet
# from siriuspy import namesys as _namesys
# from siriuspy.search import PSSearch
#
#
# class MagnetPSDevice:
#     """Magnet Power Supply EPICS Device
#
#     This class represent magnet power supply EPICS devices.
#
#      with accessible
#     properties associated
#     with EPICS PVs that are grouped within the class for convenience.
#     """
#
#     _connection_timeout = None
#
#     def __init__(self, ps_name, pvsset=None,
#                  connection_timeout=_connection_timeout):
#
#         self._uuid = _uuid.uuid4()         # unique ID for the class object
#         self._ps_name = ps_name            # power supply device name
#         self._pstype_name = PSSearch.conv_psname_2_pstype(ps_name)
#         self._database = _csdevice.get_database(self._pstype_name)
#
#         if self._database is None:
#             print(self._ps_name, self._pstype_name)
#
#         self._pvsset = pvsset if pvsset else \
#               _SiriusPVsSet(connection_timeout=connection_timeout)
#         self._connection_timeout = connection_timeout
#         self._pv_names = {}  # property:pv_name dict
#         self._callback_functions = {}
#
#         self._insert_pvs_in_set()
#
#     @property
#     def ps_name(self):
#         return self._ps_name
#
#     @property
#     def pstype_name(self):
#         return self._pstype_name
#
#     @property
#     def properties(self):
#         """Return tuple with properties names."""
#         return [propty for propty in self._database]
#
#     @property
#     def database(self):
#         return _copy.deepcopy(self._database)
#
#     @property
#     def connected(self):
#         for pv_name in self._pv_names.values():
#             if not self._pvsset[pv_name].connected:
#                 return False
#         return True
#
#     def add_callback(self, callback, index):
#         self._callback_functions[index] = callback
#
#     def __getitem__(self, key):
#         if isinstance(key, str):
#             return self._database[key]['value']
#         else:
#             raise KeyError
#
#     def __setitem__(self, key, value):
#         if isinstance(key, str):
#             pv_name = self._pv_names[key]
#             self._pvsset[pv_name] = value
#             # eventual invocation of callback will synchronize self._database
#         else:
#             raise KeyError
#
#     def _insert_pvs_in_set(self):
#         for propty in self._database:
#             pv_name = self._ps_name + ':' + propty
#             self._pv_names[propty] = pv_name
#             self._pvsset.add(pv_name,
#                              connection_timeout=self._connection_timeout)
#             self._pvsset[pv_name].add_callback(
#                 callback=self._pvs_callback, index=self._uuid)
#
#     def _pvs_callback(self, pvname, value, **kwargs):
#         names = _namesys.split_name(pvname)
#         propty = names['propty']
#         self._database[propty]['value'] = value
#         for index,function in self._callback_functions.items():
#             function(family_name=self._family_name,
#                      propty=propty,
#                      value=value,
#                      pvname=pvname,
#                      **kwargs)
#
#     def __del__(self):
#         for propty in self._database:
#             pv_name = self._pv_names[propty]
#             # the PV object may have been garbage collected previouslly.
#             if pv_name in self._pvsset:
#                 self._pvsset[pv_name].remove_callback(index=self._uuid)
