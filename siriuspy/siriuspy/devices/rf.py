"""."""

import time as _time
import numpy as _np

from .device import DeviceNC as _DeviceNC
from .device import Devices as _Devices


class RFGen(_DeviceNC):
    """."""

    RF_DELTA_MIN = 0.1  # [Hz]
    RF_DELTA_MAX = 15000.0  # [Hz]
    RF_DELTA_RMP = 20  # [Hz]

    class DEVICES:
        """Devices names."""

        AS = 'RF-Gen'
        ALL = (AS, )

    _properties = ('GeneralFreq-SP', 'GeneralFreq-RB')

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


class ASLLRF(_DeviceNC):
    """AS LLRF."""

    class DEVICES:
        """Devices names."""

        BO = 'BR-RF-DLLRF-01'
        SI = 'SR-RF-DLLRF-01'
        ALL = (BO, SI)

    _properties = (
        'PL:REF:S', 'SL:REF:PHS', 'SL:INP:PHS',
        'mV:AL:REF:S', 'SL:REF:AMP', 'SL:INP:AMP',
        'DTune-SP', 'DTune-RB', 'TUNE:DEPHS',
        'RmpPhsBot-SP', 'RmpPhsBot-RB', 'RmpPhsTop-SP', 'RmpPhsTop-RB',
        'RmpEnbl-Sel', 'RmpEnbl-Sts', 'RmpReady-Mon',
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
        self['mV:AL:REF:S'] = value

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
        'PwrCell4Top-Mon', 'PwrCell4Bot-Mon', 'PwrRFIntlk-Mon', 'Sts-Mon',
        'PwrCell2-Mon', 'PwrCell4-Mon', 'PwrCell6-Mon', 'Cylin1T-Mon',
        'Cylin2T-Mon', 'Cylin3T-Mon', 'Cylin4T-Mon', 'Cylin5T-Mon',
        'Cylin6T-Mon', 'Cylin7T-Mon', 'CoupT-Mon'
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
        self._wait('voltage', timeout=timeout)

    def set_phase(self, value, timeout=10):
        """."""
        self.dev_llrf.phase = value
        self._wait('phase', timeout=timeout)

    def set_frequency(self, value, timeout=10):
        """."""
        self.dev_rfgen.frequency = value
        self._wait('frequency', timeout=timeout)

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
                    break
            elif propty == 'voltage':
                voltage_sp = self.dev_llrf['mV:AL:REF:S']
                if abs(self.dev_llrf.voltage - voltage_sp) < 0.1:
                    break
            elif propty == 'frequency':
                freq_sp = self.dev_rfgen['GeneralFreq-SP']
                if abs(self.dev_rfgen.frequency - freq_sp) < 0.1:
                    break
            else:
                raise Exception(
                    'Set RF property (phase, voltage or frequency)')
