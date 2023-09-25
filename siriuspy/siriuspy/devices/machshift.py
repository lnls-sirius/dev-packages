"""MachShift device."""

from ..machshift.csdev import ETypes as _ETypes
from .device import Device as _Device


class MachShift(_Device):
    """Machine Shift Device."""

    MODES = _ETypes.MACHSHIFT

    PROPERTIES_DEFAULT = ('Mode-Sel', 'Mode-Sts')

    def __init__(self, props2init='all'):
        """Init."""
        # call base class constructor
        super().__init__('AS-Glob:AP-MachShift', props2init=props2init)

    @property
    def mode(self):
        """Machine Shift Mode."""
        return self['Mode-Sts']

    @mode.setter
    def mode(self, value):
        self._enum_setter('Mode-Sel', value, MachShift.MODES)

    @property
    def mode_str(self):
        """Machine Shift Mode String."""
        return MachShift.MODES[self['Mode-Sts']]

    def check_mode(self, value):
        """Check if Mode-Sts is in desired value."""
        if isinstance(value, int):
            return self.mode == value
        return self.mode == MachShift.MODES.index(value)

    def wait_mode(self, mode, timeout=None):
        """Wait Mode-Sts to reach `mode` value."""
        if isinstance(mode, str):
            mode = MachShift.MODES.index(mode)
        return self._wait('Mode-Sts', mode, timeout=timeout)
