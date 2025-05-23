"""RF devices."""

import time as _time
import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from .device import Device as _Device, DeviceSet as _DeviceSet


class RFGen(_Device):
    """Wrap the basic features of the RF Generator used in Sirius.

    The Generator is the R&S SMA100A Signal Generator.
    For more informations of the functionalities of this equipment, please
    refer to:
        https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_common_library/dl_manuals/gb_1/s/sma/SMA100A_OperatingManual_en_14.pdf

    This class interacts with an EPICS IOC made for the generator mentioned
    above. More informations on the IOC can be found in:
        https://github.com/lnls-dig/rssmx100a-epics-ioc

    """

    RF_DELTA_MIN = 0.01  # [Hz]
    RF_DELTA_MAX = 15000.0  # [Hz]
    RF_DELTA_RMP = 200  # [Hz]

    PHASE_CONTINUOUS = _get_namedtuple('PhaseContinuous', ('OFF', 'ON'))
    FREQ_OPMODE = _get_namedtuple(
        'FreqOpMode', (
            'CW',  # Continuous wave (regular mode of operation.)
            'SWE',  # Sweep Mode turned on
            'LIST')  # I don't know yet.
        )
    SWEEP_MODE = _get_namedtuple(
        'SweepMode', (
            'AUTO',  # each trigger executes waveform
            'MAN',  # execution is manual
            'STEP')  # each trigger executes one step
        )
    SWEEP_TRIG_SRC = _get_namedtuple(
        'SweepTrigSrc', (
            'AUTO',  # run continuously as soon as mode is configured.
            'SING',  # run single waveform with internal trigger.
            'EXT',   # run single waveform with external trigger.
            'EAUT')  # external trigger tells when to start and stop.
        )
    SWEEP_SPACING = _get_namedtuple(
        'SweepSpacing', (
            'LIN',  # spacing between steps is linear
            'LOG')  # spacing between steps is logarithmic
        )
    SWEEP_SHAPE = _get_namedtuple(
        'SweepShape', (
            'SAWT',  # sawtooth-like waveform
            'TRI')  # triangular waveform
        )
    SWEEP_RETRACE = _get_namedtuple('SweepRetrace', ('OFF', 'ON'))
    SWEEP_RUNNING = _get_namedtuple('SweepRunning', ('OFF', 'ON'))

    class DEVICES:
        """Devices names."""

        AS = 'RF-Gen'
        SPARE = 'RF-SI-Gen'
        ALL = (AS, SPARE)

    PROPERTIES_DEFAULT = (
        'GeneralFreq-SP', 'GeneralFreq-RB',

        'FreqFExeSweep-Cmd',  # execute single sweep
        'FreqRst-Cmd',  # reset sweeps
        'FreqFRunnMode-Mon',  # is sweep running?

        'GeneralFSweep-Sel', 'GeneralFSweep-Sts',  # frequency opmode
        'FreqFSweepMode-Sel', 'FreqFSweepMode-Sts',  # sweep mode
        'TrigFSweepSrc-Sel', 'TrigFSweepSrc-Sts',  # trigger source
        'FreqFSpacMode-Sel', 'FreqFSpacMode-Sts',  # spacing mode
        'FreqFreqRetr-Sel', 'FreqFreqRetr-Sts',  # retrace
        'FreqFreqShp-Sel', 'FreqFreqShp-Sts',  # shape
        'FreqPhsCont-Sts',  # 'FreqPhsCont-Sel', (setpoint is not needed here)

        'FreqFreqSpan-RB', 'FreqFreqSpan-SP',
        'FreqCenterFreq-RB', 'FreqCenterFreq-SP',
        'FreqStartFreq-RB', 'FreqStartFreq-SP',
        'FreqStopFreq-RB', 'FreqStopFreq-SP',
        'FreqFStepLin-RB', 'FreqFStepLin-SP',
        'FreqFStepLog-RB', 'FreqFStepLog-SP',
        'FreqFDwellTime-RB', 'FreqFDwellTime-SP',
        )

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = RFGen.DEVICES.AS

        # check if device exists
        if devname not in RFGen.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def is_phase_continuous(self):
        """."""
        return self['FreqPhsCont-Sts'] == self.PHASE_CONTINUOUS.ON

    @property
    def frequency(self):
        """."""
        return self['GeneralFreq-RB']

    @frequency.setter
    def frequency(self, value):
        delta_max = RFGen.RF_DELTA_RMP  # [Hz]
        freq0 = self.frequency
        if freq0 is None or value is None:
            return
        delta = abs(value-freq0)
        if delta < RFGen.RF_DELTA_MIN or delta > RFGen.RF_DELTA_MAX:
            return
        npoints = int(delta/delta_max) + 2
        freq_span = _np.linspace(freq0, value, npoints)[1:]
        pvo = self.pv_object('GeneralFreq-SP')
        pvo.put(freq_span[0], wait=False)
        for freq in freq_span[1:]:
            _time.sleep(1.0)
            pvo.put(freq, wait=False)
        self['GeneralFreq-SP'] = value

    def set_frequency(self, value, tol=1, timeout=10):
        """Set RF phase and wait until it gets there."""
        self.frequency = value
        return self._wait_float(
            'GeneralFreq-RB', value, abs_tol=tol, timeout=timeout)

    @property
    def freq_opmode(self):
        """Operation mode of the frequency generator.

        Takes the following values:
            0 - 'CW':  Continuous wave (regular mode of operation.)
            1 - 'SWE': Seep Mode turned on.
            2 - 'LIST': I don't know yet.

        """
        return self['GeneralFSweep-Sts']

    @freq_opmode.setter
    def freq_opmode(self, value):
        self._enum_setter('GeneralFSweep-Sel', value, self.FREQ_OPMODE)

    @property
    def freq_opmode_str(self):
        """Operation mode of the frequency generator.

        Takes the following values:
            0 - 'CW':  Continuous wave (regular mode of operation.)
            1 - 'SWE': Seep Mode turned on.
            2 - 'LIST': I don't know yet.

        """
        return self.FREQ_OPMODE._fields[self['GeneralFSweep-Sts']]

    def cmd_freq_opmode_to_continuous_wave(self):
        """."""
        self.freq_opmode = self.FREQ_OPMODE.CW
        return self._wait('GeneralFSweep-Sts', self.FREQ_OPMODE.CW)

    def cmd_freq_opmode_to_sweep(self):
        """."""
        self.freq_opmode = self.FREQ_OPMODE.SWE
        return self._wait('GeneralFSweep-Sts', self.FREQ_OPMODE.SWE)

    @property
    def freq_sweep_is_running(self):
        """Check whether any frequency sweep is in progress."""
        return self['FreqFRunnMode-Mon'] == self.SWEEP_RUNNING.ON

    def wait_freq_sweep_to_finish(self, timeout=10):
        """Wait until the current frequency sweep is finished."""
        return self._wait(
            'FreqFRunnMode-Mon', self.SWEEP_RUNNING.OFF, timeout=timeout)

    def cmd_freq_sweep_start(self):
        """Send an internal trigger to start frequency sweep.

        Only effective when `freq_sweep_trig_src` is in "SING".

        """
        self['FreqFExeSweep-Cmd'] = 1
        return True

    def cmd_freq_sweep_reset(self):
        """Reset current frequency sweep and wait to start new one."""
        self['FreqRst-Cmd'] = 1
        return True

    @property
    def freq_sweep_mode(self):
        """Mode of the frequency sweep.

        Takes the following values:
            0 - 'AUTO': each trigger executes the waveform;
            1 - 'MAN': execution is manual;
            2 - 'STEP': each trigger executes one step of the waveform.

        """
        return self['FreqFSweepMode-Sts']

    @freq_sweep_mode.setter
    def freq_sweep_mode(self, value):
        self._enum_setter('FreqFSweepMode-Sel', value, self.SWEEP_MODE)

    @property
    def freq_sweep_mode_str(self):
        """Mode of the frequency sweep.

        Takes the following values:
            0 - 'AUTO': each trigger executes the waveform;
            1 - 'MAN': execution is manual;
            2 - 'STEP': each trigger executes one step of the waveform.

        """
        return self.SWEEP_MODE._fields[self['FreqFSweepMode-Sts']]

    def cmd_freq_sweep_mode_to_automatic(self):
        """."""
        self.freq_sweep_mode = self.SWEEP_MODE.AUTO
        return self._wait('FreqFSweepMode-Sts', self.SWEEP_MODE.AUTO)

    def cmd_freq_sweep_mode_to_step(self):
        """."""
        self.freq_sweep_mode = self.SWEEP_MODE.STEP
        return self._wait('FreqFSweepMode-Sts', self.SWEEP_MODE.STEP)

    @property
    def freq_sweep_spacing_mode(self):
        """Define the spacing scale between steps of the sweep.

        Takes the following values:
            0 - 'LIN': Constant spaces between steps;
            1 - 'LOG': Logarithmic spaces between steps;

        """
        return self['FreqFSpacMode-Sts']

    @freq_sweep_spacing_mode.setter
    def freq_sweep_spacing_mode(self, value):
        self._enum_setter('FreqFSpacMode-Sel', value, self.SWEEP_SPACING)

    @property
    def freq_sweep_spacing_mode_str(self):
        """Define the spacing scale between steps of the sweep.

        Takes the following values:
            0 - 'LIN': Constant spaces between steps;
            1 - 'LOG': Logarithmic spaces between steps;

        """
        return self.SWEEP_SPACING._fields[self['FreqFSpacMode-Sts']]

    def cmd_freq_sweep_spacing_mode_to_linear(self):
        """."""
        self.freq_sweep_spacing_mode = self.SWEEP_SPACING.LIN
        return self._wait('FreqFSpacMode-Sts', self.SWEEP_SPACING.LIN)

    def cmd_freq_sweep_spacing_mode_to_log(self):
        """."""
        self.freq_sweep_spacing_mode = self.SWEEP_SPACING.LOG
        return self._wait('FreqFSpacMode-Sts', self.SWEEP_SPACING.LOG)

    @property
    def freq_sweep_trig_src(self):
        """Define the trigger source for the sweep.

        Takes the following values:
            0 - 'AUTO': run continuously as soon as `freq_sweep_mode` is
                    changed to `SWE`.
            1 - 'SING': run single waveform with internal trigger.
            2 - 'EXT': run single waveform with external trigger.
            3 - 'EAUT': external trigger tells when to start and stop.

        """
        return self['TrigFSweepSrc-Sts']

    @freq_sweep_trig_src.setter
    def freq_sweep_trig_src(self, value):
        self._enum_setter('TrigFSweepSrc-Sel', value, self.SWEEP_TRIG_SRC)

    @property
    def freq_sweep_trig_src_str(self):
        """Define the trigger source for the sweep.

        Takes the following values:
            0 - 'AUTO': run continuously as soon as `freq_sweep_mode` is
                    changed to `SWE`.
            1 - 'SING': run single waveform with internal trigger.
            2 - 'EXT': run single waveform with external trigger.
            3 - 'EAUT': external trigger tells when to start and stop.

        """
        return self.SWEEP_TRIG_SRC._fields[self['TrigFSweepSrc-Sts']]

    def cmd_freq_sweep_trig_src_to_external(self):
        """."""
        self.freq_sweep_trig_src = self.SWEEP_TRIG_SRC.EXT
        return self._wait('TrigFSweepSrc-Sts', self.SWEEP_TRIG_SRC.EXT)

    def cmd_freq_sweep_trig_src_to_single(self):
        """."""
        self.freq_sweep_trig_src = self.SWEEP_TRIG_SRC.SING
        return self._wait('TrigFSweepSrc-Sts', self.SWEEP_TRIG_SRC.SING)

    def cmd_freq_sweep_trig_src_to_auto(self):
        """."""
        self.freq_sweep_trig_src = self.SWEEP_TRIG_SRC.AUTO
        return self._wait('TrigFSweepSrc-Sts', self.SWEEP_TRIG_SRC.AUTO)

    @property
    def freq_sweep_shape(self):
        """Define the shape of the sweep.

        Takes the following values:
            0 - 'SAWT': sawtooth-like waveform:
                                _           _           _
                              _| |        _| |        _| |
                            _|   |      _|   |      _|   |
                -----|    _|     |    _|     |    _|     |-----
                     |  _|       |  _|       |  _|
                     |_|         |_|         |_|
            1 - 'TRI': triangular waveform:
                                _                   _
                              _| |_               _| |_
                            _|     |_           _|     |_
                -----|    _|         |_       _|         |_    |-----
                     |  _|             |_   _|             |_  |
                     |_|                 |_|                 |_|

        """
        return self['FreqFreqShp-Sts']

    @freq_sweep_shape.setter
    def freq_sweep_shape(self, value):
        self._enum_setter('FreqFreqShp-Sel', value, self.SWEEP_SHAPE)

    @property
    def freq_sweep_shape_str(self):
        """Define the shape of the sweep.

        Takes the following values:
            0 - 'SAWT': sawtooth-like waveform:
                                _           _           _
                              _| |        _| |        _| |
                            _|   |      _|   |      _|   |
                -----|    _|     |    _|     |    _|     |-----
                     |  _|       |  _|       |  _|
                     |_|         |_|         |_|
            1 - 'TRI': triangular waveform:
                                _                   _
                              _| |_               _| |_
                            _|     |_           _|     |_
                -----|    _|         |_       _|         |_    |-----
                     |  _|             |_   _|             |_  |
                     |_|                 |_|                 |_|

        """
        return self.SWEEP_SHAPE._fields[self['FreqFreqShp-Sts']]

    def cmd_freq_sweep_shape_to_sawtooth(self):
        """."""
        self.freq_sweep_shape = self.SWEEP_SHAPE.SAWT
        return self._wait('FreqFreqShp-Sts', self.SWEEP_SHAPE.SAWT)

    def cmd_freq_sweep_shape_to_triangular(self):
        """."""
        self.freq_sweep_shape = self.SWEEP_SHAPE.TRI
        return self._wait('FreqFreqShp-Sts', self.SWEEP_SHAPE.TRI)

    @property
    def freq_sweep_retrace(self):
        """Define whether to return to start freq. after sweep finish.

        Takes the following values:
            0 - 'OFF': return to starting frequency.
            1 - 'ON': stay at last frequency of the sweep.

        """
        return self['FreqFreqRetr-Sts']

    @freq_sweep_retrace.setter
    def freq_sweep_retrace(self, value):
        self._enum_setter('FreqFreqRetr-Sel', value, self.SWEEP_RETRACE)

    @property
    def freq_sweep_retrace_str(self):
        """Define whether to return to start freq. after sweep finish.

        Takes the following values:
            0 - 'OFF': return to starting frequency.
            1 - 'ON': stay at last frequency of the sweep.

        """
        return self.SWEEP_RETRACE._fields[self['FreqFreqRetr-Sts']]

    def cmd_freq_sweep_retrace_turn_off(self):
        """."""
        self.freq_sweep_retrace = self.SWEEP_RETRACE.OFF
        return self._wait('FreqFreqRetr-Sts', self.SWEEP_RETRACE.OFF)

    def cmd_freq_sweep_retrace_turn_on(self):
        """."""
        self.freq_sweep_retrace = self.SWEEP_RETRACE.ON
        return self._wait('FreqFreqRetr-Sts', self.SWEEP_RETRACE.ON)

    @property
    def freq_sweep_span(self):
        """Total span of the frequency sweep in [Hz]."""
        return self['FreqFreqSpan-RB']

    @freq_sweep_span.setter
    def freq_sweep_span(self, value):
        self['FreqFreqSpan-SP'] = float(value)

    @property
    def freq_sweep_center_freq(self):
        """Center frequency of the frequency sweep in [Hz]."""
        return self['FreqCenterFreq-RB']

    @freq_sweep_center_freq.setter
    def freq_sweep_center_freq(self, value):
        self['FreqCenterFreq-SP'] = float(value)

    @property
    def freq_sweep_start_freq(self):
        """Start point of the frequency sweep in [Hz]."""
        return self['FreqStartFreq-RB']

    @freq_sweep_start_freq.setter
    def freq_sweep_start_freq(self, value):
        self['FreqStartFreq-SP'] = float(value)

    @property
    def freq_sweep_stop_freq(self):
        """Other extreme of the frequency sweep in [Hz]."""
        return self['FreqStopFreq-RB']

    @freq_sweep_stop_freq.setter
    def freq_sweep_stop_freq(self, value):
        self['FreqStopFreq-SP'] = float(value)

    @property
    def freq_sweep_step_freq_linear(self):
        """Step used if `freq_sweep_spacing_mode` is linear, in [Hz]."""
        return self['FreqFStepLin-RB']

    @freq_sweep_step_freq_linear.setter
    def freq_sweep_step_freq_linear(self, value):
        self['FreqFStepLin-SP'] = float(value)

    @property
    def freq_sweep_step_freq_log(self):
        """Step used if `freq_sweep_spacing_mode` is linear, in [%]."""
        return self['FreqFStepLog-RB']

    @freq_sweep_step_freq_log.setter
    def freq_sweep_step_freq_log(self, value):
        self['FreqFStepLog-SP'] = float(value)

    @property
    def freq_sweep_step_time(self):
        """Time to stay in each step of the sweep in [s]."""
        return self['FreqFDwellTime-RB']

    @freq_sweep_step_time.setter
    def freq_sweep_step_time(self, value):
        self['FreqFDwellTime-SP'] = float(value)

    def configure_freq_sweep(
            self, ampl, nr_steps, duration, sawtooth=True, centered=True,
            increasing=True, retrace=False):
        """Configure generator to create a single frequency sweep.

        Currently the sweep will be ready to be triggered by an internal
        trigger (see method `cmd_freq_sweep_start`).

        Args:
            ampl (float): Amplitude of the sweep in Hz. NOTE: Be careful not
                to create discontinuities larger than 200 Hz in the frequency,
                which could make the LLRF lose track of the reference
                frequency.
            nr_steps (int): number of steps to divide the ramp. Notice that if
                the triangular waveform is chosen, the actual number of steps
                will be 2 times minus 1 the value provided here. Must be
                larger than 1, so stepsize is at least equal to span.
            duration (float): total desired duration in seconds.
            sawtooth (bool, optional): If True, then the waveform will be se to
                sawtooth. If False, the triangular waveform will be chosen.
                Defaults to True.
            centered (bool, optional): If True the current frequency will be
                centered in the ramp. If False, it will be equal to the
                starting frequency. Defaults to True.
            increasing (bool, optional): Whether the ramp will start at the
                smaller frequency and go to the higher one (True) or
                vice-versa (False). Defaults to True.
            retrace (bool, optional): Whether (True) or not (False) to go back
                to the current frequency after finish the sweep.
                Detaults to False.

        Returns:
            ampl (float): real amplitude that will be used in sweep.

        Raises:
            ValueError: raised if nr_steps is <= 1.

        """
        ampl = abs(ampl)
        nr_steps = int(nr_steps)
        if nr_steps <= 1:
            raise ValueError('Input nr_steps must be larger than 1.')
        nr_interv = nr_steps-1

        span = 2*ampl
        stepsize = round(span / nr_interv, 2)
        span = nr_interv * stepsize
        span *= 1 if increasing else -1
        stepsize *= 1 if increasing else -1
        curr_freq = self.frequency
        ampl = span/2

        if sawtooth:
            self.cmd_freq_sweep_shape_to_sawtooth()
            dwelltime = duration / nr_steps
        else:
            self.cmd_freq_sweep_shape_to_triangular()
            dwelltime = duration / (2*nr_steps - 1)
        self.freq_sweep_step_time = dwelltime

        # NOTE: Depending whether the sweep is centered or not it is easier to
        # set the center_freq and span or start and stop
        if centered:
            self.freq_sweep_center_freq = curr_freq
            self.freq_sweep_span = span
        else:
            self.freq_sweep_start_freq = curr_freq
            self.freq_sweep_stop_freq = curr_freq + span

        if retrace:
            self.cmd_freq_sweep_retrace_turn_on()
        else:
            self.cmd_freq_sweep_retrace_turn_off()

        self.cmd_freq_sweep_spacing_mode_to_linear()
        self.freq_sweep_step_freq_linear = stepsize

        self.cmd_freq_sweep_mode_to_automatic()
        self.cmd_freq_sweep_trig_src_to_single()

        # NOTE: do not change freq_opmode here, because this will make the
        #  generator automatically go to the starting frequency, regardless of
        # the trigger type:
        # self.cmd_freq_opmode_to_sweep()
        return ampl


class ASLLRF(_Device):
    """AS LLRF."""

    PROPERTIES_INTERLOCK = (
        'FIMLLRF1-Sel', 'FIMLLRF1-Sts', 'IntlkAll-Mon',
        'FIMManual-Sel', 'FIMManual-Sts',
        'IntlkManual-Sel', 'IntlkManual-Sts', 'IntlkReset-Cmd',
        'Inp1Intlk-Mon', 'Inp2Intlk-Mon',
    )

    VoltIncRates = _get_namedtuple('VoltIncRates', (
        'vel_0p01', 'vel_0p03', 'vel_0p1', 'vel_0p25', 'vel_0p5', 'vel_1p0',
        'vel_2p0', 'vel_4p0', 'vel_6p0', 'vel_8p0', 'vel_10p0', 'vel_15p0',
        'vel_20p0', 'vel_30p0', 'vel_50p0', 'Immediately'))
    PhsIncRates = _get_namedtuple('PhsIncRates', (
        'vel_0p1', 'vel_0p2', 'vel_0p5', 'vel_1p0', 'vel_2p0', 'vel_5p0',
        'vel_10p0', 'Immediately'))

    class DEVICES:
        """Devices names."""

        BO = 'RA-RaBO01:RF-LLRF'
        SIA = 'RA-RaSIA01:RF-LLRF'
        SIB = 'RA-RaSIB01:RF-LLRF'
        ALL = (BO, SIA, SIB)

    def __new__(cls, devname, props2init='all'):
        """."""
        # check if device exists
        if devname not in ASLLRF.DEVICES.ALL:
            raise NotImplementedError(devname)

        if 'SI' in devname:
            obj = _SILLRF(devname, props2init)
        elif 'BO' in devname:
            obj = _BOLLRF(devname, props2init)

        obj.system_nickname = cls.get_system_nickname(devname)
        return obj

    @staticmethod
    def get_system_nickname(devname):
        """."""
        if devname == ASLLRF.DEVICES.BO:
            return "BO"
        if devname == ASLLRF.DEVICES.SIA:
            return "SI-A"
        if devname == ASLLRF.DEVICES.SIB:
            return "SI-B"
        return ""


class _BaseLLRF(_Device):
    """Base LLRF."""

    PROPERTIES_DEFAULT = ASLLRF.PROPERTIES_INTERLOCK + (
        'SL-Sel', 'SL-Sts',
        'PLRef-RB', 'PLRef-SP', 'SLRefPhs-Mon', 'SLInpPhs-Mon',
        'ALRef-SP', 'ALRef-RB', 'SLRefAmp-Mon', 'SLInpAmp-Mon',
        'Detune-SP', 'Detune-RB', 'TuneDephs-Mon',
        'RmpPhsBot-SP', 'RmpPhsBot-RB', 'RmpPhsTop-SP', 'RmpPhsTop-RB',
        'RmpEnbl-Sel', 'RmpEnbl-Sts', 'RmpReady-Mon',
        'AmpIncRate-RB', 'AmpIncRate-SP',
        'PhsIncRate-RB', 'PhsIncRate-SP',
        'AmpRefMin-RB', 'AmpRefMin-SP', 'PhsRefMin-RB', 'PhsRefMin-SP',
        'CondEnbl-Sts', 'CondEnbl-Sel', 'CondDuty-RB', 'CondDuty-SP',
        'CondDutyCycle-Mon', 'PhShCav-SP', 'PhShCav-RB',
        'SLPILim-SP', 'SLPILim-RB', 'SLKI-SP', 'SLKI-RB', 'SLKP-SP', 'SLKI-RB',
    )

    def __init__(self, devname, props2init='all'):
        """."""
        # check if device exists
        if devname not in ASLLRF.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def slow_loop_state(self):
        """Slow loop state."""
        return self['SL-Sts']

    @slow_loop_state.setter
    def slow_loop_state(self, value):
        self['SL-Sel'] = int(value)

    def set_slow_loop_state(self, value, timeout=None):
        """Wait for slow loop state to reach `value`."""
        self.slow_loop_state = value
        return self._wait('SL-Sts', value, timeout=timeout)

    @property
    def is_cw(self):
        """Is CW."""
        return not self.rmp_enable

    @property
    def rmp_enable(self):
        """Ramp enable."""
        return self['RmpEnbl-Sts']

    @rmp_enable.setter
    def rmp_enable(self, value):
        self['RmpEnbl-Sel'] = value

    @property
    def rmp_ready(self):
        """Ramp ready."""
        return self['RmpReady-Mon']

    def set_rmp_enable(self, value, timeout=None, wait_ready=False):
        """Set ramp enable."""
        self.rmp_enable = value
        if not self._wait('RmpEnbl-Sts', value, timeout=timeout):
            return False
        if wait_ready:
            return self._wait('RmpReady-Mon', value, timeout=timeout)
        return True

    @property
    def phase_top(self):
        """."""
        return self['RmpPhsTop-RB']

    @phase_top.setter
    def phase_top(self, value):
        self['RmpPhsTop-SP'] = self._wrap_phase(value)

    @property
    def phase_bottom(self):
        """."""
        return self['RmpPhsBot-RB']

    @phase_bottom.setter
    def phase_bottom(self, value):
        self['RmpPhsBot-SP'] = self._wrap_phase(value)

    @property
    def phase_mon(self):
        """."""
        return self['SLInpPhs-Mon']

    @property
    def phase_ref(self):
        """."""
        return self['SLRefPhs-Mon']

    @property
    def phase_sp(self):
        """."""
        return self['PLRef-SP']

    @property
    def phase(self):
        """."""
        return self['PLRef-RB']

    @phase.setter
    def phase(self, value):
        self['PLRef-SP'] = self._wrap_phase(value)

    @property
    def phase_incrate_str(self):
        """."""
        return ASLLRF.PhsIncRates._fields[self['PhsIncRate-RB']]

    @property
    def phase_incrate(self):
        """."""
        return self['PhsIncRate-RB']

    @phase_incrate.setter
    def phase_incrate(self, value):
        self._enum_setter('PhsIncRate-SP', value, ASLLRF.PhsIncRates)

    def set_phase(self, value, tol=0.2, timeout=10, wait_mon=False):
        """Set RF phase and wait until it gets there."""
        self.phase = value
        pv2wait = 'SLInpPhs-Mon' if wait_mon else 'SLRefPhs-Mon'
        return self._wait_float(pv2wait, value, abs_tol=tol, timeout=timeout)

    def phase_shift_cav_sp(self):
        """."""
        return self['PhShCav-SP']

    @property
    def phase_shift_cav(self):
        """."""
        return self['PhShCav-RB']

    @phase_shift_cav.setter
    def phase_shift_cav(self, value):
        self['PhShCav-SP'] = self._wrap_phase(value)

    @property
    def phase_refmin_sp(self):
        """."""
        return self['PhsRefMin-SP']

    @property
    def phase_refmin(self):
        """."""
        return self['PhsRefMin-RB']

    @phase_refmin.setter
    def phase_refmin(self, value):
        self['PhsRefMin-SP'] = value

    @property
    def voltage_mon(self):
        """."""
        return self['SLInpAmp-Mon']

    @property
    def voltage_ref(self):
        """."""
        return self['SLRefAmp-Mon']

    @property
    def voltage_sp(self):
        """."""
        return self['ALRef-SP']

    @property
    def voltage(self):
        """."""
        return self['ALRef-RB']

    @voltage.setter
    def voltage(self, value):
        self['ALRef-SP'] = value

    @property
    def voltage_incrate_str(self):
        """Voltage increase rate enum string."""
        return ASLLRF.VoltIncRates._fields[self['AmpIncRate-RB']]

    @property
    def voltage_incrate(self):
        """Voltage increase rate."""
        return self['AmpIncRate-RB']

    @voltage_incrate.setter
    def voltage_incrate(self, value):
        self._enum_setter('AmpIncRate-SP', value, ASLLRF.VoltIncRates)

    def set_voltage_incrate(self, value, timeout=None):
        """Set and wait voltage increase rate to reach `value`."""
        self.voltage_incrate = value
        return self._wait('AmpIncRate-RB', value, timeout=timeout)

    def set_voltage(self, value, tol=1, timeout=10, wait_mon=False):
        """Set RF voltage and wait until it gets there."""
        self.voltage = value
        pv2wait = 'SLInpAmp-Mon' if wait_mon else 'SLRefAmp-Mon'
        return self._wait_float(pv2wait, value, abs_tol=tol, timeout=timeout)

    @property
    def voltage_refmin_sp(self):
        """."""
        return self['AmpRefMin-SP']

    @property
    def voltage_refmin(self):
        """."""
        return self['AmpRefMin-RB']

    @voltage_refmin.setter
    def voltage_refmin(self, value):
        self['AmpRefMin-SP'] = value

    @property
    def conditioning_state(self):
        """."""
        return self['CondEnbl-Sts']

    @conditioning_state.setter
    def conditioning_state(self, value):
        self['CondEnbl-Sel'] = bool(value)

    def cmd_turn_on_conditioning(self, timeout=10):
        """Turn on conditioning mode."""
        self.conditioning_state = 1
        return self._wait('CondEnbl-Sts', 1, timeout=timeout)

    def cmd_turn_off_conditioning(self, timeout=10):
        """Turn off conditioning mode."""
        self.conditioning_state = 0
        return self._wait('CondEnbl-Sts', 0, timeout=timeout)

    @property
    def conditioning_duty_cycle_mon(self):
        """Duty cycle in %."""
        return self['CondDutyCycle-Mon']

    @property
    def conditioning_duty_cycle(self):
        """Duty cycle in %."""
        return self['CondDuty-RB']

    @conditioning_duty_cycle.setter
    def conditioning_duty_cycle(self, value):
        self['CondDuty-SP'] = value

    def set_duty_cycle(self, value, tol=1, timeout=10, wait_mon=True):
        """Set RF phase and wait until it gets there."""
        self.conditioning_duty_cycle = value
        pv2wait = 'CondDuty-RB' if wait_mon else 'CondDutyCycle-Mon'
        return self._wait_float(pv2wait, value, abs_tol=tol, timeout=timeout)

    @property
    def detune(self):
        """."""
        return self['Detune-RB']

    @detune.setter
    def detune(self, value):
        self['Detune-SP'] = value

    @property
    def detune_error(self):
        """."""
        return self['TuneDephs-Mon']

    @staticmethod
    def _wrap_phase(phase):
        """Phase must be in [-180, +180] interval."""
        return (phase + 180) % 360 - 180

    # interlock properties
    @property
    def fast_interlock_monitor_orbit(self):
        """."""
        return self['FIMLLRF1-Sts']

    @fast_interlock_monitor_orbit.setter
    def fast_interlock_monitor_orbit(self, value):
        """."""
        self['FIMLLRF1-Sel'] = value

    @property
    def fast_interlock_monitor_manual(self):
        """."""
        return self['FIMManual-Sts']

    @fast_interlock_monitor_manual.setter
    def fast_interlock_monitor_manual(self, value):
        """."""
        self['FIMManual-Sel'] = value

    @property
    def interlock_manual(self):
        """."""
        return self['IntlkManual-Sts']

    @interlock_manual.setter
    def interlock_manual(self, value):
        """."""
        self['IntlkManual-Sel'] = value

    @property
    def interlock_mon(self):
        """."""
        return self['IntlkAll-Mon']

    @property
    def interlock_input1_mon(self):
        """."""
        return self['Inp1Intlk-Mon']

    @property
    def interlock_input2_mon(self):
        """."""
        return self['Inp2Intlk-Mon']

    def cmd_reset_interlock(self, wait=1):
        """Reset interlocks."""
        self['IntlkReset-Cmd'] = 1
        _time.sleep(wait)
        self['IntlkReset-Cmd'] = 0

    def loop_pi_limit_sp(self):
        return self['SLPILim-SP']

    @property
    def loop_pi_limit(self):
        return self['SLPILim-RB']

    @loop_pi_limit.setter
    def loop_pi_limit(self, value):
        self['SLPILim-SP'] = value

    def loop_ki_sp(self):
        return self['SLKI-SP']

    @property
    def loop_ki(self):
        return self['SLKI-RB']

    @loop_ki.setter
    def loop_ki(self, value):
        self['SLKI-SP'] = value

    def loop_kp_sp(self):
        return self['SLKP-SP']

    @property
    def loop_kp(self):
        return self['SLKP-RB']

    @loop_kp.setter
    def loop_kp(self, value):
        self['SLKP-SP'] = value


class _BOLLRF(_BaseLLRF):
    """."""

    # fieldflatness properties that are exclusive for P5Cav at BO
    PROPERTIES_DEFAULT = _BaseLLRF.PROPERTIES_DEFAULT + (
        'FFOn-Mon', 'FFEnbl-Sts', 'FFEnbl-Sel', 'FFDir-Sts', 'FFDir-Sel',
        'FFGainCell2-RB', 'FFGainCell2-SP', 'FFGainCell4-RB', 'FFGainCell4-SP',
        'FFDeadBand-RB', 'FFDeadBand-SP', 'FFCell2-Mon', 'FFCell4-Mon',
        'FFError-Mon',
        )

    @property
    def field_flatness_acting(self):
        """Return whether the field flatness loop is acting."""
        return self['FFOn-Mon']

    @property
    def field_flatness_enable(self):
        """Return whether the field flatness loop is enabled."""
        return self['FFEnbl-Sts']

    @field_flatness_enable.setter
    def field_flatness_enable(self, value):
        """Control state of field flatness loop."""
        self['FFEnbl-Sel'] = bool(value)

    @property
    def field_flatness_position(self):
        """Return the field flatness position."""
        return self['FFDir-Sts']

    @field_flatness_position.setter
    def field_flatness_position(self, value):
        """Control the field flatness position."""
        self['FFDir-Sel'] = bool(value)

    @property
    def field_flatness_gain1(self):
        """Return the gain of the first cell controlled."""
        return self['FFGainCell2-RB']

    @field_flatness_gain1.setter
    def field_flatness_gain1(self, value):
        """Control the gain of the first cell controlled."""
        self['FFGainCell2-SP'] = value

    @property
    def field_flatness_gain2(self):
        """Return the gain of the second cell controle."""
        return self['FFGainCell4-RB']

    @field_flatness_gain2.setter
    def field_flatness_gain2(self, value):
        """Control the gain of the second cell controlled."""
        self['FFGainCell4-SP'] = value

    @property
    def field_flatness_deadband(self):
        """Return the loop action deadband in [%]."""
        return self['FFDeadBand-RB']

    @field_flatness_deadband.setter
    def field_flatness_deadband(self, value):
        """Control the loop action deadband in [%]."""
        self['FFDeadBand-SP'] = value

    @property
    def field_flatness_amp1(self):
        """Amplitude of the first cell controled in [mV]."""
        return self['FFCell2-Mon']

    @property
    def field_flatness_amp2(self):
        """Amplitude of the second cell controled in [mV]."""
        return self['FFCell4-Mon']

    @property
    def field_flatness_error(self):
        """Return the amplitude error in [mV]."""
        return self['FFError-Mon']


class _SILLRF(_BaseLLRF):
    pass


class BORFCavMonitor(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        BO = 'BO-05D:RF-P5Cav'

    PROPERTIES_DEFAULT = (
        'FwdPwrW-Mon', 'RevPwrW-Mon',
        'Cell3TopPwrW-Mon', 'Cell3BotPwrW-Mon', 'PwrRFIntlk-Mon', 'Sts-Mon',
        'Cell1PwrW-Mon', 'Cell2PwrW-Mon', 'Cell3PwrW-Mon', 'Cell4PwrW-Mon',
        'Cell5PwrW-Mon', 'Cylin1T-Mon', 'Cylin2T-Mon', 'Cylin3T-Mon',
        'Cylin4T-Mon', 'Cylin5T-Mon', 'CoupT-Mon',
        'Cell3BotVGap-Mon', 'Cell3TopVGap-Mon',
        )

    def __init__(self, props2init='all'):
        """."""
        super().__init__(BORFCavMonitor.DEVICES.BO, props2init=props2init)

    @property
    def status(self):
        """."""
        return self['Sts-Mon']

    @property
    def power_interlock(self):
        """."""
        return self['PwrRFIntlk-Mon']

    @property
    def power_top(self):
        """Power at Top in [W]."""
        return self['Cell3TopPwrW-Mon']

    @property
    def power_bottom(self):
        """Power at Bottom in [W]."""
        return self['Cell3BotPwrW-Mon']

    @property
    def power_reverse(self):
        """Reverse power in [W]."""
        return self['RevPwrW-Mon']

    @property
    def power_forward(self):
        """Forward power in [W]."""
        return self['FwdPwrW-Mon']

    @property
    def power_cell1(self):
        """Power on Cell1 in [W]."""
        return self['Cell1PwrW-Mon']

    @property
    def power_cell2(self):
        """Power on Cell2 in [W]."""
        return self['Cell2PwrW-Mon']

    @property
    def power_cell3(self):
        """Power on Cell3 in [W]."""
        return self['Cell3PwrW-Mon']

    @property
    def power_cell4(self):
        """Power on Cell4 in [W]."""
        return self['Cell4PwrW-Mon']

    @property
    def power_cell5(self):
        """Power on Cell5 in [W]."""
        return self['Cell5PwrW-Mon']

    @property
    def temp_coupler(self):
        """."""
        return self['CoupT-Mon']

    @property
    def temp_cell1(self):
        """."""
        return self['Cylin1T-Mon']

    @property
    def temp_cell2(self):
        """."""
        return self['Cylin2T-Mon']

    @property
    def temp_cell3(self):
        """."""
        return self['Cylin3T-Mon']

    @property
    def temp_cell4(self):
        """."""
        return self['Cylin4T-Mon']

    @property
    def temp_cell5(self):
        """."""
        return self['Cylin5T-Mon']

    @property
    def gap_voltage_bottom(self):
        """Gap Voltage in [V]."""
        return self['Cell3BotVGap-Mon']

    @property
    def gap_voltage_top(self):
        """Gap Voltage in [V]."""
        return self['Cell3TopVGap-Mon']


class SIRFCavMonitor(_Device):
    """TODO: UPDATE WITH PVS FOR SC CAVITIES."""

    class DEVICES:
        """Devices names."""

        SIA = 'SI-03SP:RF-SRFCav-A'
        SIB = 'SI-03SP:RF-SRFCav-B'
        ALL = (SIA, SIB, )

    PROPERTIES_DEFAULT = (
        'PwrW-Mon', 'PwrdBm-Mon', 'Amp-Mon',
        'FwdPwrW-Mon', 'FwdPwrdBm-Mon', 'FwdAmp-Mon',
        'RevPwrW-Mon', 'RevPwrdBm-Mon', 'RevAmp-Mon',
        'TunerMoveDown-Mon', 'TunerMoveUp-Mon', 'VGap-Mon',
        )

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in SIRFCavMonitor.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def system_nickname(self):
        """."""
        if self.devname == ASLLRF.DEVICES.SIA:
            return "A"
        if self.devname == ASLLRF.DEVICES.SIB:
            return "B"
        return ""

    @property
    def gap_voltage(self):
        """Gap voltage in [V]."""
        return self['VGap-Mon']

    @property
    def power(self):
        """Power at cavity in [W]."""
        return self['PwrW-Mon']

    @property
    def power_dbm(self):
        """Power at cavity in [dBm]."""
        return self['PwrdBm-Mon']

    @property
    def amplitude(self):
        """Amplitude at cavity in [mV]."""
        return self['Amp-Mon']

    @property
    def power_forward(self):
        """Forward power in [W]."""
        return self['FwdPwrW-Mon']

    @property
    def power_forward_dbm(self):
        """Forward power in [dBm]."""
        return self['FwdPwrdBm-Mon']

    @property
    def power_reverse(self):
        """Reverse power in [W]."""
        return self['RevPwrW-Mon']

    @property
    def power_reverse_dbm(self):
        """Reverse power in [dBm]."""
        return self['RevPwrdBm-Mon']

    @property
    def amplitude_forward(self):
        """Forward amplitude in [mV]."""
        return self['FwdAmp-Mon']

    @property
    def amplitude_reverse(self):
        """Reverse amplitude in [mV]."""
        return self['RevAmp-Mon']

    @property
    def tuner_moving_down(self):
        """Is tuner moving down?."""
        return self['TunerMoveDown-Mon']

    @property
    def tuner_moving_up(self):
        """Is tuner moving up?."""
        return self['TunerMoveUp-Mon']


class RFCav(_DeviceSet):
    """."""

    class DEVICES:
        """Devices names."""

        BO = 'BO-05D:RF-P5Cav'
        SIA = 'SI-03SP:RF-SRFCav-A'
        SIB = 'SI-03SP:RF-SRFCav-B'
        ALL = (BO, SIA, SIB)

    def __init__(self, devname, props2init='all'):
        """RFCav DeviceSet.

        Args:
            devname (str): choose the accelerator cavity in RFCav.DEVICES
            props2init (str, optional): 'all' to connect with all PVs or
                bool(props2init) == False to initialize without any
                connection. Defaults to 'all'.

        """
        # check if device exists
        if devname not in RFCav.DEVICES.ALL:
            raise NotImplementedError(devname)

        _isall = isinstance(props2init, str) and props2init.lower() == 'all'
        if not _isall and props2init:
            raise ValueError(
                "props2init must be 'all' or bool(props2init) == False")

        self.dev_rfgen = RFGen(props2init=props2init)
        if devname == RFCav.DEVICES.SIA:
            self.dev_llrf = ASLLRF(ASLLRF.DEVICES.SIA, props2init=props2init)
            self.dev_cavmon = SIRFCavMonitor(
                SIRFCavMonitor.DEVICES.SIA, props2init=props2init)
        elif devname == RFCav.DEVICES.SIB:
            self.dev_llrf = ASLLRF(ASLLRF.DEVICES.SIB, props2init=props2init)
            self.dev_cavmon = SIRFCavMonitor(
                SIRFCavMonitor.DEVICES.SIB, props2init=props2init)
        elif devname == RFCav.DEVICES.BO:
            self.dev_llrf = ASLLRF(ASLLRF.DEVICES.BO, props2init=props2init)
            self.dev_cavmon = BORFCavMonitor(props2init=props2init)
        devices = (self.dev_rfgen, self.dev_llrf, self.dev_cavmon)

        # call base class constructor
        super().__init__(devices, devname=devname)

    @property
    def is_cw(self):
        """."""
        return self.dev_llrf.is_cw

    @property
    def power(self):
        """."""
        return self.dev_cavmon.get_power(self.is_cw)

    def set_voltage(self, value, timeout=10, tol=1, wait_mon=False):
        """."""
        return self.dev_llrf.set_voltage(
            value, tol=tol, timeout=timeout, wait_mon=wait_mon)

    def set_phase(self, value, timeout=10, tol=0.2, wait_mon=False):
        """."""
        return self.dev_llrf.set_phase(
            value, tol=tol, timeout=timeout, wait_mon=wait_mon)

    def set_frequency(self, value, timeout=10, tol=0.05):
        """."""
        return self.dev_rfgen.set_frequency(value, tol=tol, timeout=timeout)


class RFKillBeam(_DeviceSet):
    """RF Kill Beam Button."""

    TIMEOUT_WAIT = 10  # [s]

    def __init__(self):
        """Init."""
        props2init = ASLLRF.PROPERTIES_INTERLOCK
        si_a = ASLLRF(devname=ASLLRF.DEVICES.SIA, props2init=props2init)
        si_b = ASLLRF(devname=ASLLRF.DEVICES.SIB, props2init=props2init)
        devs = [si_a, si_b]
        super().__init__(devices=devs, devname='SI-Glob:RF-KillBeam')

    def cmd_kill_beam(self):
        """Kill beam."""
        if not self.wait_for_connection(self.TIMEOUT_WAIT):
            return [False, 'Could not read RF PVs.']

        for llrf in self.devices:
            llrf.interlock_manual = 1
        _time.sleep(1)
        for llrf in self.devices:
            llrf.interlock_manual = 0
        return [True, '']


class SILLRFPreAmp(_Device):
    """SILLRF Pre Amplifier."""

    class DEVICES:
        """Devices names."""
        # Cavity A
        SSA1 = 'RA-ToSIA01:RF-CtrlPanel'
        SSA2 = 'RA-ToSIA02:RF-CtrlPanel'
        # Cavity B
        SSA3 = 'RA-ToSIB03:RF-CtrlPanel'
        SSA4 = 'RA-ToSIB04:RF-CtrlPanel'
        ALL = (SSA1, SSA2, SSA3, SSA4)

    PROPERTIES_DEFAULT = (
        'PINSwEnbl-Cmd', 'PINSwDsbl-Cmd', 'PINSwSts-Mon',
    )

    def __init__(self, devname, props2init='all'):
        if devname not in SILLRFPreAmp.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    def cmd_enable_pinsw(self, timeout=None, wait_mon=True):
        """Enable PINSw 1."""
        self['PINSwEnbl-Cmd'] = 1
        _time.sleep(1)
        self['PINSwEnbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PINSwSts-Mon', 1, timeout=timeout)
        return True

    def cmd_disable_pinsw(self, timeout=None, wait_mon=True):
        """Disable PINSw 1."""
        self['PINSwDsbl-Cmd'] = 1
        _time.sleep(1)
        self['PINSwDsbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PINSwSts-Mon', 0, timeout=timeout)
        return True


class BOLLRFPreAmp(_Device):
    """BOLLRF Pre Amplifier."""

    class DEVICES:
        """Devices names."""

        BO01 = 'RA-RaBO01:RF-LLRFPreAmp'
        ALL = (BO01, )

    PROPERTIES_DEFAULT = (
        'PinSwEnbl-Cmd', 'PinSwDsbl-Cmd', 'PinSw-Mon',
    )

    def __init__(self, devname='', props2init='all'):
        if not devname:
            devname = BOLLRFPreAmp.DEVICES.BO01
        if devname not in BOLLRFPreAmp.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    def cmd_enable_pinsw(self, timeout=None, wait_mon=True):
        """Enable PINSw."""
        self['PinSwEnbl-Cmd'] = 1
        _time.sleep(1)
        self['PinSwEnbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PinSw-Mon', 1, timeout=timeout)
        return True

    def cmd_disable_pinsw(self, timeout=None, wait_mon=True):
        """Disable PINSw."""
        self['PinSwDsbl-Cmd'] = 1
        _time.sleep(1)
        self['PinSwDsbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PinSw-Mon', 0, timeout=timeout)
        return True


class SIRFDCAmp(_Device):
    """SI RF DC/TDK amplifier."""

    class DEVICES:
        """Devices names."""
        # Cavity A
        SSA1 = 'RA-ToSIA01:RF-TDKSource'
        SSA2 = 'RA-ToSIA02:RF-TDKSource'
        # Cavity B
        SSA3 = 'RA-ToSIB03:RF-TDKSource'
        SSA4 = 'RA-ToSIB04:RF-TDKSource'
        ALL = (SSA1, SSA2, SSA3, SSA4)

    PROPERTIES_DEFAULT = (
        'PwrDCEnbl-Cmd', 'PwrDCDsbl-Cmd', 'PwrDC-Mon',
    )

    def __init__(self, devname, props2init='all'):
        if devname not in SIRFDCAmp.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    def cmd_enable(self, timeout=None, wait_mon=True):
        """Enable."""
        self['PwrDCEnbl-Cmd'] = 1
        _time.sleep(1)
        self['PwrDCEnbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PwrDC-Mon', 1, timeout=timeout)
        return True

    def cmd_disable(self, timeout=None, wait_mon=True):
        """Disable."""
        self['PwrDCDsbl-Cmd'] = 1
        _time.sleep(1)
        self['PwrDCDsbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PwrDC-Mon', 0, timeout=timeout)
        return True


class BORFDCAmp(_Device):
    """BO RF DC/DC amplifier."""

    class DEVICES:
        """Devices names."""

        SSA = 'RA-ToBO:RF-SSAmpTower'
        ALL = (SSA, )

    PROPERTIES_DEFAULT = (
        'PwrCnvEnbl-Sel', 'PwrCnvDsbl-Sel', 'PwrCnv-Sts',
    )

    def __init__(self, devname='', props2init='all'):
        if not devname:
            devname = BORFDCAmp.DEVICES.SSA
        if devname not in BORFDCAmp.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    def cmd_enable(self, timeout=None, wait_mon=True):
        """Enable."""
        self['PwrCnvEnbl-Sel'] = 1
        _time.sleep(1)
        self['PwrCnvEnbl-Sel'] = 0
        if wait_mon:
            return self._wait('PwrCnv-Sts', 1, timeout=timeout)
        return True

    def cmd_disable(self, timeout=None, wait_mon=True):
        """Disable."""
        self['PwrCnvDsbl-Sel'] = 1
        _time.sleep(1)
        self['PwrCnvDsbl-Sel'] = 0
        if wait_mon:
            return self._wait('PwrCnv-Sts', 0, timeout=timeout)
        return True


class SIRFACAmp(_Device):
    """SI RF AC/TDK amplifier."""

    class DEVICES:
        """Devices names."""
        # Cavity A
        SSA1 = 'RA-ToSIA01:RF-ACPanel'
        SSA2 = 'RA-ToSIA02:RF-ACPanel'
        # Cavity B
        SSA3 = 'RA-ToSIB03:RF-ACPanel'
        SSA4 = 'RA-ToSIB04:RF-ACPanel'
        ALL = (SSA1, SSA2, SSA3, SSA4)

    PROPERTIES_DEFAULT = (
        'PwrACEnbl-Cmd', 'PwrACDsbl-Cmd', 'PwrAC-Mon',
    )

    def __init__(self, devname, props2init='all'):
        if devname not in SIRFACAmp.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    def cmd_enable(self, timeout=None, wait_mon=True):
        """Enable."""
        self['PwrACEnbl-Cmd'] = 1
        _time.sleep(1)
        self['PwrACEnbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PwrAC-Mon', 1, timeout=timeout)
        return True

    def cmd_disable(self, timeout=None, wait_mon=True):
        """Disable."""
        self['PwrACDsbl-Cmd'] = 1
        _time.sleep(1)
        self['PwrACDsbl-Cmd'] = 0
        if wait_mon:
            return self._wait('PwrAC-Mon', 0, timeout=timeout)
        return True


class BORF300VDCAmp(_Device):
    """BO RF 300VDC amplifier."""

    class DEVICES:
        """Devices names."""

        SSA = 'RA-ToBO:RF-ACDCPanel'
        ALL = (SSA, )

    PROPERTIES_DEFAULT = (
        '300VdcEnbl-Sel', '300VdcDsbl-Sel', '300Vdc-Sts',
    )

    def __init__(self, devname=None, props2init='all'):
        if not devname:
            devname = BORF300VDCAmp.DEVICES.SSA
        if devname not in BORF300VDCAmp.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    def cmd_enable(self, timeout=None, wait_mon=True):
        """Enable."""
        self['300VdcEnbl-Sel'] = 1
        _time.sleep(1)
        self['300VdcEnbl-Sel'] = 0
        if wait_mon:
            return self._wait('300Vdc-Sts', 1, timeout=timeout)
        return True

    def cmd_disable(self, timeout=None, wait_mon=True):
        """Disable."""
        self['300VdcDsbl-Sel'] = 1
        _time.sleep(1)
        self['300VdcDsbl-Sel'] = 0
        if wait_mon:
            return self._wait('300Vdc-Sts', 0, timeout=timeout)
        return True
