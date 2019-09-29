"""Power Supply Module."""

from siriuspy.bsmp import SerialError as _SerialError


def _psupply_update_connected(func):
    # This gunctions decorates PSupply methods to keep track of connected status
    def new_update_func(obj, *args, **kwargs):
        try:
            response = func(obj, *args, **kwargs)
            setattr(obj, '_connected', True)
            return response
        except _SerialError:
            setattr(obj, '_connected', False)
            raise
    return new_update_func


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

    def update(self):
        """Update all power supply entities."""
        connected = True
        self.update_groups()
        connected &= self._connected
        self.update_variables()
        self._connected = connected

    def update_variables(self):
        """Update all variables."""
        return self.update_variables_in_group(group_id=0)
    @_psupply_update_connected
    def update_groups(self, groups=None):
        """."""
        # NOTE: implement!!!
        # self._psbsmp.query_list_of_group_of_variables()
        for group_id, var_ids in groups.items():
            self._groups[group_id] = var_ids

    @_psupply_update_connected
    def update_wfmref(self):
        """Update wfmref."""
        self._wfmref = self._psbsmp.wfmref_read

    @_psupply_update_connected
    def update_variables_in_group(self, group_id):
        """Update variables if a group."""
        ack, values = self._psbsmp.read_group_of_variables(group_id=group_id)
        if ack == self.psbsmp.CONST_BSMP.ACK_OK:
            var_ids = self._groups[group_id]
            for var_id, value in zip(var_ids, values):
                self._variables[var_id] = value
        return ack
