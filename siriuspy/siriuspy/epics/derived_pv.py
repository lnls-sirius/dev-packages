from .group_pvs import GroupPVs as _GroupPVs

class DerivedPV:

    def __init__(self, group_pvs, pv_database):

        self._group_pvs = group_pvs
        self._pv_database = pv_database

    @property
    def update(self):
        """This is an abstract (pure) virtual method that has to be implemented in the derived class.
           It should update 'self._pv_database' according to current state of 'self._group_pvs' """
        raise NotImplemented

    @property
    def group_pvs(self):
        return self._group_pvs

    @property
    def pv_database(self):
        return _copy.deepcopy(self._pv_database) # deepcopy maybe be necessary

    @property
    def connected(self):
        return self._group_pvs.connected


    def disconnect(self):
        self._group_pvs.disconnect()

    def __del__(self):
        self.disconnect()
