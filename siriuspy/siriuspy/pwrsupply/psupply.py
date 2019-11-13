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

    DEFAULT_UPDATE_INTERVAL_WFM = 2.0  # [s]
    DEFAULT_UPDATE_INTERVAL_VARIABLES = 0.1  # [s]
    DEFAULT_UPDATE_INTERVAL_PARAMETERS = 2.0  # [s]

    def __init__(self, psbsmp):
        """Init."""
        self._psbsmp = psbsmp
        self._connected = None
        self._groups = self._init_groups()
        self._variables = self._init_variables()
        self._curves = self._init_curves()
        self._parameters = self._init_parameters()
        self._wfm_rb = None
        self._wfmref_mon = None
        self._wfm_mon = None
        self._timestamp_update = None
        self._timestamp_update_group = None
        self._timestamp_update_variables = None
        self._timestamp_update_wfm = None
        self._timestamp_update_parameters = None


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
    def wfmref_mon_index(self):
        """Return current index into DSP selected curve."""
        curve_id = \
            self._variables[self._psbsmp.CONST.V_WFMREF_SELECTED]
        if curve_id == 0:
            beg = self._variables[
                self._psbsmp.CONST.V_WFMREF0_START]
            end = self._variables[
                self._psbsmp.CONST.V_WFMREF0_END]
        else:
            beg = self._variables[
                self._psbsmp.CONST.V_WFMREF1_START]
            end = self._variables[
                self._psbsmp.CONST.V_WFMREF1_END]
        index = self._psbsmp.curve_index_calc(beg, end)
        return index

    @property
    def wfm_mon(self):
        """Return wfmref."""
        return self._wfm_mon

    @property
    def variables(self):
        """."""
        return self._variables

    @property
    def parameters(self):
        """."""
        return self._parameters

    @property
    def timestamp_update(self):
        """Return timestamp of last power supply update."""
        tstamps = (
            self._timestamp_update,
            self._timestamp_update_group,
            self._timestamp_update_variables,
            self._timestamp_update_wfm)
        maxtstamp = max(val if val is not None else 0 for val in tstamps)
        return maxtstamp

    def get_variable(self, var_id):
        """."""
        return self._variables[var_id]

    def get_parameter(self, eid):
        """."""
        return self._parameters[eid]

    def update(self, interval=0.0):
        """Update all power supply entities.

        Method does not update groups of variables.
        """
        now = _time.time()
        tstamp = self._timestamp_update
        if tstamp is None or (now - tstamp) > interval:
            connected = True
            # variables
            if not self.update_variables(interval=0.0):
                return False
            connected &= self._connected
            # wfmref
            if not self.update_wfm(interval=0.0):
                return False
            connected &= self._connected
            # parameters
            if not self.update_parameters(interval=0.0):
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
    def update_variables(self, interval=None):
        """Update all variables."""
        if interval is None:
            interval = PSupply.DEFAULT_UPDATE_INTERVAL_VARIABLES
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
    def update_wfm(self, interval=None):
        """Update wfmref."""
        if self._psbsmp.IS_DCLINK:
            return True
        if interval is None:
            interval = PSupply.DEFAULT_UPDATE_INTERVAL_WFM
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
            # update timestamp (even it could not read wfm_mon)
            self._timestamp_update_wfm = now
        return True

    @_psupply_update_connected
    def update_parameters(self, interval=None):
        """Update power supply parameters."""
        if interval is None:
            interval = PSupply.DEFAULT_UPDATE_INTERVAL_PARAMETERS
        now = _time.time()
        tstamp = self._timestamp_update_parameters
        if tstamp is None or (now - tstamp) >= interval:
            parameters = self._psbsmp.entities.parameters
            for eid in parameters.eids:
                parameter = parameters[eid]
                counter = parameter['count']
                if eid != self._psbsmp.CONST.P_PS_NAME and counter > 1:
                    value = _np.zeros(counter) * float('NaN')
                    for idx in range(counter):
                        value[idx] = self._psbsmp.parameter_read(eid, idx)
                else:
                    value = self._psbsmp.parameter_read(eid)
                self._parameters[eid] = value
                # print(eid, value)
            if value is not None:
                self._timestamp_update_variables = now
                return True
            else:
                return False
        return True

    def reset_variables_groups(self, groups):
        """."""
        # reset groups of variables for all bsmp devices
        ack, _ = self._psbsmp.reset_groups_of_variables(
            groups[3:], add_wfmref_group=True)
        if ack != self.psbsmp.CONST_BSMP.ACK_OK:
            ValueError('Could not reset groups of variables!')
        return True

    def _init_groups(self):
        return dict()

    def _init_variables(self):
        return dict()

    def _init_curves(self):
        return dict()

    def _init_parameters(self):
        """Init power supply parameters."""
        parameters = self._psbsmp.entities.parameters
        parameters_values = dict()
        for eid in parameters.eids:
            if eid == 0:
                parameters_values[eid] = ''
            else:
                parameter = parameters[eid]
                counter = parameter['count']
                value = _np.zeros(counter) * float('NaN')
                parameters_values[eid] = value
        return parameters_values
