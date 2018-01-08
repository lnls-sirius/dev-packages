#!/usr/local/bin/python-sirius
"""PulsedPowerSupply definition."""
import numpy as _np
from siriuspy.pwrsupply.data import PSData as _PSData


class PulsedPowerSupplySim:
    """Simulation of a pulsed power supply."""

    def __init__(self, psname):
        """Class constructor.

        Input:
            a pulsed power supply name
        """
        self._psname = psname
        self._data = _PSData(self._psname)
        # Properties
        self._voltage_sp = 0
        self._voltage_rb = 0
        self._voltage_mon = 0
        self._pwrstate_sel = 0
        self._pwrstate_sts = 0
        self._pulsed_sel = 0
        self._pulsed_sts = 0
        self._reset_cmd = 0
        self._intlk_mon = 0
        self._ctrlmode_mon = 0

        self._callback = None
        self._reset_issued = False

    # Public interface
    def add_callback(self, func):
        """Add a callback to be called when pv changes."""
        self._callback = func

    @property
    def voltage_sp(self):
        """Return voltage_sp."""
        return self._get_voltage_sp()

    @voltage_sp.setter
    def voltage_sp(self, value):
        self._set_voltage_sp(value)

    @property
    def voltage_rb(self):
        """Return voltage_rb."""
        return self._get_voltage_rb()

    @property
    def voltage_mon(self):
        """Return voltage mon."""
        return self._get_voltage_mon()

    @property
    def pwrstate_sel(self):
        """Return power state sel value."""
        return self._get_pwrstate_sel()

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        self._set_pwrstate_sel(value)

    @property
    def pwrstate_sts(self):
        """Return power state status."""
        return self._get_pwrstate_sts()

    @property
    def pulsed_sel(self):
        """Return setpoint for pulses enabled."""
        return self._get_enable_pulses_sel()

    @pulsed_sel.setter
    def pulsed_sel(self, value):
        self._set_enable_pulses_sel(value)

    @property
    def pulsed_sts(self):
        """Return wether pulses are enabled or not."""
        return self._get_enable_pulses_sts()

    @property
    def reset(self):
        """Return number of reset commands issued."""
        return self._get_reset()

    @reset.setter
    def reset(self, value):
        self._set_reset(value)

    @property
    def intlk_mon(self):
        """Return interlock mask."""
        return self._get_intlk_mon()

    @property
    def intlklabels_cte(self):
        """Return interlock labels."""
        return self._get_intlk_labels()

    @property
    def ctrlmode_mon(self):
        """Return control mode."""
        return self._get_ctrlmode_mon()

    @property
    def database(self):
        """Return pulsed ps database as a dict."""
        return self._data.propty_database

    # Private methods
    def _get_voltage_sp(self):
        return self._voltage_sp

    def _set_voltage_sp(self, value):
        if not self._reset_issued:
            self._voltage_sp = value
            self._issue_callback('Voltage-SP', value)
        # self._voltage_rb = value
        # self._issue_callback('Voltage-RB', value)
        # self._set_voltageref_mon(value)
        self._set_voltage_rb(value)
        self._set_voltage_mon(value)

    def _get_voltage_rb(self):
        return self._voltage_rb

    def _set_voltage_rb(self, value):
        # Will be implemented by PS
        # self._voltage_rb = value
        if self._ctrlmode_mon == 0 or \
                self._reset_issued:
            max_voltage = \
                self._data.propty_database['Voltage-RB']["hihi"]
            # print(self._data.propty_database)
            if value > max_voltage:
                value = max_voltage

            self._voltage_rb = value
            self._issue_callback('Voltage-RB', value)

    def _get_voltage_mon(self):
        return self._voltage_mon

    def _set_voltage_mon(self, value):
        if self._ctrlmode_mon == 0 and \
                self._pwrstate_sts == 1 or \
                self._reset_issued:
            max_voltage = \
                self._data.propty_database['Voltage-Mon']["hihi"]
            if value > max_voltage:
                value = max_voltage

            self._voltage_mon = value
            self._issue_callback('Voltage-Mon', value)

    def _get_pwrstate_sel(self):
        return self._pwrstate_sel

    def _set_pwrstate_sel(self, value):
        if not self._reset_issued:
            self._pwrstate_sel = value
            self._issue_callback('PwrState-Sel', value)
        self._set_pwrstate_sts(value)

    def _get_pwrstate_sts(self):
        return self._pwrstate_sts

    def _set_pwrstate_sts(self, value):
        if self._ctrlmode_mon == 0 or \
                self._reset_issued:
            if value == 1:
                self._pwrstate_sts = value
                self._set_voltage_mon(self.voltage_sp)
            else:
                self._set_voltage_mon(0)
                self._pwrstate_sts = value
            self._issue_callback('PwrState-Sts', value)

    def _get_enable_pulses_sts(self):
        return self._pulsed_sts

    def _set_enable_pulses_sel(self, value):
        if not self._reset_issued:
            self._pulsed_sel = value
            self._issue_callback('Pulsed-Sel', value)
        self._set_enable_pulses_sts(value)

    def _get_enable_pulses_sel(self):
        return self._pulsed_sel

    def _set_enable_pulses_sts(self, value):
        if self._ctrlmode_mon == 0 and \
                self._pwrstate_sts == 1 or \
                self._reset_issued:
            self._pulsed_sts = value
            self._issue_callback('Pulsed-Sts', value)

    def _get_reset(self):
        return self._reset_cmd

    def _set_reset(self, value):
        self._reset_cmd += 1
        if self.ctrlmode_mon == 1:  # Local mode
            return
        self._reset_issued = True
        self._reset()
        self._reset_issued = False

    def _reset(self):
        self._issue_callback('Reset-Cmd', self._reset_cmd)

        self.voltage_sp = 0
        self.pwrstate_sel = 0
        self.pulsed_sel = 0
        self._set_intlk_mon(0)

    def _get_intlk_mon(self):
        return self._intlk_mon

    def _set_intlk_mon(self, value):
        self._intlk_mon = 0
        self._issue_callback('Intlk-Mon', value)

    def _get_intlk_labels(self):
        return _np.array(
            ['Bit 0', 'Bit 1', 'Bit 2', 'Bit 3', 'Bit 4', 'Bit 5'])

    def _get_ctrlmode_mon(self):
        return self._ctrlmode_mon

    def _issue_callback(self, attr, value):
        if self._callback:
            pv = self._psname + ":" + attr
            self._callback(pv, value)
