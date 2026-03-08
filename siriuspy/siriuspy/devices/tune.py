"""Tune devices."""

from .device import Device as _Device, DeviceSet as _DeviceSet


class TuneFrac(_Device):
    """Tune Frac device."""

    DEF_TIMEOUT = 1  # [s]

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-Tune-H'
        SI_V = 'SI-Glob:DI-Tune-V'
        ALL = (SI_H, SI_V)

    PROPERTIES_DEFAULT = (
        'TuneFrac-Mon',
        'Enbl-Sel',
        'Enbl-Sts',
        'Span-RB',
        'Span-SP',
        'RevN-RB',
        'RevN-SP',
        'FreqOff-RB',
        'FreqOff-SP',
    )

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
    def span(self):
        """Span."""
        return self['Span-RB']

    @span.setter
    def span(self, value):
        """Span."""
        self['Span-SP'] = value

    @property
    def rev_harmonic(self):
        """Revolution harmonic."""
        return self['RevN-RB']

    @rev_harmonic.setter
    def rev_harmonic(self, value):
        """Revolution harmonic."""
        if not 0 <= int(value) <= 864:
            raise ValueError('rev_harmonic must be in range [0, 864]')
        self['RevN-SP'] = int(value)

    @property
    def center_frequency(self):
        """Center frequency."""
        return self['FreqOff-RB']

    @center_frequency.setter
    def center_frequency(self, value):
        """Center frequency."""
        self['FreqOff-SP'] = value

    @property
    def enable(self):
        """Enable status."""
        return self['Enbl-Sts']

    def cmd_enable(self, timeout=DEF_TIMEOUT):
        """Enable."""
        self['Enbl-Sel'] = 1
        return self.wait('Enbl-Sts', value=1, timeout=timeout)

    def cmd_disable(self, timeout=DEF_TIMEOUT):
        """Disable."""
        self['Enbl-Sel'] = 0
        return self.wait('Enbl-Sts', value=0, timeout=timeout)


class TuneProc(_Device):
    """Tune Proc device."""

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-TuneProc-H'
        SI_V = 'SI-Glob:DI-TuneProc-V'
        ALL = (SI_H, SI_V)

    PROPERTIES_DEFAULT = ('Trace-Mon',)

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
        ALL = (SI,)

    def __init__(self, devname=None, props2init='all'):
        """Init."""
        # check if device exists
        if devname is None:
            devname = Tune.DEVICES.SI
        if devname not in Tune.DEVICES.ALL:
            raise NotImplementedError(devname)

        isall = isinstance(props2init, str) and props2init.lower() == 'all'
        if not isall and props2init:
            raise ValueError(
                "props2init must be 'all' or bool(props2init) == False"
            )

        tune_frac_h = TuneFrac(TuneFrac.DEVICES.SI_H, props2init=props2init)
        tune_frac_v = TuneFrac(TuneFrac.DEVICES.SI_V, props2init=props2init)
        tune_proc_h = TuneProc(TuneProc.DEVICES.SI_H, props2init=props2init)
        tune_proc_v = TuneProc(TuneProc.DEVICES.SI_V, props2init=props2init)

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
    def spanx(self):
        """Span X."""
        return self.devices[0].span

    @spanx.setter
    def spanx(self, value):
        """Span X."""
        self.devices[0].span = value

    @property
    def spany(self):
        """Span Y."""
        return self.devices[1].span

    @spany.setter
    def spany(self, value):
        """Span Y."""
        self.devices[1].span = value

    @property
    def rev_harmonicx(self):
        """Revolution harmonic X."""
        return self.devices[0].rev_harmonic

    @rev_harmonicx.setter
    def rev_harmonicx(self, value):
        """Revolution harmonic X."""
        self.devices[0].rev_harmonic = value

    @property
    def rev_harmonicy(self):
        """Revolution harmonic Y."""
        return self.devices[1].rev_harmonic

    @rev_harmonicy.setter
    def rev_harmonicy(self, value):
        """Revolution harmonic Y."""
        self.devices[1].rev_harmonic = value

    @property
    def center_frequencyx(self):
        """Center frequency X."""
        return self.devices[0].center_frequency

    @center_frequencyx.setter
    def center_frequencyx(self, value):
        """Center frequency X."""
        self.devices[0].center_frequency = value

    @property
    def center_frequencyy(self):
        """Center frequency Y."""
        return self.devices[1].center_frequency

    @center_frequencyy.setter
    def center_frequencyy(self, value):
        """Center frequency Y."""
        self.devices[1].center_frequency = value

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
        ALL = (SI,)

    PROPERTIES_DEFAULT = (
        'DeltaTuneX-SP',
        'DeltaTuneX-RB',
        'DeltaTuneY-SP',
        'DeltaTuneY-RB',
        'SetNewRefKL-Cmd',
        'ApplyDelta-Cmd',
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
