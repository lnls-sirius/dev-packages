"""."""


from .device import Device as _Device
from .device import Devices as _Devices


class TuneFrac(_Device):
    """."""

    DEVICE_SI_H = 'SI-Glob:DI-Tune-H'
    DEVICE_SI_V = 'SI-Glob:DI-Tune-V'

    DEVICES = (DEVICE_SI_H, DEVICE_SI_V)

    _properties = ('TuneFrac-Mon', )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in TuneFrac.DEVICES:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=TuneFrac._properties)

    @property
    def tune(self):
        """."""
        return self['TuneFrac-Mon']


class TuneProc(_Device):
    """."""

    DEVICE_SI_H = 'SI-Glob:DI-TuneProc-H'
    DEVICE_SI_V = 'SI-Glob:DI-TuneProc-V'

    DEVICES = (DEVICE_SI_H, DEVICE_SI_V)

    _properties = ('Trace-Mon', )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in TuneProc.DEVICES:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=TuneProc._properties)

    @property
    def tune_wfm(self):
        """."""
        return self['Trace-Mon']


class Tune(_Devices):
    """."""

    DEVICE_SI = 'SI-Glob:DI-Tune'

    DEVICES = (DEVICE_SI, )

    def __init__(self, devname):
        """."""
        if devname == Tune.DEVICE_SI:
            tune_frac_h = TuneFrac(TuneFrac.DEVICE_SI_H)
            tune_frac_v = TuneFrac(TuneFrac.DEVICE_SI_V)
            tune_proc_h = TuneFrac(TuneProc.DEVICE_SI_H)
            tune_proc_v = TuneFrac(TuneProc.DEVICE_SI_V)

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
