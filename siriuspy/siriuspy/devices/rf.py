"""."""

import time as _time
import numpy as _np
from epics import PV

from .device import Device as _Device
from .device import Devices as _Devices


class RFGen(_Device):
    """."""

    DEVICE = 'RF-Gen'
    RF_DELTA_MIN = 0.1  # [Hz]
    RF_DELTA_MAX = 1000.0  # [Hz]
    RF_DELTA_RMP = 20  # [Hz]

    _properties = ('GeneralFreq-SP', 'GeneralFreq-RB')

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__(RFGen.DEVICE, properties=RFGen._properties)

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


class RFLL(_Device):
    """."""

    DEVICE_SI = 'SR-RF-DLLRF-01'
    DEVICE_BO = 'BR-RF-DLLRF-01'

    _properties = (
        'PL:REF:S', 'SL:INP:PHS',
        'mV:AL:REF:S', 'SL:REF:AMP',
        'RmpPhsBot-SP', 'RmpPhsBot-RB',
        'RmpPhsTop-SP', 'RmpPhsTop-RB')

    def __init__(self, devname, is_cw=None):
        """."""
        # set is_cw
        self._is_cw = RFLL._set_is_cw(devname, is_cw)

        # call base class constructor
        super().__init__(devname, properties=RFLL._properties)

    @property
    def is_cw(self):
        """."""
        return self._is_cw

    @property
    def phase(self):
        """."""
        if self._is_cw:
            return self['SL:INP:PHS']
        return self['RmpPhsBot-RB']

    @phase.setter
    def phase(self, value):
        """."""
        if self._is_cw:
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

    @staticmethod
    def _set_is_cw(devname, is_cw):
        defcw = (devname == RFLL.DEVICE_BO)
        value = defcw if is_cw is None else is_cw
        return value


class RFPowMon(_Device):
    """."""

    DEVICE_SI = 'RA-RaSIA01:RF-LLRFCalSys'
    DEVICE_BO = 'BO-05D:RF-P5Cav'

    _properties = {
        DEVICE_SI: ('PwrW1-Mon', ),
        DEVICE_BO: ('Cell3PwrTop-Mon', 'Cell3Pwr-Mon')}

    def __init__(self, devname, is_cw=None):
        """."""
        # set is_cw
        self._is_cw = self._set_is_cw(devname, is_cw)

        # call base class constructor
        super().__init__(devname, properties=RFPowMon._properties[devname])

    @property
    def is_cw(self):
        """."""
        return self._is_cw

    @property
    def power(self):
        """."""
        if self._devname == RFPowMon.DEVICE_BO:
            if self.is_cw:
                return self['Cell3PwrTop-Mon']
            return self['Cell3Pwr-Mon']
        return self['PwrW1-Mon']

    # --- private methods ---

    @staticmethod
    def _set_is_cw(devname, is_cw):
        defcw = (devname == RFPowMon.DEVICE_BO)
        value = defcw if is_cw is None else is_cw
        return value


class RFCav(_Devices):
    """."""

    DEVICE_SI = 'RA-RaSIA01:RF-LLRFCalSys'
    DEVICE_BO = 'BO-05D:RF-P5Cav'

    def __init__(self, devname, is_cw=None):
        """."""
        rfgen = RFGen()
        if devname == RFCav.DEVICE_SI:
            rfll = RFLL(RFLL.DEVICE_SI, is_cw)
            rfpowmon = RFPowMon(RFPowMon.DEVICE_SI, is_cw)
        elif devname == RFCav.DEVICE_BO:
            rfll = RFLL(RFLL.DEVICE_BO, is_cw)
            rfpowmon = RFPowMon(RFPowMon.DEVICE_SI, is_cw)
        devices = (rfgen, rfll, rfpowmon)

        # call base class constructor
        super().__init__(devname, devices)

    @property
    def is_cw(self):
        """."""
        return self.devices[0].is_cw

    @property
    def rf_gen(self):
        """Return RFGen device."""
        return self.devices[0]

    @property
    def rf_ll(self):
        """Return RFLL device."""
        return self.devices[1]

    @property
    def rf_powmon(self):
        """Return RFPoweMon device."""
        return self.devices[2]
