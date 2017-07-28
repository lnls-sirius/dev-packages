"""This module has classes that defines different configurations of PVs."""
import re
from ..search import MASearch


class ConfigurationPvs:
    """Base class that defines a group of PVs."""

    def pvs(self):
        """Return pvs that belong to this configuration.

        This function must be overriden by sub classes.
        """
        return self._getPvs()

    @staticmethod
    def getStrengthName(slot):
        """Return strength name for given device."""
        if re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-B", slot):
            return "Energy"
        elif re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-Q", slot):
            return "KL"
        elif re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-S", slot):
            return "SL"
        elif re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-(C|F)", slot):
            return "Kick"
        else:
            raise NotImplementedError

    def _getPvs(self):
        raise NotImplementedError


class BoStrengthPvs(ConfigurationPvs):
    """Configuration of strength PVs from booster elements."""

    def _getPvs(self):
        pvs = dict()
        slots = MASearch.get_manames()
        if slots:
            for slot in slots:
                strength_name = ConfigurationPvs.getStrengthName(slot)
                pv = slot + ":" + strength_name + "-RB"
                if re.match("^BO-\w{2,4}:MA-(B|Q|S|C|F)", pv):
                    pvs[pv] = float

        return pvs


class SiStrengthPvs(ConfigurationPvs):
    """Configuration of strength PVs from sirius elements."""

    def _getPvs(self):
        pvs = dict()
        slots = MASearch.get_manames()
        if slots:
            for slot in slots:
                strength_name = ConfigurationPvs.getStrengthName(slot)
                pv = slot + ":" + strength_name + "-RB"
                if re.match("^SI-Fam:MA-(B|Q|S)", pv) or \
                        re.match("^SI-\d{2}[A-Z]\d:MA-(:?Q|CH|CV|FCH|FCV).*", pv):
                    pvs[pv] = float

        return pvs
