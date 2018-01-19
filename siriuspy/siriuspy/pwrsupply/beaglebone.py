"""Beagle Bone implementation module."""


class BeagleBone:
    """BeagleBone class."""

    def __init__(self, bbb_name):
        """Init method."""
        self._bbb_name = bbb_name
        self._serial_comm = None
        self._pwrsupplies = None

    @property
    def psnames(self):
        """Return power supply names."""
        raise NotImplementedError

    @property
    def read(self, psname, field):
        """Return power supply field."""
        return self._pwrsupplies[psname].read(field)

    @property
    def write(self, psname, field, value):
        """Write value to field of power supply."""
        return self._pwrsupplies[psname].write(field, value)
