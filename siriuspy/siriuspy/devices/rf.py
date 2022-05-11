"""RF devices."""

import time as _time
import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from .device import DeviceNC as _DeviceNC, Devices as _Devices


class RFGen(_DeviceNC):
    """Wrap the basic features of the RF Generator used in Sirius.

    The Generator is the R&S SMA100A Signal Generator.
    For more informations of the functionalities of this equipment, please
    refer to:
        https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_common_library/dl_manuals/gb_1/s/sma/SMA100A_OperatingManual_en_14.pdf

    This class interacts with an EPICS IOC made for the generator mentioned
    above. More informations on the IOC can be found in:
        https://github.com/lnls-dig/rssmx100a-epics-ioc

    """

    RF_DELTA_MIN = 0.1  # [Hz]
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

    _properties = (
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

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = RFGen.DEVICES.AS

        # check if device exists
        if devname not in RFGen.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=RFGen._properties)

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
        self._pvs['GeneralFreq-SP'].put(freq_span[0], wait=False)
        for freq in freq_span[1:]:
            _time.sleep(1.0)
            self._pvs['GeneralFreq-SP'].put(freq, wait=False)
        self['GeneralFreq-SP'] = value

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


class ASLLRF(_DeviceNC):
    """AS LLRF."""

    class DEVICES:
        """Devices names."""

        BO = 'BR-RF-DLLRF-01'
        SI = 'SR-RF-DLLRF-01'
        ALL = (BO, SI)

    _properties = (
        'PL:REF:S', 'SL:REF:PHS', 'SL:INP:PHS',
        'mV:AL:REF-SP', 'mV:AL:REF-RB', 'SL:REF:AMP', 'SL:INP:AMP',
        'DTune-SP', 'DTune-RB', 'TUNE:DEPHS',
        'RmpPhsBot-SP', 'RmpPhsBot-RB', 'RmpPhsTop-SP', 'RmpPhsTop-RB',
        'RmpEnbl-Sel', 'RmpEnbl-Sts', 'RmpReady-Mon',
        'FF:ON', 'FF', 'FF:S', 'FF:POS', 'FF:POS:S',
        'FF:GAIN:CELL2', 'FF:GAIN:CELL2:S', 'FF:GAIN:CELL4', 'FF:GAIN:CELL4:S',
        'FF:DEADBAND', 'FF:DEADBAND:S', 'FF:CELL2', 'FF:CELL4', 'FF:ERR',
        'AMPREF:INCRATE', 'AMPREF:INCRATE:S',
        )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in ASLLRF.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=ASLLRF._properties)

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
        return self['SL:INP:PHS']

    @property
    def phase(self):
        """."""
        return self['SL:REF:PHS']

    @phase.setter
    def phase(self, value):
        self['PL:REF:S'] = self._wrap_phase(value)

    @property
    def voltage_mon(self):
        """."""
        return self['SL:INP:AMP']

    @property
    def voltage(self):
        """."""
        return self['SL:REF:AMP']

    @voltage.setter
    def voltage(self, value):
        self['mV:AL:REF-SP'] = value

    @property
    def detune(self):
        """."""
        return self['DTune-RB']

    @detune.setter
    def detune(self, value):
        self['DTune-SP'] = value

    @property
    def detune_error(self):
        """."""
        return self['TUNE:DEPHS']

    @property
    def field_flatness_acting(self):
        """Return whether the field flatness loop is acting."""
        return self['FF:ON']

    @property
    def field_flatness_enable(self):
        """Return whether the field flatness loop is enabled."""
        return self['FF']

    @field_flatness_enable.setter
    def field_flatness_enable(self, value):
        """Control state of field flatness loop."""
        self['FF:S'] = bool(value)

    @property
    def field_flatness_position(self):
        """Return the field flatness position."""
        return self['FF:POS']

    @field_flatness_position.setter
    def field_flatness_position(self, value):
        """Control the field flatness position."""
        self['FF:POS:S'] = bool(value)

    @property
    def field_flatness_gain1(self):
        """Return the gain of the first cell controlled."""
        return self['FF:GAIN:CELL2']

    @field_flatness_gain1.setter
    def field_flatness_gain1(self, value):
        """Control the gain of the first cell controlled."""
        self['FF:GAIN:CELL2:S'] = value

    @property
    def field_flatness_gain2(self):
        """Return the gain of the second cell controle."""
        return self['FF:GAIN:CELL4']

    @field_flatness_gain2.setter
    def field_flatness_gain2(self, value):
        """Control the gain of the second cell controlled."""
        self['FF:GAIN:CELL4:S'] = value

    @property
    def field_flatness_deadband(self):
        """Return the loop action deadband in [%]."""
        return self['FF:DEADBAND']

    @field_flatness_deadband.setter
    def field_flatness_deadband(self, value):
        """Control the loop action deadband in [%]."""
        self['FF:DEADBAND:S'] = value

    @property
    def field_flatness_amp1(self):
        """Amplitude of the first cell controled in [mV]."""
        return self['FF:CELL2']

    @property
    def field_flatness_amp2(self):
        """Amplitude of the second cell controled in [mV]."""
        return self['FF:CELL4']

    @property
    def field_flatness_error(self):
        """Return the amplitude error in [mV]."""
        return self['FF:ERR']

    @staticmethod
    def _wrap_phase(phase):
        """Phase must be in [-180, +180] interval."""
        return (phase + 180) % 360 - 180


class BORFCavMonitor(_DeviceNC):
    """."""

    class DEVICES:
        """Devices names."""

        BO = 'BO-05D:RF-P5Cav'

    _properties = (
        'Cell3PwrTop-Mon', 'Cell3PwrBot-Mon', 'PwrRFIntlk-Mon', 'Sts-Mon',
        'Cell1Pwr-Mon', 'Cell2Pwr-Mon', 'Cell3Pwr-Mon', 'Cell4Pwr-Mon',
        'Cell5Pwr-Mon', 'Cylin1T-Mon', 'Cylin2T-Mon', 'Cylin3T-Mon',
        'Cylin4T-Mon', 'Cylin5T-Mon', 'CoupT-Mon',
        'RmpAmpVCavBot-Mon', 'RmpAmpVCavTop-Mon',
        )

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__(
            BORFCavMonitor.DEVICES.BO, properties=BORFCavMonitor._properties)

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
        """."""
        return self['Cell3PwrTop-Mon']

    @property
    def power_bottom(self):
        """."""
        return self['Cell3PwrBot-Mon']

    @property
    def power_reverse(self):
        """."""
        return self['PwrRev-Mon']

    @property
    def power_forward(self):
        """."""
        return self['PwrFwd-Mon']

    @property
    def power_cell1(self):
        """."""
        return self['Cell1Pwr-Mon']

    @property
    def power_cell2(self):
        """."""
        return self['Cell2Pwr-Mon']

    @property
    def power_cell3(self):
        """."""
        return self['Cell3Pwr-Mon']

    @property
    def power_cell4(self):
        """."""
        return self['Cell4Pwr-Mon']

    @property
    def power_cell5(self):
        """."""
        return self['Cell5Pwr-Mon']

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
        return self['RmpAmpVCavBot-Mon']

    @property
    def gap_voltage_top(self):
        """Gap Voltage in [V]."""
        return self['RmpAmpVCavTop-Mon']


class SIRFCavMonitor(_DeviceNC):
    """."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-02SB:RF-P7Cav'

    _properties = (
        'PwrRev-Mon', 'PwrFwd-Mon',
        'PwrCell4Top-Mon', 'PwrCell4Bot-Mon', 'PwrRFIntlk-Mon', 'Sts-Mon',
        'PwrCell2-Mon', 'PwrCell4-Mon', 'PwrCell6-Mon', 'Cylin1T-Mon',
        'Cylin2T-Mon', 'Cylin3T-Mon', 'Cylin4T-Mon', 'Cylin5T-Mon',
        'Cylin6T-Mon', 'Cylin7T-Mon', 'CoupT-Mon', 'AmpVCav-Mon',
        )

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__(
            SIRFCavMonitor.DEVICES.SI, properties=SIRFCavMonitor._properties)

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
        """."""
        return self['PwrCell4Top-Mon']

    @property
    def power_bottom(self):
        """."""
        return self['PwrCell4Bot-Mon']

    @property
    def power_reverse(self):
        """."""
        return self['PwrRev-Mon']

    @property
    def power_forward(self):
        """."""
        return self['PwrFwd-Mon']

    @property
    def power_cell2(self):
        """."""
        return self['PwrCell2-Mon']

    @property
    def power_cell4(self):
        """."""
        return self['PwrCell4-Mon']

    @property
    def power_cell6(self):
        """."""
        return self['PwrCell6-Mon']

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
    def temp_cell6(self):
        """."""
        return self['Cylin6T-Mon']

    @property
    def temp_cell7(self):
        """."""
        return self['Cylin7T-Mon']

    @property
    def gap_voltage(self):
        """."""
        return self['AmpVCav-Mon']


class RFCav(_Devices):
    """."""

    class DEVICES:
        """Devices names."""

        BO = 'BO-05D:RF-P5Cav'
        SI = 'SI-02SB:RF-P7Cav'
        ALL = (BO, SI)

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in RFCav.DEVICES.ALL:
            raise NotImplementedError(devname)

        rfgen = RFGen()
        if devname == RFCav.DEVICES.SI:
            llrf = ASLLRF(ASLLRF.DEVICES.SI)
            rfmon = SIRFCavMonitor()
        elif devname == RFCav.DEVICES.BO:
            llrf = ASLLRF(ASLLRF.DEVICES.BO)
            rfmon = BORFCavMonitor()
        devices = (rfgen, llrf, rfmon)

        # call base class constructor
        super().__init__(devname, devices)

    @property
    def is_cw(self):
        """."""
        return self.dev_llrf.is_cw

    @property
    def power(self):
        """."""
        return self.dev_cavmon.get_power(self.is_cw)

    @property
    def dev_rfgen(self):
        """Return RFGen device."""
        return self.devices[0]

    @property
    def dev_llrf(self):
        """Return LLRF device."""
        return self.devices[1]

    @property
    def dev_cavmon(self):
        """Return RFPoweMon device."""
        return self.devices[2]

    def set_voltage(self, value, timeout=10):
        """."""
        self.dev_llrf.voltage = value
        return self._wait('voltage', timeout=timeout)

    def set_phase(self, value, timeout=10):
        """."""
        self.dev_llrf.phase = value
        return self._wait('phase', timeout=timeout)

    def set_frequency(self, value, timeout=10):
        """."""
        self.dev_rfgen.frequency = value
        return self._wait('frequency', timeout=timeout)

    # --- private methods ---

    def _wait(self, propty, timeout=10):
        """."""
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if propty == 'phase':
                if self.is_cw:
                    phase_sp = self.dev_llrf['PL:REF:S']
                else:
                    phase_sp = self.dev_llrf['RmpPhsBot-SP']
                if abs(self.dev_llrf.phase - phase_sp) < 0.1:
                    return True
            elif propty == 'voltage':
                voltage_sp = self.dev_llrf['mV:AL:REF-SP']
                if abs(self.dev_llrf.voltage - voltage_sp) < 0.1:
                    return True
            elif propty == 'frequency':
                freq_sp = self.dev_rfgen['GeneralFreq-SP']
                if abs(self.dev_rfgen.frequency - freq_sp) < 0.1:
                    return True
            else:
                raise Exception(
                    'Set RF property (phase, voltage or frequency)')
        return False


class RFKillBeam(_Devices):
    """RF Kill Beam Button."""

    TIMEOUT_WAIT = 3.0  # [s]
    INCRATE_VALUE = 14  # 50 mV/s
    REFMIN_VALUE = 60  # Minimum Amplitude Reference

    def __init__(self):
        """Init."""

        rfdev = ASLLRF(ASLLRF.DEVICES.SI)
        devices = (rfdev, )

        # call base class constructor
        super().__init__('SI-Glob:RF-KillBeam', devices)

    @property
    def dev_llrf(self):
        """Device SILLRF."""
        return self.devices[0]

    def cmd_kill_beam(self):
        """Kill beam."""
        # get initial Amplitude Increase Rate
        aincrate_init = self.dev_llrf['AMPREF:INCRATE']
        if aincrate_init is None:
            return [False, 'Could not read RF Amplitude Increase Rate PV'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE)!']

        # get initial Amplitude Reference
        alref_init = self.dev_llrf['mV:AL:REF-RB']
        if alref_init is None:
            return [False, 'Could not read Amplitude Reference PV'
                           '(SR-RF-DLLRF-01:mV:AL:REF-RB)!']

        # set Amplitude Increase Rate to 50 mV/s and wait
        self._pv_put('AMPREF:INCRATE:S', RFKillBeam.INCRATE_VALUE)

        if not self.dev_llrf._wait(
                'AMPREF:INCRATE:S', RFKillBeam.INCRATE_VALUE,
                timeout=RFKillBeam.TIMEOUT_WAIT):
            return [False, 'Could not set RF Amplitude Increase Rate PV'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE:S)!']

        # waiting time
        wait_time = int((alref_init - RFKillBeam.REFMIN_VALUE)/50)

        # set Amplitude Reference to 60mV and wait for wait_time seconds
        if not self._pv_put('mV:AL:REF-SP', RFKillBeam.REFMIN_VALUE):
            return [False, 'Could not set Amplitude Reference PV'
                           '(SR-RF-DLLRF-01:mV:AL:REF-SP)!']
        _time.sleep(wait_time)

        # set Amplitude Reference to initial value
        if not self._pv_put('mV:AL:REF-SP', alref_init):
            return [False, 'Could not set Amplitude Reference PV'
                           '(SR-RF-DLLRF-01:mV:AL:REF-SP)!']
        _time.sleep(wait_time)

        # set Amplitude Increase Rate to initial value
        if not self._pv_put('AMPREF:INCRATE:S', aincrate_init):
            return [False, 'Could not set RF Amplitude Increase Rate PV'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE:S)!']

        return [True, '']

    def _pv_put(self, propty, value):
        pvo = self.dev_llrf.pv_object(propty)
        if pvo.wait_for_connection():
            return pvo.put(value)
        return False
