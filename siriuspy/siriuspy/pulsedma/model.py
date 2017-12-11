"""Class to handle pulsed magnets."""
import re as _re
import logging as _logging

from .data import PMData as _PMData
from .ComputedPV import ComputedPV as _ComputedPV
from .normalizer import PulsedMagnetNormalizer as \
    _PulsedMagnetNormalizer
from ..namesys import SiriusPVName as _SiriusPVName
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
                "\t{:16s} - {}\n\n"
                ).format(self.maname,
                         'Kick-SP', self.strength_sp,
                         'Kick-RB', self.strength_rb,
                         'Kick-Mon', self.strength_mon)

        """rep += ("\tDipole\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n"
                "\t{:16s} - {}\n\n"
                ).format("Current-SP", self._dipole_current_sp,
                         "Current-RB", self._dipole_current_rb,
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
                         'CtrlMode-Mon', self.ctrlmode_mon,
                         'PwrState-Sel', self.pwrstate_sel,
                         'PwrState-Sts', self.pwrstate_sts,
                         'Pulsed-Sel', self.pulsed_sel,
                         'Pulsed-Sts', self.pulsed_sts,
                         'Reset-Cmd', self.reset_cmd,
                         'Intl-Mon', self.intlk_mon,
                         'Voltage-SP', self.voltage_sp,
                         'Voltage-RB', self.voltage_rb,
                         'Voltage-Mon', self.voltage_mon)

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
        return self.read(self._controller, 'Kick-SP')

    @strength_sp.setter
    def strength_sp(self, value):
        upper_limit = self._controller['Kick-SP'].upper_disp_limit
        lower_limit = self._controller['Kick-SP'].lower_disp_limit

        if upper_limit is None or lower_limit is None:
            return

        if value > upper_limit:
            value = upper_limit
        elif value < lower_limit:
            value = lower_limit
        self.write(self._controller, 'Kick-SP', value)

    @property
    def strength_rb(self):
        """Return strength set point."""
        # return self._strength_rb
        return self._controller['Kick-RB'].get()

    @property
    def strengthref_mon(self):
        """Return strength set point."""
        # return self._strengthref_mon
        return self._controller[_ps_props.StrengthRefMon].get()

    @property
    def strength_mon(self):
        """Return strength set point."""
        # return self._strength_mon
        return self._controller['Kick-Mon'].get()

    @property
    def database(self):
        """PV database."""
        return self._get_database()

    def _get_database(self, prefix=None):
        # Use CSDEVICE !!!

        for attr in ('Kick-SP', 'Kick-RB', 'Kick-Mon'):
            value = self.read(self._controller, attr)
            if value is not None:
                self._db[attr]["value"] = value

        self._db['Kick-SP']["high"] = \
            (self._controller['Kick-SP'].upper_warning_limit or 0.0)
        self._db['Kick-SP']["low"] = \
            (self._controller['Kick-SP'].lower_warning_limit or 0.0)
        self._db['Kick-SP']["hihi"] = \
            (self._controller['Kick-SP'].upper_alarm_limit or 0.0)
        self._db['Kick-SP']["lolo"] = \
            (self._controller['Kick-SP'].lower_alarm_limit or 0.0)
        self._db['Kick-SP']["hilim"] = \
            (self._controller['Kick-SP'].upper_disp_limit or 0.0)
        self._db['Kick-SP']["lolim"] = \
            (self._controller['Kick-SP'].lower_disp_limit or 0.0)

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
            'Kick-SP': [
                dipole_prefix + ":" + "Current-SP",
                ma_prefix + ":" + 'Voltage-SP'],
            'Kick-RB': [
                dipole_prefix + ":" + "Current-RB",
                ma_prefix + ":" + 'Voltage-RB'],
            'Kick-Mon': [dipole_prefix + ":" + "Current-Mon",
                         ma_prefix + ":" + 'Voltage-Mon']}
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
        if _re.match("B.*", self._maname.dev):
            return None
        elif self._maname.sec == "SI":
            return "SI-Fam:MA-B1B2"
        elif self._maname.sec == "BO":
            return "BO-Fam:MA-B"
        elif self._maname.sec == "TB":
            return "TB-Fam:MA-B"
        elif self._maname.sec == "TS":
            return "TS-Fam:MA-B"
        else:
            raise NotImplementedError(
                "No section named {}".format(self._maname.sec))
