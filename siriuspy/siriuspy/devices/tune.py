"""."""


from .device import Device as _Device
from .device import Devices as _Devices


class TuneFrac(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-Tune-H'
        SI_V = 'SI-Glob:DI-Tune-V'
        ALL = (SI_H, SI_V)

    _properties = ('TuneFrac-Mon', )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in TuneFrac.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=TuneFrac._properties)

    @property
    def tune(self):
        """."""
        return self['TuneFrac-Mon']


class TuneProc(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-TuneProc-H'
        SI_V = 'SI-Glob:DI-TuneProc-V'
        ALL = (SI_H, SI_V)

    _properties = ('Trace-Mon', )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in TuneProc.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=TuneProc._properties)

    @property
    def tune_wfm(self):
        """."""
        return self['Trace-Mon']


class Tune(_Devices):
    """."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:DI-Tune'
        ALL = (SI, )

    def __init__(self, devname):
        """."""
        if devname == Tune.DEVICES.ALL:
            tune_frac_h = TuneFrac(TuneFrac.DEVICES.SI_H)
            tune_frac_v = TuneFrac(TuneFrac.DEVICES.SI_V)
            tune_proc_h = TuneFrac(TuneProc.DEVICES.SI_H)
            tune_proc_v = TuneFrac(TuneProc.DEVICES.SI_V)

        devices = (tune_frac_h, tune_frac_v, tune_proc_h, tune_proc_v)

        # call base class constructor
        super().__init__(devname, devices)

    def dev_tune_frac_h(self):
        """."""
        return self.devices[0]

    def dev_tune_frac_v(self):
        """."""
        return self.devices[1]

    def dev_tune_proc_h(self):
        """."""
        return self.devices[2]

    def dev_tune_proc_v(self):
        """."""
        return self.devices[3]
