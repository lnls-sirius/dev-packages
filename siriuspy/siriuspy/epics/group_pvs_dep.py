import copy as _copy
from .group_pvs import GroupPVs as _GroupPVs
import uuid as _uuid

class GroupPVsDep:
    """Object class that manages dependence of a PV database on a group of other PVs."""

    def __init__(self, pv_database, group_pvs):

        self._group_pvs = group_pvs
        self._pv_database = pv_database
        self._set_callback_flag = False
        self._id = _uuid.uuid4()

    @property
    def update_pv_database(self):
        """Method with the recipe of how to update the PV database from the group PVs current state.

        This is an abstract (pure) virtual method that has to be implemented in the derived class.
        It should update 'self._pv_database' according to current state of 'self._group_pvs'.
        This function is invoked automatically everytime a primitive PV changes its value.
        """
        raise NotImplemented

    @property
    def pv_database(self):
        """Return a copy of the current PV database"""
        if not self._set_callback_flag:
            raise Exception('set_pvs_callback not invoked yet!')
        return _copy.deepcopy(self._pv_database) # deepcopy maybe be necessary

    @property
    def connected(self):
        """Return True if all primitive PVs are connected."""
        return self._group_pvs.connected

    @property
    def value(self):
        """Return current value of PV database."""
        if not self._set_callback_flag:
            raise Exception('set_pvs_callback not invoked yet!')
        return self._pv_database['value']

    def set_pvs_callback(self):
        self._set_callback_flag = True
        self._group_pvs.add_callback(callback=self._update_pv_database, index=self._id)


    def __del__(self):
        if self._set_callback_flag:
            self._group_pvs.remove_callback(index=self._id)
