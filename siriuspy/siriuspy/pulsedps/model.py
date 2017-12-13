#!/usr/local/bin/python-sirius
"""PulsedPowerSupply definition."""
import logging as _logging
from epics import PV as _PV

from siriuspy import envars as _envars
from siriuspy.pulsedps.data import PUData as _PUData

_logging.basicConfig(level=_logging.WARNING)


class PulsedPowerSupply:
    """Class to communicate with a pulsed power supply via epics."""

    def __init__(self, psname, use_vaca=False, vaca_prefix="", lock=True):
        """Class constructor.

        Input:
            a pulsed power supply name
            whether to add a vaca prefix or not
            optional vaca prefix; username and hostname will be used otherwise
        """
        self._set_vaca_prefix(use_vaca, vaca_prefix)

        self._psname = psname
        self._prefix = self._vaca_prefix + self._psname

        self._init_data()
        self._init_controller()

    def __repr__(self):
        """Overload repr func."""
        return ("PulsedPowerSupply(\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {:b}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {})"
                ).format('CtrlMode-Mon', self.ctrlmode_mon,
                         'PwrState-Sel', self.pwrstate_sel,
                         'PwrState-Sts', self.pwrstate_sts,
                         'Pulsed-Sel', self.pulsed_sel,
                         'Pulsed-Sts', self.pulsed_sts,
                         'Reset-Cmd', self.reset_cmd,
                         'Intlk-Mon', self.intlk_mon,
                         'Voltage-SP', self.voltage_sp,
                         'Voltage-RB', self.voltage_rb,
                         'Voltage-Mon', self.voltage_mon)

    def add_callback_to_pv(self, attr, func):
        """Add func as a callback to given attribute."""
        if callable(func):
            self._controller[attr].add_callback(func)
        else:
            raise AssertionError("Callback must be a callable type.")

    def add_callback(self, func):
        """Register a callback."""
        if callable(func):
            self.callback = func
        else:
            raise AssertionError("Callback must be a callable type.")

    def read(self, controller, attr):
        """Do not hang."""
        # print("Connected?: ", attr, controller[attr].connected)
        if controller[attr].connected:
            return controller[attr].get()
        else:
            _logging.warning("Failed to get value for {}".format(attr))

    def write(self, controller, attr, value):
        """Do not hang."""
        if controller[attr].connected:
            return controller[attr].put(value)
        else:
            _logging.warning("Failed to write to {}".format(attr))

    @property
    def voltage_sp(self):
        """Return voltage_sp."""
        return self.read(self._controller, 'Voltage-SP')

    @voltage_sp.setter
    def voltage_sp(self, value):
        upper_limit = self._db['Voltage-SP']["hilim"]
        lower_limit = self._db['Voltage-SP']["lolim"]
        if value > upper_limit:
            value = upper_limit
        elif value < lower_limit:
            value = lower_limit
        self.write(self._controller, 'Voltage-SP', value)

    @property
    def voltage_rb(self):
        """Return voltage_rb."""
        return self._controller['Voltage-RB'].get()

    @property
    def voltage_mon(self):
        """Return voltage mon."""
        return self._controller['Voltage-Mon'].get()

    @property
    def pwrstate_sel(self):
        """Return power state sel value."""
        # return self._controller['PwrState-Sel'].get()
        return self.read(self._controller, 'PwrState-Sel')

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        # self._controller['PwrState-Sel'].put(value)
        self.write(self._controller, 'PwrState-Sel', value)

    @property
    def pwrstate_sts(self):
        """Return power state status."""
        return self._controller['PwrState-Sts'].get()

    @property
    def pulsed_sel(self):
        """Return setpoint for pulses enabled."""
        return self.read(self._controller, 'Pulsed-Sel')
        # return self._controller['Pulsed-Sel'].get()

    @pulsed_sel.setter
    def pulsed_sel(self, value):
        # self._controller['Pulsed-Sel'].put(value)
        self.write(self._controller, 'Pulsed-Sel', value)

    @property
    def pulsed_sts(self):
        """Return wether pulses are enabled or not."""
        return self._controller['Pulsed-Sts'].get()

    @property
    def reset_cmd(self):
        """Return number of reset commands issued."""
        return self.read(self._controller, 'Reset-Cmd')
        # return self._controller['Reset-Cmd'].get()

    @reset_cmd.setter
    def reset_cmd(self, value):
        # self._controller['Reset-Cmd'].put(value)
        self.write(self._controller, 'Reset-Cmd', value)

    @property
    def intlk_mon(self):
        """Return interlock mask."""
        return self._controller['Intlk-Mon'].get()

    @property
    def ctrlmode_mon(self):
        """Return control mode."""
        return self._controller['CtrlMode-Mon'].get()

    @property
    def database(self):
        """Return pulsed ps database as a dict."""
        return self._get_database()

    # Private methods
    def _get_database(self):
        for attr in ('Kick-SP', 'Kick-RB', 'Kick-Mon'):
            value = self.read(self._controller, attr)
            if value is not None:
                self._db[attr]["value"] = value

        return self._db

    def _set_vaca_prefix(self, use_vaca, vaca_prefix):
        self._vaca_prefix = ""
        if use_vaca:
            if vaca_prefix:
                self._vaca_prefix = vaca_prefix
            else:
                self._vaca_prefix = _envars.vaca_prefix

    def _init_data(self):
        self._data = _PUData(self._psname)
        self._db = self._get_db()

    def _get_db(self):
        return self._data.propty_database

    def _init_controller(self):
        self._controller = {}
        attrs = list(self._db.keys()) + ['Kick-SP', 'Kick-RB', 'Kick-Mon']
        for attr in attrs:
            self._controller[attr] = _PV(
                self._vaca_prefix + self._psname + ":" + attr)


class PulsedPowerSupplySim:
    """Simulation of a pulsed power supply."""

    def __init__(self, psname):
        """Class constructor.

        Input:
            a pulsed power supply name
        """
        self._psname = psname
        self._data = _PUData(self._psname)
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
        return self._get_reset_cmd()

    @reset.setter
    def reset(self, value):
        self._set_reset(value)

    @property
    def intlk_mon(self):
        """Return interlock mask."""
        return self._get_intlk_mon()

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
        self._voltage_rb = value
        self._issue_callback('Voltage-RB', value)
        self._set_voltageref_mon(value)
        self._set_voltage_mon(value)

    def _get_voltage_rb(self):
        return self._voltage_rb

    def _set_voltage_rb(self, value):
        # Will be implemented by PS
        self._voltage_rb = value

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
        return self._pwrstate_sts

    def _set_pwrstate_sel(self, value):
        if not self._reset_issued:
            self._pwrstate_sel = value
            self._issue_callback('PwrState-Sel', value)
        self._set_pwrstate_sts(value)

    def _get_pwrstate_sts(self):
        return self._pwrstate_sel

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
        if self.ctrlmode_mon == 1:  # Local mode
            return
        self._reset_issued = True
        self._reset()
        self._reset_issued = False

    def _reset(self):
        self._reset_cmd += 1
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

    def _get_ctrlmode_mon(self):
        return self._ctrlmode_mon

    def _issue_callback(self, attr, value):
        if self._callback:
            pv = self._psname + ":" + attr
            self._callback(pv, value)
