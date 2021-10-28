"""."""


from .device import Device as _Device
from .device import Devices as _Devices


class TuneFrac(_Device):
    """."""

    DEF_TIMEOUT = 1  # [s]

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-Tune-H'
        SI_V = 'SI-Glob:DI-Tune-V'
        ALL = (SI_H, SI_V)

    _properties = (
        'TuneFrac-Mon',
        'Enbl-Sel', 'Enbl-Sts'
        )

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

    @property
    def enable(self):
        """."""
        return self['Enbl-Sts']

    def cmd_enable(self, timeout=DEF_TIMEOUT):
        """."""
        self['Enbl-Sel'] = 1
        return self._wait('Enbl-Sts', value=1, timeout=timeout)

    def cmd_disable(self, timeout=DEF_TIMEOUT):
        """."""
        self['Enbl-Sel'] = 0
        return self._wait('Enbl-Sts', value=0, timeout=timeout)


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
        # check if device exists
        if devname not in Tune.DEVICES.ALL:
            raise NotImplementedError(devname)

        tune_frac_h = TuneFrac(TuneFrac.DEVICES.SI_H)
        tune_frac_v = TuneFrac(TuneFrac.DEVICES.SI_V)
        tune_proc_h = TuneProc(TuneProc.DEVICES.SI_H)
        tune_proc_v = TuneProc(TuneProc.DEVICES.SI_V)

        devices = (tune_frac_h, tune_frac_v, tune_proc_h, tune_proc_v)

        # call base class constructor
        super().__init__(devname, devices)

    @property
    def tunex(self):
        """."""
        return self.devices[0].tune

    @property
    def tuney(self):
        """."""
        return self.devices[1].tune

    @property
    def tunex_wfm(self):
        """."""
        return self.devices[2].tune_wfm

    @property
    def tuney_wfm(self):
        """."""
        return self.devices[3].tune_wfm

    @property
    def enablex(self):
        """."""
        return self.devices[0].enable

    @property
    def enabley(self):
        """."""
        return self.devices[1].enable

    def cmd_enablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """."""
        return self.devices[0].cmd_enable(timeout=timeout)

    def cmd_enabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """."""
        return self.devices[1].cmd_enable(timeout=timeout)

    def cmd_disablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """."""
        return self.devices[0].cmd_disable(timeout=timeout)

    def cmd_disabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """."""
        return self.devices[1].cmd_disable(timeout=timeout)

class TuneCorr(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:AP-TuneCorr'
        ALL = (SI, )

    _properties = (
        'DeltaTuneX-SP', 'DeltaTuneX-RB',
        'DeltaTuneY-SP', 'DeltaTuneY-RB',
        'SetNewRefKL-Cmd', 'ApplyDelta-Cmd',
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in TuneCorr.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=TuneCorr._properties)

    @property
    def delta_tunex(self):
        """."""
        return self['DeltaTuneX-RB']

    @delta_tunex.setter
    def delta_tunex(self, value):
        """."""
        self['DeltaTuneX-SP'] = value

    @property
    def delta_tuney(self):
        """."""
        return self['DeltaTuneY-RB']

    @delta_tuney.setter
    def delta_tuney(self, value):
        """."""
        self['DeltaTuneY-SP'] = value

    def cmd_update_reference(self):
        """."""
        self['SetNewRefKL-Cmd'] = 1
        return True

    def cmd_apply_delta(self):
        """."""
        self['ApplyDelta-Cmd'] = 1
        return True
