

class GroupPVs:
    """Objects of this class represent grouped PVs"""

    def __init__(self, pv_names, pvs_set):
        """Create class object from given arguments.

        Arguments:
        pv_names -- iterable with names of PVs stored in 'pvs_set'
        pvs_set  -- a SiriusPVsSet object storing SiriusPV objects.
        """
        self._pv_names = tuple([item for item in pv_names])
        self._pvs_set = pvs_set

    @property
    def pv_names(self):
        """Return a tuple of strings representing PV grouped in the class object."""

        return self._pv_names

    @property
    def connected(self):
        """Return True if all grouped PVs are connected."""

        for prop, pv in self._pvs.items():
            if not pv.connected:
                return False
                return True

    def add_callback(self, callback, index):
        """Add callback function to all grouped PV.

        Arguments:
        callback -- reference to the callback function
        index    -- an immutable used as a key to the callback being added.
        """
        for pv_name in self._pv_names:
            self._pvs_set[pv_name].add_callback(callback=callback, index=index)

    def remove_callback(self, index):
        for pv_name in self._pv_names:
            self._pvs_set[pv_name].remove_callback(index=index)

    def __getitem__(self, key):
        """Return the SiriusPV object associated with the key argument.

        Arguments:
        key -- either a string PV name or an index into the tupple of PV names.
        """
        # maybe the implementation here could be more carefull: catch more
        # gracefully anomalous situations where pvs_set is inconsistent with
        # pv_names due to a (key,value) pair removed in another scope.
        if isinstance(key, str):
            return self._pvs_set[key]
        elif isinstance(key, int):
            return self._pvs_set[self._pv_names[key]]
        else:
            raise KeyError
