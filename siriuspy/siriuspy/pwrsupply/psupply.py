"""Power Supply Module."""


class PSupply:
    """Power Supply.

    Contains the state of a BSMP power supply.
    """

    def __init__(self, psbsmp):
        """Init."""
        self._psbsmp = psbsmp
        self._connected = None
        self._groups = dict()
        self._variables = dict()
        self._wfmref = None

    @property
    def psbsmp(self):
        """Return PSBSMP communication objetc."""
        return self._psbsmp

    @property
    def connected(self):
        """Return connection state."""
        return self._connected

    @property
    def wfmref(self):
        """Return wfmref."""
        return self._wfmref

    @property
    def variables(self):
        """."""
        return self._variables

    def get_variable(self, var_id):
        """."""
        return self._variables[var_id]

    def update_groups(self, groups):
        """."""
        self._connected = False
        # NOTE: implement!!!
        # self._psbsmp.query_list_of_group_of_variables()
        for group_id, var_ids in groups.items():
            self._groups[group_id] = var_ids
        self._connected = True

    def update_wfmref(self):
        """Update wfmref."""
        self._connected = False
        self._wfmref = self._psbsmp.wfmref_read
        self._connected = True

    def update_variables_in_group(self, group_id):
        """Update variables if a group."""
        self._connected = False
        ack, values = self._psbsmp.read_group_of_variables(group_id=group_id)
        if ack == self.psbsmp.CONST_BSMP.ACK_OK:
            self._connected = True
            var_ids = self._groups[group_id]
            for var_id, value in zip(var_ids, values):
                self._variables[var_id] = value
        return ack
