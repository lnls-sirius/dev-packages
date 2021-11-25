"""."""

import time as _time
import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from .device import DeviceNC as _DeviceNC
from .device import Devices as _Devices


class RFGen(_DeviceNC):
    """."""

    RF_DELTA_MIN = 0.1  # [Hz]
    RF_DELTA_MAX = 15000.0  # [Hz]
    RF_DELTA_RMP = 200  # [Hz]

    FREQ_OPMODE = _get_namedtuple('FreqOpMode', ('CW', 'SWE', 'LIST'))
    SWEEP_MODE = _get_namedtuple(
        'SweepTrigSrc', ('AUTO', 'MAN', 'STEP'))
    SWEEP_TRIG_SRC = _get_namedtuple(
        'SweepTrigSrc', ('AUTO', 'SING', 'EXT', 'EAUT'))
    SWEEP_SPACING = _get_namedtuple('SweepSpacing', ('LIN', 'LOG'))
    SWEEP_SHAPE = _get_namedtuple('SweepShape', ('SAWT', 'TRI'))
    SWEEP_RETRACE = _get_namedtuple('SweepRetrace', ('OFF', 'ON'))

    class DEVICES:
        """Devices names."""

        AS = 'RF-Gen'
        ALL = (AS, )

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
        'FreqPhsCont-Sel', 'FreqPhsCont-Sts',

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
    def frequency(self):
        """."""
        return self['GeneralFreq-RB']

    @frequency.setter
    def frequency(self, value):
        delta_max = RFGen.RF_DELTA_RMP  # [Hz]
        freq0 = self['GeneralFreq-SP']
        if freq0 is None or value is None:
            return
        delta = abs(value-freq0)
        if delta < RFGen.RF_DELTA_MIN or delta > RFGen.RF_DELTA_MAX:
            return
        npoints = int(round(delta/delta_max)) + 2
        freq_span = _np.linspace(freq0, value, npoints)[1:]
        for freq in freq_span:
            self._pvs['GeneralFreq-SP'].put(freq, wait=False)
            _time.sleep(1.0)
        self['GeneralFreq-SP'] = value

    @property
    def freq_opmode(self):
        """."""
        return self['GeneralFSweep-Sts']

    @freq_opmode.setter
    def freq_opmode(self, value):
        self._enum_setter('GeneralFSweep-Sel', value, self.FREQ_OPMODE)

    @property
    def freq_opmode_str(self):
        """."""
        return self.FREQ_OPMODE._fields[self['GeneralFSweep-Sts']]

    def cmd_set_freq_opmode_to_continuous_wave(self):
        """."""
        self.freq_opmode = self.FREQ_OPMODE.CW
        return self._wait('GeneralFSweep-Sts', self.FREQ_OPMODE.CW)

    def cmd_set_freq_opmode_to_sweep(self):
        """."""
        self.freq_opmode = self.FREQ_OPMODE.SWE
        return self._wait('GeneralFSweep-Sts', self.FREQ_OPMODE.SWE)

    @property
    def freq_sweep_mode(self):
        """."""
        return self['FreqFSweepMode-Sts']

    @freq_sweep_mode.setter
    def freq_sweep_mode(self, value):
        self._enum_setter('FreqFSweepMode-Sel', value, self.SWEEP_MODE)

    @property
    def freq_sweep_mode_str(self):
        """."""
        return self.SWEEP_MODE._fields[self['FreqFSweepMode-Sts']]

    def cmd_set_freq_sweep_mode_to_automatic(self):
        """."""
        self.freq_sweep_mode = self.SWEEP_MODE.AUTO
        return self._wait('FreqFSweepMode-Sts', self.SWEEP_MODE.AUTO)

    def cmd_set_freq_sweep_mode_to_step(self):
        """."""
        self.freq_sweep_mode = self.SWEEP_MODE.STEP
        return self._wait('FreqFSweepMode-Sts', self.SWEEP_MODE.STEP)

    @property
    def freq_sweep_spacing_mode(self):
        """."""
        return self['FreqFSpacMode-Sts']

    @freq_sweep_spacing_mode.setter
    def freq_sweep_spacing_mode(self, value):
        self._enum_setter('FreqFSpacMode-Sel', value, self.SWEEP_SPACING)

    @property
    def freq_sweep_spacing_mode_str(self):
        """."""
        return self.SWEEP_SPACING._fields[self['FreqFSpacMode-Sts']]

    def cmd_set_freq_sweep_spacing_mode_to_linear(self):
        """."""
        self.freq_sweep_spacing_mode = self.SWEEP_SPACING.LIN
        return self._wait('FreqFSpacMode-Sts', self.SWEEP_SPACING.LIN)

    def cmd_set_freq_sweep_spacing_mode_to_log(self):
        """."""
        self.freq_sweep_spacing_mode = self.SWEEP_SPACING.LOG
        return self._wait('FreqFSpacMode-Sts', self.SWEEP_SPACING.LOG)

    @property
    def freq_sweep_trig_src(self):
        """."""
        return self['TrigFSweepSrc-Sts']

    @freq_sweep_trig_src.setter
    def freq_sweep_trig_src(self, value):
        self._enum_setter('TrigFSweepSrc-Sel', value, self.SWEEP_TRIG_SRC)

    @property
    def freq_sweep_trig_src_str(self):
        """."""
        return self.SWEEP_TRIG_SRC._fields[self['TrigFSweepSrc-Sts']]

    def cmd_set_freq_sweep_trig_src_to_external(self):
        """."""
        self.freq_sweep_trig_src = self.SWEEP_TRIG_SRC.EXT
        return self._wait('TrigFSweepSrc-Sts', self.SWEEP_TRIG_SRC.EXT)

    def cmd_set_freq_sweep_trig_src_to_single(self):
        """."""
        self.freq_sweep_trig_src = self.SWEEP_TRIG_SRC.SING
        return self._wait('TrigFSweepSrc-Sts', self.SWEEP_TRIG_SRC.SING)

    def cmd_set_freq_sweep_trig_src_to_auto(self):
        """."""
        self.freq_sweep_trig_src = self.SWEEP_TRIG_SRC.AUTO
        return self._wait('TrigFSweepSrc-Sts', self.SWEEP_TRIG_SRC.AUTO)

    @property
    def freq_sweep_shape(self):
        """."""
        return self['FreqFreqShp-Sts']

    @freq_sweep_shape.setter
    def freq_sweep_shape(self, value):
        self._enum_setter('FreqFreqShp-Sel', value, self.SWEEP_SHAPE)

    @property
    def freq_sweep_shape_str(self):
        """."""
        return self.SWEEP_SHAPE._fields[self['FreqFreqShp-Sts']]

    def cmd_set_freq_sweep_shape_to_sawtooth(self):
        """."""
        self.freq_sweep_shape = self.SWEEP_SHAPE.SAWT
        return self._wait('FreqFreqShp-Sts', self.SWEEP_SHAPE.SAWT)

    def cmd_set_freq_sweep_shape_to_triangular(self):
        """."""
        self.freq_sweep_shape = self.SWEEP_SHAPE.TRI
        return self._wait('FreqFreqShp-Sts', self.SWEEP_SHAPE.TRI)

    @property
    def freq_sweep_retrace(self):
        """."""
        return self['FreqFreqRetr-Sts']

    @freq_sweep_retrace.setter
    def freq_sweep_retrace(self, value):
        self._enum_setter('FreqFreqRetr-Sel', value, self.SWEEP_RETRACE)

    @property
    def freq_sweep_retrace_str(self):
        """."""
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
        """."""
        return self['FreqFreqSpan-RB']

    @freq_sweep_span.setter
    def freq_sweep_span(self, value):
        self['FreqFreqSpan-SP'] = float(value)

    @property
    def freq_sweep_center_freq(self):
        """."""
        return self['FreqCenterFreq-RB']

    @freq_sweep_center_freq.setter
    def freq_sweep_center_freq(self, value):
        self['FreqCenterFreq-SP'] = float(value)

    @property
    def freq_sweep_start_freq(self):
        """."""
        return self['FreqStartFreq-RB']

    @freq_sweep_start_freq.setter
    def freq_sweep_start_freq(self, value):
        self['FreqStartFreq-SP'] = float(value)

    @property
    def freq_sweep_stop_freq(self):
        """."""
        return self['FreqStopFreq-RB']

    @freq_sweep_stop_freq.setter
    def freq_sweep_stop_freq(self, value):
        self['FreqStopFreq-SP'] = float(value)

    @property
    def freq_sweep_step_freq_linear(self):
        """."""
        return self['FreqFStepLin-RB']

    @freq_sweep_step_freq_linear.setter
    def freq_sweep_step_freq_linear(self, value):
        self['FreqFStepLin-SP'] = float(value)

    @property
    def freq_sweep_step_freq_log(self):
        """."""
        return self['FreqFStepLog-RB']

    @freq_sweep_step_freq_log.setter
    def freq_sweep_step_freq_log(self, value):
        self['FreqFStepLog-SP'] = float(value)

    @property
    def freq_sweep_step_time(self):
        """."""
        return self['FreqFDwellTime-RB']

    @freq_sweep_step_time.setter
    def freq_sweep_step_time(self, value):
        self['FreqFDwellTime-SP'] = float(value)


class ASLLRF(_DeviceNC):
    """AS LLRF."""

    class DEVICES:
        """Devices names."""

        BO = 'BR-RF-DLLRF-01'
        SI = 'SR-RF-DLLRF-01'
        ALL = (BO, SI)

    _properties = (
        'PL:REF:S', 'SL:REF:PHS', 'SL:INP:PHS',
        'mV:AL:REF-SP', 'SL:REF:AMP', 'SL:INP:AMP',
        'DTune-SP', 'DTune-RB', 'TUNE:DEPHS',
        'RmpPhsBot-SP', 'RmpPhsBot-RB', 'RmpPhsTop-SP', 'RmpPhsTop-RB',
        'RmpEnbl-Sel', 'RmpEnbl-Sts', 'RmpReady-Mon',
        'FF:ON', 'FF', 'FF:S', 'FF:POS', 'FF:POS:S',
        'FF:GAIN:CELL2', 'FF:GAIN:CELL2:S', 'FF:GAIN:CELL4', 'FF:GAIN:CELL4:S',
        'FF:DEADBAND', 'FF:DEADBAND:S', 'FF:CELL2', 'FF:CELL4', 'FF:ERR',
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
        self['RmpPhsTop-SP'] = value

    @property
    def phase_bottom(self):
        """."""
        return self['RmpPhsBot-RB']

    @phase_bottom.setter
    def phase_bottom(self, value):
        self['RmpPhsBot-SP'] = value

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
        self['PL:REF:S'] = value

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
