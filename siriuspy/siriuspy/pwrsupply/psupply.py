"""Power Supply Module."""

import time as _time
from copy import deepcopy as _dcopy
from siriuspy.bsmp import SerialError as _SerialError


def _psupply_update_connected(func):
    # This functions decorates PSupply methods to keep track of
    # connected status.
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
        self._curves = dict()
        self._wfmref = None
        self._wfmref_sp = None
        self._last_wfm_update = None

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
    def wfmref_sp(self):
        """Return wfmref_sp."""
        return self._wfmref_sp

    @wfmref_sp.setter
    def wfmref_sp(self, value):
        """Set wfmref_sp."""
        self._wfmref_sp = _dcopy(value)

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
    def update_groups(self, var_ids_list=None):
        """."""
        # NOTE: implement!!!
        # read variable groups from power supply
        # var_ids_list = self._psbsmp.query_list_of_group_of_variables()

        # stores groups definition
        for group_id, var_ids in enumerate(var_ids_list):
            self._groups[group_id] = var_ids

    @_psupply_update_connected
    def update_wfmref(self, interval=0.5):
        """Update wfmref."""
        # address = self._psbsmp.channel.address
        now = _time.time()
        # if address == 1:
        #     print('update_wfmref: {}'.format(now))
        if self._last_wfm_update is None or \
           (now - self._last_wfm_update) > interval:
            # t0 = _time.time()
            self._wfmref = self._psbsmp.wfmref_read()
            # t1 = _time.time()
            # if address == 1:
            #     print('wfmref_read took {:.1f} ms, @ time {:6f}'.format(
            #         1000*(t1-t0), now - 1570129351))
            self._last_wfm_update = now

    @_psupply_update_connected
    def update_variables_in_group(self, group_id):
        """Update variables if a group."""
        ack, values = self._psbsmp.read_group_of_variables(group_id=group_id)
        if ack == self.psbsmp.CONST_BSMP.ACK_OK:
            var_ids = self._groups[group_id]
            for var_id, value in zip(var_ids, values):
                self._variables[var_id] = value
        return ack
