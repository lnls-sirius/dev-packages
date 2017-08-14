#!/usr/local/bin/python-sirius
"""PulsedPowerSupply definition."""
from epics import Device

from siriuspy import envars
from siriuspy.pulsedps import properties
from siriuspy.pulsedps.data import PUData as _PUData


class PulsedPowerSupply:
    """Class to communicate with a pulsed power supply via epics."""

    def __init__(self, psname, use_vaca=False, vaca_prefix=""):
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
                "\t{:16s} - {}\n"
                "\t{:16s} - {})"
                ).format(properties.CtrlMode, self.ctrlmode_mon,
                         properties.PwrStateSel, self.pwrstate_sel,
                         properties.PwrStateSts, self.pwrstate_sts,
                         properties.EnablePulsesSel, self.enablepulses_sel,
                         properties.EnablePulsesSts, self.enablepulses_sts,
                         properties.ResetCmd, self.reset_cmd,
                         properties.ExternalInterlock, self.intlk_mon,
                         properties.TensionSP, self.tension_sp,
                         properties.TensionRB, self.tension_rb,
                         properties.TensionRefMon, self.tensionref_mon,
                         properties.TensionMon, self.tension_mon)

    def add_callback_to_pv(self, attr, func):
        """Add func as a callback to given attribute."""
        if callable(func):
            self._controller.add_callback(attr, func)
        else:
            raise AssertionError("Callback must be a callable type.")

    def add_callback(self, func):
        """Register a callback."""
        if callable(func):
            self._callback = func
        else:
            raise AssertionError("Callback must be a callable type.")

    @property
    def tension_sp(self):
        """Return tension_sp."""
        return self._controller.get(properties.TensionSP)

    @tension_sp.setter
    def tension_sp(self, value):
        self._controller.put(properties.TensionSP, value)

    @property
    def tension_rb(self):
        """Return tension_rb."""
        return self._controller.get(properties.TensionRB)

    @property
    def tensionref_mon(self):
        """Return tension ref mon."""
        return self._controller.get(properties.TensionRefMon)

    @property
    def tension_mon(self):
        """Return tension mon."""
        return self._controller.get(properties.TensionMon)

    @property
    def pwrstate_sel(self):
        """Return power state sel value."""
        return self._controller.get(properties.PwrStateSel)

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        self._controller.put(properties.PwrStateSel, value)

    @property
    def pwrstate_sts(self):
        """Return power state status."""
        return self._controller.get(properties.PwrStateSts)

    @property
    def enablepulses_sel(self):
        """Return setpoint for pulses enabled."""
        return self._controller.get(properties.EnablePulsesSel)

    @enablepulses_sel.setter
    def enablepulses_sel(self, value):
        self._controller.put(properties.EnablePulsesSel, value)

    @property
    def enablepulses_sts(self):
        """Return wether pulses are enabled or not."""
        return self._controller.get(properties.EnablePulsesSts)

    @property
    def reset_cmd(self):
        """Return number of reset commands issued."""
        return self._controller.get(properties.ResetCmd)

    @reset_cmd.setter
    def reset_cmd(self, value):
        self._controller.put(properties.ResetCmd, value)

    @property
    def intlk_mon(self):
        """Return interlock mask."""
        return self._controller.get(properties.ExternalInterlock)

    @property
    def ctrlmode_mon(self):
        """Return control mode."""
        return self._controller.get(properties.CtrlMode)

    @property
    def database(self):
        """Return pulsed ps database as a dict."""
        return self._get_database()

    # Private methods
    def _get_database(self):
        db = self._data.propty_database

        db[properties.PwrStateSel]["value"] = self.pwrstate_sel
        db[properties.PwrStateSts]["value"] = self.pwrstate_sts
        db[properties.EnablePulsesSel]["value"] = self.enablepulses_sel
        db[properties.EnablePulsesSts]["value"] = self.enablepulses_sts
        db[properties.ResetCmd]["value"] = self.reset_cmd
        db[properties.CtrlMode]["value"] = self.ctrlmode_mon
        db[properties.ExternalInterlock]["value"] = self.intlk_mon
        db[properties.TensionSP]["value"] = self.tension_sp
        db[properties.TensionRB]["value"] = self.tension_rb
        db[properties.TensionRefMon]["value"] = self.tensionref_mon
        db[properties.TensionMon]["value"] = self.tension_mon

        return db

    def _set_vaca_prefix(self, use_vaca, vaca_prefix):
        self._vaca_prefix = ""
        if use_vaca:
            if vaca_prefix:
                self._vaca_prefix = vaca_prefix
            else:
                self._vaca_prefix = envars.vaca_prefix

    def _init_data(self):
        self._data = _PUData(self._psname)

    def _init_controller(self):
        self._controller = Device(prefix=self._prefix, delim=":",
                                  attrs=properties.PulsedPowerSupplyAttrs)


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
        self._tension_sp = 0
        self._tension_rb = 0
        self._tensionref_mon = 0
        self._tension_mon = 0
        self._pwrstate_sel = 0
        self._pwrstate_sts = 0
        self._enablepulses_sel = 0
        self._enablepulses_sts = 0
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
    def tension_sp(self):
        """Return tension_sp."""
        return self._get_tension_sp()

    @tension_sp.setter
    def tension_sp(self, value):
        self._set_tension_sp(value)

    @property
    def tension_rb(self):
        """Return tension_rb."""
        return self._get_tension_rb()

    @property
    def tensionref_mon(self):
        """Return tension ref mon."""
        return self._get_tensionref_mon()

    @property
    def tension_mon(self):
        """Return tension mon."""
        return self._get_tension_mon()

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
    def enablepulses_sel(self):
        """Return setpoint for pulses enabled."""
        return self._get_enable_pulses_sel()

    @enablepulses_sel.setter
    def enablepulses_sel(self, value):
        self._set_enable_pulses_sel(value)

    @property
    def enablepulses_sts(self):
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
    def _get_tension_sp(self):
        return self._tension_sp

    def _set_tension_sp(self, value):
        if not self._reset_issued:
            self._tension_sp = value
            self._issue_callback(properties.TensionSP, value)
        self._tension_rb = value
        self._issue_callback(properties.TensionRB, value)
        self._set_tensionref_mon(value)
        self._set_tension_mon(value)

    def _get_tension_rb(self):
        return self._tension_rb

    def _set_tension_rb(self, value):
        # Will be implemented by PS
        self._tension_rb = value

    def _get_tensionref_mon(self):
        return self._tensionref_mon

    def _set_tensionref_mon(self, value):
        if self._ctrlmode_mon == 0 and \
                self._pwrstate_sts == 1 or \
                self._reset_issued:
            max_tension = \
                self._data.propty_database[properties.TensionRefMon]["hihi"]
            if value > max_tension:
                value = max_tension

            self._tensionref_mon = value
            self._issue_callback(properties.TensionRefMon, value)

    def _get_tension_mon(self):
        return self._tension_mon

    def _set_tension_mon(self, value):
        if self._ctrlmode_mon == 0 and \
                self._pwrstate_sts == 1 or \
                self._reset_issued:
            max_tension = \
                self._data.propty_database[properties.TensionRefMon]["hihi"]
            if value > max_tension:
                value = max_tension

            self._tension_mon = value
            self._issue_callback(properties.TensionMon, value)

    def _get_pwrstate_sel(self):
        return self._pwrstate_sts

    def _set_pwrstate_sel(self, value):
        if not self._reset_issued:
            self._pwrstate_sel = value
            self._issue_callback(properties.PwrStateSel, value)
        self._set_pwrstate_sts(value)

    def _get_pwrstate_sts(self):
        return self._pwrstate_sel

    def _set_pwrstate_sts(self, value):
        if self._ctrlmode_mon == 0 or \
                self._reset_issued:
            self._pwrstate_sts = value
            self._issue_callback(properties.PwrStateSts, value)
            if value == 1:
                self._set_tensionref_mon(self.tension_sp)
                self._set_tension_mon(self.tension_sp)
            else:
                self._set_tensionref_mon(0)
                self._set_tension_mon(0)

    def _get_enable_pulses_sts(self):
        return self._enablepulses_sts

    def _set_enable_pulses_sel(self, value):
        if not self._reset_issued:
            self._enablepulses_sel = value
            self._issue_callback(properties.EnablePulsesSel, value)
        self._set_enable_pulses_sts(value)

    def _get_enable_pulses_sel(self):
        return self._enablepulses_sel

    def _set_enable_pulses_sts(self, value):
        if self._ctrlmode_mon == 0 and \
                self._pwrstate_sts == 1 or \
                self._reset_issued:
            self._enablepulses_sts = value
            self._issue_callback(properties.EnablePulsesSts, value)

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
        self._issue_callback(properties.ResetCmd, self._reset_cmd)

        self.tension_sp = 0
        self.pwrstate_sel = 0
        self.enablepulses_sel = 0
        self._set_intlk_mon(0)

    def _get_intlk_mon(self):
        return self._intlk_mon

    def _set_intlk_mon(self, value):
        self._intlk_mon = 0
        self._issue_callback(properties.ExternalInterlock, value)

    def _get_ctrlmode_mon(self):
        return self._ctrlmode_mon

    def _issue_callback(self, attr, value):
        if self._callback:
            pv = self._psname + ":" + attr
            self._callback(pv, value)
