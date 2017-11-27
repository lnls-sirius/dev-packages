"""Class to handle pulsed magnets."""
import re as _re
import logging as _logging

from . import properties as _pm_props
from .data import PMData as _PMData
from .ComputedPV import ComputedPV as _ComputedPV
from .normalizer import PulsedMagnetNormalizer as \
    _PulsedMagnetNormalizer
from ..namesys import SiriusPVName as _SiriusPVName
from ..pulsedps import properties as _pu_props
from ..pulsedps.model import PulsedPowerSupply as _PulsedPowerSupply

_logging.basicConfig(level=_logging.WARNING)


class PulsedMagnetPowerSupply(_PulsedPowerSupply):
    """Pulsed magnets are handled by this class."""

    def __init__(self, maname,
                 use_vaca=False,
                 vaca_prefix="",
                 lock=True,
                 callback=None):
        """Class constructor."""
        self._maname = _SiriusPVName(maname)
        # Dipole used to get normalized strength
        self._dipole_name = self._get_dipole_name()
        # Object used by the normalized strength computed pv
        self._strobj = _PulsedMagnetNormalizer(self._maname, self._dipole_name)
        # Call PulsedPowerSupply constructor
        super().__init__(self._maname.replace("PM-", "PU-"),
                         use_vaca=True,
                         lock=lock)

    def __repr__(self):
        """Overload repr func."""
        rep = "PulsedMagnet(\n"

        rep += ("\t{}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n\n"
                ).format(self.maname,
                         _pm_props.StrengthSP, self.strength_sp,
                         _pm_props.StrengthRB, self.strength_rb,
                         _pm_props.StrengthRefMon, self.strengthref_mon,
                         _pm_props.StrengthMon, self.strength_mon)

        """rep += ("\tDipole\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n\n"
                ).format("Current-SP", self._dipole_current_sp,
                         "Current-RB", self._dipole_current_rb,
                         "CurrentRef-Mon", self._dipole_currentref_mon,
                         "Current-Mon", self._dipole_current_mon)"""

        # for psname in self._psnames:
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
                ).format(self._psname,
                         _pu_props.CtrlMode, self.ctrlmode_mon,
                         _pu_props.PwrStateSel, self.pwrstate_sel,
                         _pu_props.PwrStateSts, self.pwrstate_sts,
                         _pu_props.EnablePulsesSel, self.enablepulses_sel,
                         _pu_props.EnablePulsesSts, self.enablepulses_sts,
                         _pu_props.ResetCmd, self.reset_cmd,
                         _pu_props.ExternalInterlock, self.intlk_mon,
                         _pu_props.TensionSP, self.tension_sp,
                         _pu_props.TensionRB, self.tension_rb,
                         _pu_props.TensionRefMon, self.tensionref_mon,
                         _pu_props.TensionMon, self.tension_mon)

        return rep + ")"

    @property
    def maname(self):
        """Return magnet name."""
        return self._maname

    @property
    def callback(self):
        """Callback property used by client to receive pv updates."""
        return self._callback

    @callback.setter
    def callback(self, func):
        if callable(func):
            for pv in self._controller.values():
                pv.add_callback(func)
            # self._callback = func
        else:
            raise AssertionError("Callback must be a callable type.")

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self.read(self._controller, _pm_props.StrengthSP)

    @strength_sp.setter
    def strength_sp(self, value):
        upper_limit = self._controller[_pm_props.StrengthSP].upper_disp_limit
        lower_limit = self._controller[_pm_props.StrengthSP].lower_disp_limit

        if upper_limit is None or lower_limit is None:
            return

        if value > upper_limit:
            value = upper_limit
        elif value < lower_limit:
            value = lower_limit
        self.write(self._controller, _pm_props.StrengthSP, value)

    @property
    def strength_rb(self):
        """Return strength set point."""
        # return self._strength_rb
        return self._controller[_pm_props.StrengthRB].get()

    @property
    def strengthref_mon(self):
        """Return strength set point."""
        # return self._strengthref_mon
        return self._controller[_pm_props.StrengthRefMon].get()

    @property
    def strength_mon(self):
        """Return strength set point."""
        # return self._strength_mon
        return self._controller[_pm_props.StrengthMon].get()

    @property
    def database(self):
        """PV database."""
        return self._get_database()

    def _get_database(self, prefix=None):
        for attr in _pm_props.PulsedMagnetAttrs:
            value = self.read(self._controller, attr)
            if value is not None:
                self._db[attr]["value"] = value

        self._db[_pm_props.StrengthSP]["high"] = \
            (self._controller[_pm_props.StrengthSP].upper_warning_limit or 0.0)
        self._db[_pm_props.StrengthSP]["low"] = \
            (self._controller[_pm_props.StrengthSP].lower_warning_limit or 0.0)
        self._db[_pm_props.StrengthSP]["hihi"] = \
            (self._controller[_pm_props.StrengthSP].upper_alarm_limit or 0.0)
        self._db[_pm_props.StrengthSP]["lolo"] = \
            (self._controller[_pm_props.StrengthSP].lower_alarm_limit or 0.0)
        self._db[_pm_props.StrengthSP]["hilim"] = \
            (self._controller[_pm_props.StrengthSP].upper_disp_limit or 0.0)
        self._db[_pm_props.StrengthSP]["lolim"] = \
            (self._controller[_pm_props.StrengthSP].lower_disp_limit or 0.0)

        if prefix is None:
            return self._db

        prefixed_db = {}
        for key, value in self._db.items():
            prefixed_db[prefix + ":" + key] = value

        return prefixed_db

    def _init_data(self):
        self._data = _PMData(self._maname)
        self._db = self._data.get_database(self._data.psnames[0])

    def _init_controller(self):
        # Init PS PVs
        super()._init_controller()
        # Add magnet normalized PVs
        ma_prefix = self._vaca_prefix + self._psname
        dipole_prefix = self._vaca_prefix + self._dipole_name

        computed_pvs = {
            _pm_props.StrengthSP: [
                dipole_prefix + ":" + "Current-SP",
                ma_prefix + ":" + _pu_props.TensionSP],
            _pm_props.StrengthRB: [
                dipole_prefix + ":" + "Current-RB",
                ma_prefix + ":" + _pu_props.TensionRB],
            _pm_props.StrengthRefMon:
                [dipole_prefix + ":" + "CurrentRef-Mon",
                 ma_prefix + ":" + _pu_props.TensionRefMon],
            _pm_props.StrengthMon: [dipole_prefix + ":" + "Current-Mon",
                                    ma_prefix + ":" + _pu_props.TensionMon]}
        # Add PVs as computed PVs
        for attr, params in computed_pvs.items():
            pvname = self.maname + ":" + attr
            self._controller[attr] = \
                _ComputedPV(pvname, self._strobj, params[1], params[0])
        # Wait for connection 1ms
        # for pv in self._controller.values():
        #     print("Waitng for pv {}".format(pv))
        #     pv.wait_for_connection(timeout=0.001)

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
