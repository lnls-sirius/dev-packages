"""Tune devices."""


from .device import Device as _Device
from .device import DeviceSet as _DeviceSet


class TuneFrac(_Device):
    """Tune Frac device."""

    DEF_TIMEOUT = 1  # [s]

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-Tune-H'
        SI_V = 'SI-Glob:DI-Tune-V'
        ALL = (SI_H, SI_V)

    PROPERTIES_DEFAULT = ('TuneFrac-Mon', 'Enbl-Sel', 'Enbl-Sts')

    def __init__(self, devname, props2init='all'):
        """Init."""
        if devname not in TuneFrac.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def tune(self):
        """Tune Frac."""
        return self['TuneFrac-Mon']

    @property
    def enable(self):
        """Enable status."""
        return self['Enbl-Sts']

    def cmd_enable(self, timeout=DEF_TIMEOUT):
        """Enable."""
        self['Enbl-Sel'] = 1
        return self._wait('Enbl-Sts', value=1, timeout=timeout)

    def cmd_disable(self, timeout=DEF_TIMEOUT):
        """Disable."""
        self['Enbl-Sel'] = 0
        return self._wait('Enbl-Sts', value=0, timeout=timeout)


class TuneProc(_Device):
    """Tune Proc device."""

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-TuneProc-H'
        SI_V = 'SI-Glob:DI-TuneProc-V'
        ALL = (SI_H, SI_V)

    PROPERTIES_DEFAULT = ('Trace-Mon', )

    def __init__(self, devname, props2init='all'):
        """Init."""
        # check if device exists
        if devname not in TuneProc.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def tune_wfm(self):
        """Tune waveform."""
        return self['Trace-Mon']


class Tune(_DeviceSet):
    """Tune device."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:DI-Tune'
        ALL = (SI, )

    def __init__(self, devname=None):
        """Init."""
        # check if device exists
        if devname is None:
            devname = Tune.DEVICES.SI
        if devname not in Tune.DEVICES.ALL:
            raise NotImplementedError(devname)

        tune_frac_h = TuneFrac(TuneFrac.DEVICES.SI_H)
        tune_frac_v = TuneFrac(TuneFrac.DEVICES.SI_V)
        tune_proc_h = TuneProc(TuneProc.DEVICES.SI_H)
        tune_proc_v = TuneProc(TuneProc.DEVICES.SI_V)

        devices = (tune_frac_h, tune_frac_v, tune_proc_h, tune_proc_v)

        # call base class constructor
        super().__init__(devices, devname=devname)

    @property
    def tunex(self):
        """Tune Frac X."""
        return self.devices[0].tune

    @property
    def tuney(self):
        """Tune Frac Y."""
        return self.devices[1].tune

    @property
    def tunex_wfm(self):
        """Tune waveform X."""
        return self.devices[2].tune_wfm

    @property
    def tuney_wfm(self):
        """Tune waveform Y."""
        return self.devices[3].tune_wfm

    @property
    def enablex(self):
        """Tune X enable status."""
        return self.devices[0].enable

    @property
    def enabley(self):
        """Tune Y enable status."""
        return self.devices[1].enable

    def cmd_enablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Enable tune X."""
        return self.devices[0].cmd_enable(timeout=timeout)

    def cmd_enabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Enable tune Y."""
        return self.devices[1].cmd_enable(timeout=timeout)

    def cmd_disablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Disable tune X."""
        return self.devices[0].cmd_disable(timeout=timeout)

    def cmd_disabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Disable tune Y."""
        return self.devices[1].cmd_disable(timeout=timeout)


class TuneCorr(_Device):
    """TuneCorr device."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:AP-TuneCorr'
        ALL = (SI, )

    PROPERTIES_DEFAULT = (
        'DeltaTuneX-SP', 'DeltaTuneX-RB',
        'DeltaTuneY-SP', 'DeltaTuneY-RB',
        'SetNewRefKL-Cmd', 'ApplyDelta-Cmd',
        )

    def __init__(self, devname=None, props2init='all'):
        """Init."""
        if devname is None:
            devname = TuneCorr.DEVICES.SI
        if devname not in TuneCorr.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def delta_tunex(self):
        """Delta Tune X."""
        return self['DeltaTuneX-RB']

    @delta_tunex.setter
    def delta_tunex(self, value):
        self['DeltaTuneX-SP'] = value

    @property
    def delta_tuney(self):
        """Delta Tune Y."""
        return self['DeltaTuneY-RB']

    @delta_tuney.setter
    def delta_tuney(self, value):
        self['DeltaTuneY-SP'] = value

    def cmd_update_reference(self):
        """Update reference tunes."""
        self['SetNewRefKL-Cmd'] = 1
        return True

    def cmd_apply_delta(self):
        """Apply delta tunes."""
        self['ApplyDelta-Cmd'] = 1
        return True
