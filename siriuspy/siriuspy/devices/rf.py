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


class LLRF(_DeviceNC):
    """."""

    class DEVICES:
        """Devices names."""

        BO = 'BR-RF-DLLRF-01'
        SI = 'SR-RF-DLLRF-01'
        ALL = (BO, SI)

    _properties = (
        'PL:REF:S', 'SL:INP:PHS',
        'mV:AL:REF:S', 'SL:REF:AMP', 'RmpEnbl-Sts',
        'RmpPhsBot-SP', 'RmpPhsBot-RB',
        'RmpPhsTop-SP', 'RmpPhsTop-RB')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in LLRF.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=LLRF._properties)

    @property
    def is_cw(self):
        """."""
        return not self['RmpEnbl-Sts']

    @property
    def phase(self):
        """."""
        if self.is_cw:
            return self['SL:INP:PHS']
        return self['RmpPhsBot-RB']

    @phase.setter
    def phase(self, value):
        """."""
        if self.is_cw:
            self['PL:REF:S'] = value
        else:
            self['RmpPhsBot-SP'] = value
            self['RmpPhsTop-SP'] = value

    @property
    def voltage(self):
        """."""
        return self['SL:REF:AMP']

    @voltage.setter
    def voltage(self, value):
        self['mV:AL:REF:S'] = value

    # --- private methods ---


class RFPowMon(_DeviceNC):
    """."""

    class DEVICES:
        """Devices names."""

        BO = 'BO-05D:RF-P5Cav'
        SI = 'SI-02SB:RF-P7Cav'
        ALL = (BO, SI)

    _properties = {
        DEVICES.SI: ('PwrCell4-Mon', ),
        DEVICES.BO: ('Cell3PwrTop-Mon', 'Cell3Pwr-Mon')}

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in RFPowMon.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=RFPowMon._properties[devname])

    def get_power(self, is_cw=True):
        """."""
        if self._devname == RFPowMon.DEVICES.BO:
            if is_cw:
                return self['Cell3PwrTop-Mon']
            return self['Cell3Pwr-Mon']
        return self['PwrCell4-Mon']


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
            llrf = LLRF(LLRF.DEVICES.SI)
            rfpowmon = RFPowMon(RFPowMon.DEVICES.SI)
        elif devname == RFCav.DEVICES.BO:
            llrf = LLRF(LLRF.DEVICES.BO)
            rfpowmon = RFPowMon(RFPowMon.DEVICES.BO)
        devices = (rfgen, llrf, rfpowmon)

        # call base class constructor
        super().__init__(devname, devices)

    @property
    def is_cw(self):
        """."""
        return self.dev_llrf.is_cw

    @property
    def power(self):
        """."""
        return self.dev_rfpowmon.get_power(self.is_cw)

    @property
    def dev_rfgen(self):
        """Return RFGen device."""
        return self.devices[0]

    @property
    def dev_llrf(self):
        """Return LLRF device."""
        return self.devices[1]

    @property
    def dev_rfpowmon(self):
        """Return RFPoweMon device."""
        return self.devices[2]

    def cmd_set_voltage(self, value, timeout=10):
        """."""
        self.dev_llrf.voltage = value
        self._wait('voltage', timeout=timeout)

    def cmd_set_phase(self, value, timeout=10):
        """."""
        self.dev_llrf.phase = value
        self._wait('phase', timeout=timeout)

    def cmd_set_frequency(self, value, timeout=10):
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
