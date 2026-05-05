"""Tune devices."""

from ..optics.constants import SI as _SI, BO as _BO

from .device import Device as _Device, DeviceSet as _DeviceSet
from .timing import Trigger as _Trigger


class TuneFrac(_Device):
    """Tune Frac device."""

    DEF_TIMEOUT = 1  # [s]

    class DEVICES:
        """Devices names."""

        SI_H = 'SI-Glob:DI-Tune-H'
        SI_V = 'SI-Glob:DI-Tune-V'
        BO_H = 'BO-Glob:DI-Tune-H'
        BO_V = 'BO-Glob:DI-Tune-V'
        ALL = (SI_H, SI_V, BO_H, BO_V)

    PROPERTIES_DEFAULT = (
        'SpecAnaGetSpec-Sel',
        'SpecAnaGetSpec-Sts',
        'Enbl-Sel',
        'Enbl-Sts',
        'Span-RB',
        'Span-SP',
        'RevN-RB',
        'RevN-SP',
        'FreqOff-RB',
        'FreqOff-SP',
    )
    PROPERTIES_DEFAULT_SI = PROPERTIES_DEFAULT + (
        'TuneFrac-Mon',
    )
    PROPERTIES_DEFAULT_BO = PROPERTIES_DEFAULT

    def __init__(self, devname, props2init='all'):
        """Init."""
        if devname not in TuneFrac.DEVICES.ALL:
            raise NotImplementedError(devname)
        is_si = devname.startswith(_SI.sector)
        self._sector = _SI.sector if is_si else _BO.sector
        if self.sector == _SI.sector:
            self.PROPERTIES_DEFAULT = TuneFrac.PROPERTIES_DEFAULT_SI
        else:
            self.PROPERTIES_DEFAULT = TuneFrac.PROPERTIES_DEFAULT_BO
        super().__init__(devname, props2init=props2init)

    @property
    def sector(self):
        """."""
        return self._sector

    @property
    def tune(self):
        """Tune Frac."""
        if self.sector == _SI.sector:
            return self['TuneFrac-Mon']

    @property
    def span(self):
        """Span [kHz]."""
        return self['Span-RB']

    @span.setter
    def span(self, value):
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
        """Center frequency offset [kHz]."""
        return self['FreqOff-RB']

    @center_frequency.setter
    def center_frequency(self, value):
        self['FreqOff-SP'] = value

    @property
    def aquisition_enabled(self):
        """Return aquisition state."""
        return self['SpecAnaGetSpec-Sts']

    @property
    def excitation_enabled(self):
        """Return excitation state."""
        return self['Enbl-Sts']

    def cmd_acquisition_enable(self, timeout=DEF_TIMEOUT):
        """Start data acquisition."""
        self['SpecAnaGetSpec-Sel'] = 1
        return self.wait('SpecAnaGetSpec-Sts', value=1, timeout=timeout)

    def cmd_acquisition_disable(self, timeout=DEF_TIMEOUT):
        """Stop data acquisition."""
        self['SpecAnaGetSpec-Sel'] = 0
        return self.wait('SpecAnaGetSpec-Sts', value=0, timeout=timeout)

    def cmd_excitation_enable(self, timeout=DEF_TIMEOUT):
        """Enable."""
        self['Enbl-Sel'] = 1
        return self.wait('Enbl-Sts', value=1, timeout=timeout)

    def cmd_excitation_disable(self, timeout=DEF_TIMEOUT):
        """Disable."""
        self['Enbl-Sel'] = 0
        return self.wait('Enbl-Sts', value=0, timeout=timeout)


class SITuneProc(_Device):
    """Tune Proc device."""

    class DEVICES:
        """Devices names."""

        H = 'SI-Glob:DI-TuneProc-H'
        V = 'SI-Glob:DI-TuneProc-V'
        ALL = (H, V)

    PROPERTIES_DEFAULT = ('Trace-Mon',)

    def __init__(self, devname, props2init='all'):
        """Init."""
        # check if device exists
        if devname not in SITuneProc.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def tune_wfm(self):
        """Tune waveform."""
        return self['Trace-Mon']


class BOTuneProc(_Device):
    """Tune Proc device."""

    class DEVICES:
        """Devices names."""

        H = 'BO-Glob:DI-TuneProc-H'
        V = 'BO-Glob:DI-TuneProc-V'
        ALL = (H, V)

    PROPERTIES_DEFAULT = (
        'SpecArray-Mon',
        'SwePts-SP',
        'SwePts-RB',
        'FrameCount-Mon',
    )

    def __init__(self, devname, props2init='all'):
        """Init."""
        # check if device exists
        if devname not in BOTuneProc.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def freq_sweep_nrpts(self):
        """."""
        return int(self['SwePts-RB'])  # type: ignore

    @freq_sweep_nrpts.setter
    def freq_sweep_nrpts(self, value):
        """."""
        self['SwePts-SP'] = value

    @property
    def frame_count(self):
        """."""
        return self['FrameCount-Mon']

    @property
    def tune_spect_array(self):
        """Tune spect array."""
        spect = self['SpecArray-Mon']
        return spect


class Tune(_DeviceSet):
    """Tune device."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:DI-Tune'
        BO = 'BO-Glob:DI-Tune'
        ALL = (SI, BO)

    def __init__(self, devname=None, props2init='all'):
        """Init."""
        # check if device exists
        if devname is None:
            devname = Tune.DEVICES.SI
        if devname not in Tune.DEVICES.ALL:
            raise NotImplementedError(devname)
        is_si = devname.startswith(_SI.sector)
        self._sector = _SI.sector if is_si else _BO.sector
        isall = isinstance(props2init, str) and props2init.lower() == 'all'
        if not isall and props2init:
            raise ValueError(
                "props2init must be 'all' or bool(props2init) == False"
            )

        if self.sector == _SI.sector:
            tune_frac_h = TuneFrac(
                TuneFrac.DEVICES.SI_H, props2init=props2init)
            tune_frac_v = TuneFrac(
                TuneFrac.DEVICES.SI_V, props2init=props2init)
            tune_proc_h = SITuneProc(
                SITuneProc.DEVICES.H, props2init=props2init)
            tune_proc_v = SITuneProc(
                SITuneProc.DEVICES.V, props2init=props2init)
            devices = (
                tune_frac_h,
                tune_frac_v,
                tune_proc_h,
                tune_proc_v,
            )
        else:
            tune_frac_h = TuneFrac(
                TuneFrac.DEVICES.BO_H, props2init=props2init)
            tune_frac_v = TuneFrac(
                TuneFrac.DEVICES.BO_V, props2init=props2init)
            tune_proc_h = BOTuneProc(
                BOTuneProc.DEVICES.H, props2init=props2init)
            tune_proc_v = BOTuneProc(
                BOTuneProc.DEVICES.V, props2init=props2init)
            trig = _Trigger(trigname='BO-Glob:TI-TuneProc')
            devices = (
                tune_frac_h,
                tune_frac_v,
                tune_proc_h,
                tune_proc_v,
                trig
            )

        # call base class constructor
        super().__init__(devices, devname=devname)

    @property
    def sector(self):
        """."""
        return self._sector

    @property
    def dev_tune_frac_h(self):
        """."""
        return self.devices[0]

    @property
    def dev_tune_frac_v(self):
        """."""
        return self.devices[1]

    @property
    def dev_tune_proc_h(self):
        """."""
        return self.devices[2]

    @property
    def dev_tune_proc_v(self):
        """."""
        return self.devices[3]

    @property
    def dev_trig(self):
        """."""
        if self.sector == _BO.sector:
            return self.devices[4]

    @property
    def tunex(self):
        """Tune Frac X."""
        if self.sector == _SI.sector:
            return self.dev_tune_frac_h.tune

    @property
    def tuney(self):
        """Tune Frac Y."""
        if self.sector == _SI.sector:
            return self.dev_tune_frac_v.tune

    @property
    def trig_nr_pulses(self):
        """."""
        if self.sector == _BO.sector:
            return self.dev_trig.nr_pulses

    @property
    def frame_countx(self):
        """."""
        if self.sector == _BO.sector:
            return self.dev_tune_proc_h.frame_count

    @property
    def frame_county(self):
        """."""
        if self.sector == _BO.sector:
            return self.dev_tune_proc_v.frame_count

    @property
    def spectx(self):
        """."""
        if self.sector == _BO.sector:
            return self._get_spect(self.dev_tune_proc_h)

    @property
    def specty(self):
        """."""
        if self.sector == _BO.sector:
            return self._get_spect(self.dev_tune_proc_v)

    @property
    def spectx_acquisition_status(self):
        """."""
        if self.sector == _BO.sector:
            return self.frame_countx == self.trig_nr_pulses

    @property
    def specty_acquisition_status(self):
        """."""
        if self.sector == _BO.sector:
            return self.frame_county == self.trig_nr_pulses

    @property
    def spanx(self):
        """Span X [kHz]."""
        return self.devices[0].span

    @spanx.setter
    def spanx(self, value):
        self.devices[0].span = value

    @property
    def spany(self):
        """Span Y [kHz]."""
        return self.devices[1].span

    @spany.setter
    def spany(self, value):
        self.devices[1].span = value

    @property
    def rev_harmonicx(self):
        """Revolution harmonic X."""
        return self.devices[0].rev_harmonic

    @rev_harmonicx.setter
    def rev_harmonicx(self, value):
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
        self.devices[0].center_frequency = value

    @property
    def center_frequencyy(self):
        """Center frequency Y."""
        return self.devices[1].center_frequency

    @center_frequencyy.setter
    def center_frequencyy(self, value):
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

    def cmd_acquisition_enablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Enable tune X acquisition."""
        return self.dev_tune_frac_h.cmd_acquisition_enable(timeout=timeout)

    def cmd_acquisition_enabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Enable tune Y acquisition."""
        return self.dev_tune_frac_v.cmd_acquisition_enable(timeout=timeout)

    def cmd_acquisition_disablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Disable tune X acquisition."""
        return self.dev_tune_frac_h.cmd_acquisition_disable(timeout=timeout)

    def cmd_acquisition_disabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Disable tune Y acquisition."""
        return self.dev_tune_frac_v.cmd_acquisition_disable(timeout=timeout)

    def cmd_excitation_enablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Enable tune X excitation."""
        return self.devices[0].cmd_excitation_enable(timeout=timeout)

    def cmd_excitation_enabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Enable tune Y excitation."""
        return self.devices[1].cmd_excitation_enable(timeout=timeout)

    def cmd_excitation_disablex(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Disable tune X excitation."""
        return self.devices[0].cmd_excitation_disable(timeout=timeout)

    def cmd_excitation_disabley(self, timeout=TuneFrac.DEF_TIMEOUT):
        """Disable tune Y excitation."""
        return self.devices[1].cmd_excitation_disable(timeout=timeout)

    def _get_spect(self, dev_proc):
        """."""
        nr_pulses = self.trig_nr_pulses
        freq_sweep_nrpts = dev_proc.freq_sweep_nrpts
        size = freq_sweep_nrpts * nr_pulses
        data = dev_proc.tune_spect_array
        data = data[:size]
        spect = data.reshape(nr_pulses, -1)
        spect = spect[::-1, :]
        return spect


class SITuneCorr(_Device):
    """SI TuneCorr device."""

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
            devname = SITuneCorr.DEVICES.SI
        if devname not in SITuneCorr.DEVICES.ALL:
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
