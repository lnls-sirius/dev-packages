"""Class to handle pulsed magnets."""
import re as _re
from threading import Thread

from epics import Device

from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.model import DipoleNormalizer
from siriuspy.pulsedps.model import PulsedPowerSupply
from siriuspy.pulsedps import properties as pu_props
from siriuspy.pulsedma import properties as pm_props
from siriuspy.pulsedma.data import PMData as _PMData


class PulsedMagnetNormalizer:
    """Calculate normalize tensions for pulsed magnets."""

    def __init__(self, maname, dipole_name, left="linear", right="linear"):
        """Class constructor."""
        self._maname = maname
        self._data = _PMData(self._maname)
        self._dipole = DipoleNormalizer(dipole_name, left=left, right=right)
        self._left = left
        self._right = right
        self._magfunc = self._data.magfunc(self._data.psnames[0])
        self._mfmult = _mutil.get_magfunc_2_multipole_dict()[self._magfunc]

    # Public interface
    def conv_tension_2_strength(self, tension, current_dipole):
        """Normalize tension into kick."""
        # Get integrated field
        intfield = self._conv_tension_2_intfield(tension)
        # Get magnetic rigidity
        brho = self._dipole._get_brho(current_dipole)
        try:
            return intfield/brho
        except ZeroDivisionError:
            return 0

    def conv_strength_2_tension(self, strength, current_dipole):
        """Denormalize the strength returning the tension."""
        intfield = self._conv_strength_2_intfield(strength, current_dipole)
        mf = self._mfmult
        excdata = self._data.excdata(self._data.psnames[0])
        tension = excdata.interp_mult2curr(intfield, mf["harmonic"],
                                           mf["type"], left=self._left,
                                           right=self._right)
        return tension

    # Private methods
    def _conv_tension_2_multipoles(self, tension):
        msum = {}
        excdata = self._data.excdata(self._data.psnames[0])
        m = excdata.interp_curr2mult(
            tension, left=self._left, right=self._right)
        msum = _mutil.sum_magnetic_multipoles(msum, m)
        return msum

    def _conv_tension_2_intfield(self, tension):
        m = self._conv_tension_2_multipoles(tension)
        mf = self._mfmult
        intfield = m[mf["type"]][mf["harmonic"]]
        return intfield

    def _conv_strength_2_intfield(self, strength, current_dipole):
        brho = self._dipole._get_brho(current_dipole)
        return strength*brho


class PulsedMagnetPowerSupply(PulsedPowerSupply):
    """Pulsed magnets are handled by this class."""

    class CompositeController:
        """Composition of devices that can be treated as one."""

        def __init__(self, devices):
            """Set devices."""
            self._devices = devices

        def get(self, attr, as_string=False):
            """Get first device attr."""
            return self._devices[0].get(attr, as_string)

        def put(self, attr, value, wait=False, timeout=10.0):
            """Put for all devices."""
            for device in self._devices:
                device.put(attr, value, wait, timeout)

        def add_callback(self, attr, callback):
            """Add callback for all devices."""
            for device in self._devices:
                device.add_callback(attr, callback)

    def __init__(self, maname, use_vaca=True, vaca_prefix="", callback=None):
        """Class constructor."""
        self._set_vaca_prefix(use_vaca, vaca_prefix)

        self._maname = _SiriusPVName(maname)
        self._psnames = [self._maname.replace("PM-", "PU-")]

        self._dipole_name = self._get_dipole_name()

        self._init_data()
        self._init_controller()

        self._strobj = PulsedMagnetNormalizer(self._maname, self._dipole_name)

        self._callback = callback

        self._threads = list()
        # PU Properties
        # self._tension_sp = 0.0
        # self._tension_rb = 0.0
        # self._tensionref_mon = 0.0
        # self._tension_mon = 0.0
        # self._pwrstate_sel = 0
        # self._pwrstate_sts = 0
        # self._enablepulses_sel = 0
        # self._enablepulses_sts = 0
        # self._reset_cmd = 0
        # self._intlk_mon = 0
        # self._ctrlmode_mon = 0
        # PM properties
        self._strength_sp = 0.0
        self._strength_rb = 0.0
        self._strengthref_mon = 0.0
        self._strength_mon = 0.0
        # Ref dipole properties
        self._dipole_current_sp = self._dipole_controller.get("Current-SP")
        self._dipole_current_rb = self._dipole_controller.get("Current-RB")
        self._dipole_currentref_mon = \
            self._dipole_controller.get("CurrentRef-Mon")
        self._dipole_current_mon = self._dipole_controller.get("Current-Mon")
        # Set callback to keep pu properties updated
        self._update_strengths()
        self._set_pv_callbacks()

    def __repr__(self):
        """Overload repr func."""
        rep = "PulsedMagnet(\n"

        rep += ("\t{}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n\n"
                ).format(self._maname,
                         pm_props.StrengthSP, self.strength_sp,
                         pm_props.StrengthRB, self.strength_rb,
                         pm_props.StrengthRefMon, self.strengthref_mon,
                         pm_props.StrengthMon, self.strength_mon)

        rep += ("\tDipole\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n\n"
                ).format("Current-SP", self._dipole_current_sp,
                         "Current-RB", self._dipole_current_rb,
                         "CurrentRef-Mon", self._dipole_currentref_mon,
                         "Current-Mon", self._dipole_current_mon)

        for psname in self._psnames:
            rep += ("\t{}\n"
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
                    "\t{:16s} - {}\n"
                    ).format(psname,
                             pu_props.CtrlMode, self.ctrlmode_mon,
                             pu_props.PwrStateSel, self.pwrstate_sel,
                             pu_props.PwrStateSts, self.pwrstate_sts,
                             pu_props.EnablePulsesSel, self.enablepulses_sel,
                             pu_props.EnablePulsesSts, self.enablepulses_sts,
                             pu_props.ResetCmd, self.reset_cmd,
                             pu_props.ExternalInterlock, self.intlk_mon,
                             pu_props.TensionSP, self.tension_sp,
                             pu_props.TensionRB, self.tension_rb,
                             pu_props.TensionRefMon, self.tensionref_mon,
                             pu_props.TensionMon, self.tension_mon)

        return rep + ")"

    @property
    def callback(self):
        """Callback property used by client to receive pv updates."""
        return self._callback

    @callback.setter
    def callback(self, func):
        if callable(func):
            self._callback = func
        else:
            raise AssertionError("Callback must be a callable type.")

    @property
    def tension_sp(self):
        """Return tension set point."""
        return self._controller.get(pu_props.TensionSP)

    @tension_sp.setter
    def tension_sp(self, value):
        self._update_strength(
            pm_props.StrengthSP, value, self._dipole_current_sp)
        self._controller.put(pu_props.TensionSP, value)

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self._strength_sp

    @strength_sp.setter
    def strength_sp(self, value):
        self._strength_sp = value
        # Denormalize and set tension
        self.tension_sp = self._strobj.conv_strength_2_tension(
            value, self._dipole_current_sp)

    @property
    def strength_rb(self):
        """Return strength set point."""
        return self._strength_rb

    @property
    def strengthref_mon(self):
        """Return strength set point."""
        return self._strengthref_mon

    @property
    def strength_mon(self):
        """Return strength set point."""
        return self._strength_mon

    def _get_database(self, prefix):
        db = self._data.get_database(self._data.psnames[0])

        db[pu_props.PwrStateSel]["value"] = self.pwrstate_sel
        db[pu_props.PwrStateSts]["value"] = self.pwrstate_sts
        db[pu_props.EnablePulsesSel]["value"] = self.enablepulses_sel
        db[pu_props.EnablePulsesSts]["value"] = self.enablepulses_sts
        db[pu_props.ResetCmd]["value"] = self.reset_cmd
        db[pu_props.CtrlMode]["value"] = self.ctrlmode_mon
        db[pu_props.ExternalInterlock]["value"] = self.intlk_mon
        db[pu_props.TensionSP]["value"] = self.tension_sp
        db[pu_props.TensionRB]["value"] = self.tension_rb
        db[pu_props.TensionRefMon]["value"] = self.tensionref_mon
        db[pu_props.TensionMon]["value"] = self.tension_mon
        db[pm_props.StrengthSP]["value"] = self.strength_sp
        db[pm_props.StrengthRB]["value"] = self.strength_rb
        db[pm_props.StrengthRefMon]["value"] = self.strengthref_mon
        db[pm_props.StrengthMon]["value"] = self.strength_mon

        hilim = self._strobj.conv_tension_2_strength(
            db[pu_props.TensionSP]["hilim"], self._dipole_current_sp)
        lolim = self._strobj.conv_tension_2_strength(
            db[pu_props.TensionSP]["lolim"], self._dipole_current_sp)

        if hilim < lolim:
            hilim, lolim = lolim, hilim

        db[pm_props.StrengthSP]["hilim"] = hilim
        db[pm_props.StrengthSP]["lolim"] = lolim

        prefixed_db = {}
        for key, value in db.items():
            prefixed_db[prefix + ":" + key] = value

        return prefixed_db

    def _init_data(self):
        self._data = _PMData(self._maname)

    def _init_controller(self):
        print(self._vaca_prefix)
        self._controller = self.CompositeController(
            [Device(prefix=self._vaca_prefix + psname, delim=":",
                    attrs=pu_props.PulsedPowerSupplyAttrs)
             for psname in self._psnames])

        attrs = ("Current-SP", "Current-RB", "CurrentRef-Mon", "Current-Mon")
        dipole_prefix = self._vaca_prefix + self._dipole_name
        self._dipole_controller = \
            Device(prefix=dipole_prefix, delim=":", attrs=attrs)
        # Set dipole callbacks
        for attr in attrs:
            self._dipole_controller.add_callback(
                attr, self._dipole_changed_callback)

    def _get_dipole_name(self):
        if _re.match("B.*", self._maname.dev_type):
            return None
        elif self._maname.section == "SI":
            return "SI-Fam:MA-B1B2"
        elif self._maname.section == "BO":
            return "BO-Fam:MA-B"
        elif self._maname.section == "TB":
            return "TB-Fam:MA-B"
        elif self._maname.section == "TS":
            return "TS-Fam:MA-B"
        else:
            raise NotImplementedError(
                "No section named {}".format(self._maname.section))

    def _issue_callback(self, pfield, value, **kwargs):
        if self._callback:
            pvname = self._maname + ":" + pfield
            self._callback(pvname, value, **kwargs)

    def _dipole_changed_callback(self, pvname, value, **kwargs):
        pfield = pvname.split(":")[-1]

        self._clear_threads()

        if pfield == "Current-SP":
            self._dipole_current_sp = value
            self._threads.append(
                Thread(target=self._update_strength,
                       args=(pm_props.StrengthSP,
                             self.tension_sp,
                             self._dipole_current_sp)))
            self._threads[-1].start()
        if pfield == "Current-RB":
            self._dipole_current_rb = value
            self._threads.append(
                Thread(target=self._update_strength,
                       args=(pm_props.StrengthRB,
                             self.tension_rb,
                             self._dipole_current_rb)))
            self._threads[-1].start()
        if pfield == "CurrentRef-Mon":
            self._dipole_currentref_mon = value
            self._threads.append(Thread(target=self._update_strength,
                                        args=(pm_props.StrengthRefMon,
                                              self.tensionref_mon,
                                              self._dipole_currentref_mon)))
            self._threads[-1].start()
        if pfield == "Current-Mon":
            self._dipole_current_mon = value
            self._threads.append(Thread(target=self._update_strength,
                                        args=(pm_props.StrengthMon,
                                              self.tension_mon,
                                              self._dipole_current_mon)))
            self._threads[-1].start()

    def _value_changed_callback(self, pvname, value, **kwargs):
        pfield = pvname.split(":")[-1]

        self._clear_threads()

        # Maybe use setattr when the pvname are defined
        if pfield == pu_props.TensionRB:
            # self._tension_rb = value
            self._threads.append(Thread(target=self._update_strength,
                                        args=(pm_props.StrengthRB, value,
                                              self._dipole_current_rb)))
            self._threads[-1].start()
        elif pfield == pu_props.TensionRefMon:
            # self._tensionref_mon = value
            self._threads.append(Thread(
                                    target=self._update_strength,
                                    args=(pm_props.StrengthRefMon, value,
                                          self._dipole_currentref_mon)))
            self._threads[-1].start()
        elif pfield == pu_props.TensionMon:
            # self._tension_mon = value
            self._threads.append(Thread(target=self._update_strength,
                                        args=(pm_props.StrengthMon, value,
                                              self._dipole_current_mon)))
            self._threads[-1].start()

        self._issue_callback(pfield, value, **kwargs)

    def _set_pv_callbacks(self):
        for prop in pu_props.PulsedPowerSupplyAttrs:
            self.add_callback_to_pv(prop, self._value_changed_callback)

    def _update_strength(self, pfield, tension, dipole_current):

        if pfield == pm_props.StrengthSP:
            self._strength_sp = \
                self._strobj.conv_tension_2_strength(tension, dipole_current)
            strength = self._strength_sp
        elif pfield == pm_props.StrengthRB:
            self._strength_rb = \
                self._strobj.conv_tension_2_strength(tension, dipole_current)
            strength = self._strength_rb
        elif pfield == pm_props.StrengthRefMon:
            self._strengthref_mon = \
                self._strobj.conv_tension_2_strength(tension, dipole_current)
            strength = self._strengthref_mon
        elif pfield == pm_props.StrengthMon:
            self._strength_mon = \
                self._strobj.conv_tension_2_strength(tension, dipole_current)
            strength = self._strength_mon

        self._issue_callback(pfield, strength)

    def _update_strengths(self):
        self._update_strength(pm_props.StrengthSP, self.tension_sp,
                              self._dipole_current_sp)
        self._update_strength(pm_props.StrengthRB, self.tension_rb,
                              self._dipole_current_rb)
        self._update_strength(pm_props.StrengthRefMon, self.tensionref_mon,
                              self._dipole_currentref_mon)
        self._update_strength(pm_props.StrengthMon, self.tension_mon,
                              self._dipole_current_mon)

    def _clear_threads(self):
        self._threads = [t for t in self._threads if t.isAlive()]
