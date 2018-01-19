"""Beagle Bone implementation module."""


class BeagleBone:
    """BeagleBone class."""

    def __init__(self, bbb_name):
        """Init method."""
        self._bbb_name = bbb_name
        self._serial_comm = None
        self._pwrsupplies = None

    @property
    def ps_names(self):
        """Return power supply names."""
        raise NotImplementedError

    @property
    def read(self, ps_name, field):
        """Return power supply field."""
        return self._pwrsupplies[ps_name].read(field)

    @property
    def write(self, ps_name, field, value):
        """Write value to field of power supply."""
        return self._pwrsupplies[ps_name].write(field, value)
