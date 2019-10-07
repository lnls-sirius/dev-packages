"""Power Supply Module."""

import time as _time
import numpy as _np
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
        self._wfm_rb = None
        self._wfmref_mon = None
        self._wfm_mon = None
        self._timestamp_update = None
        self._timestamp_update_group = None
        self._timestamp_update_variables = None
        self._timestamp_update_wfm = None

    @property
    def psbsmp(self):
        """Return PSBSMP communication objetc."""
        return self._psbsmp

    @property
    def connected(self):
        """Return connection state."""
        return self._connected

    @property
    def wfm_rb(self):
        """Return wfm_rb."""
        return self._wfm_rb

    @wfm_rb.setter
    def wfm_rb(self, value):
        """Set wfm_rb."""
        self._wfm_rb = _np.array(value)

    @property
    def wfmref_mon(self):
        """Return wfmref."""
        return self._wfmref_mon

    @property
    def wfm_mon(self):
        """Return wfmref."""
        return self._wfm_mon

    @property
    def variables(self):
        """."""
        return self._variables

    def get_variable(self, var_id):
        """."""
        return self._variables[var_id]

    def update(self, interval=0.0):
        """Update all power supply entities.
        Does not update groups of variables.
        """
        now = _time.time()
        tstamp = self._timestamp_update
        if tstamp is None or (now - tstamp) > interval:
            connected = True
            # variables
            if not self.update_variables():
                return False
            connected &= self._connected
            # wfmref
            if not self.update_wfm():
                return False
            connected &= self._connected
            # update connected state
            self._connected = connected
            if connected:
                self._timestamp_update = now
        return True

    @_psupply_update_connected
    def update_groups(self, interval=0.0):
        """."""
        now = _time.time()
        tstamp = self._timestamp_update_group
        if tstamp is None or (now - tstamp) >= interval:
            ack, groupsinfo = self._psbsmp.query_list_of_group_of_variables()
            if ack == self.psbsmp.CONST_BSMP.ACK_OK:
                for i in range(len(groupsinfo)):
                    ack, var_ids = \
                        self._psbsmp.query_group_of_variables(group_id=i)
                    if ack == self.psbsmp.CONST_BSMP.ACK_OK:
                        self._groups[i] = var_ids
                    else:
                        return False
            else:
                return False
            self._timestamp_update_group = now
        return True

    @_psupply_update_connected
    def update_variables(self, interval=0.0):
        """Update all variables."""
        now = _time.time()
        tstamp = self._timestamp_update_variables
        if tstamp is None or (now - tstamp) >= interval:
            group_id = self._psbsmp.CONST_BSMP.ID_STD_GROUP_ALL
            ack, values = self._psbsmp.read_group_of_variables(
                group_id=group_id)
            if ack == self.psbsmp.CONST_BSMP.ACK_OK:
                # update _variables with data read from device
                if group_id not in self._groups:
                    return False
                var_ids = self._groups[group_id]
                for var_id, value in zip(var_ids, values):
                    self._variables[var_id] = value
                # update timestamp
                self._timestamp_update_variables = now
            else:
                return False
        return True

    @_psupply_update_connected
    def update_wfm(self, interval=0.0):
        """Update wfmref."""
        now = _time.time()
        tstamp = self._timestamp_update_wfm
        if tstamp is None or (now - tstamp) >= interval:
            # update wfmref_mon
            wfmref_mon = self._psbsmp.wfmref_mon_read()
            if wfmref_mon is None:
                return False
            self._wfmref_mon = wfmref_mon
            # update wfm_mon
            wfm_mon = self._psbsmp.wfm_mon_read()
            if wfm_mon is not None:
                self._wfm_mon = wfm_mon
                # NOTE: a successful read means bufsample is not
                # currently being filled by DSP. Therefore an issue
                # of a bufsample enable command is in order!
                self._psbsmp.wfmref_mon_bufsample_enable()
            # update timestamp
            self._timestamp_update_wfm = now
        return True

    def reset_variables_groups(self, groups):
        """."""
        # checks groups in dictionary
        # NOTE: this is a legacy check, for PRUcontroller.
        # it can be relaxed in the future.
        group_ids = sorted(groups.keys())
        if len(group_ids) < 3:  # needs to have all default groups
            return False
        for i in range(len(group_ids)):  # consecutive?
            if i not in group_ids:
                return False

        # create list of variable ids
        varids_groups = [groups[gid] for gid in group_ids]

        # reset groups of variables for all bsmp devices
        self._psbsmp.reset_groups_of_variables(
            varids_groups[3:], add_wfmref_group=True)

        return True
