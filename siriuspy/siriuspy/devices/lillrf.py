"""."""

import time as _time

from .device import DeviceNC as _DeviceNC


class LILLRF(_DeviceNC):
    """."""

    class DEVICES:
        """Devices names."""

        LI_SHB = 'LA-RF:LLRF:BUN1'
        LI_KLY1 = 'LA-RF:LLRF:KLY1'
        LI_KLY2 = 'LA-RF:LLRF:KLY2'
        ALL = (LI_SHB, LI_KLY1, LI_KLY2)

    _properties = (
        'SET_AMP', 'GET_AMP',
        'SET_PHASE', 'GET_PHASE')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in LILLRF.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=LILLRF._properties)

    @property
    def amplitude(self):
        """."""
        return self['GET_AMP']

    @amplitude.setter
    def amplitude(self, value):
        self['SET_AMP'] = value

    @property
    def phase(self):
        """."""
        return self['GET_PHASE']

    @phase.setter
    def phase(self, value):
        self['SET_PHASE'] = value

    def cmd_set_phase(self, value, timeout=10):
        """."""
        self.phase = value
        self._wait_rb_sp(timeout, 'phase')

    def cmd_set_amplitude(self, value, timeout=30):
        """."""
        self.amplitude = value
        self._wait_rb_sp(timeout, 'amplitude')

    def _wait_rb_sp(self, timeout=10, propty=None):
        """."""
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if propty == 'phase':
                if abs(self.phase - self['SET_PHASE']) < 0.1:
                    break
            elif propty == 'amplitude':
                if abs(self.amplitude - self['SET_AMP']) < 0.1:
                    break
            else:
                raise Exception(
                    'Set LLRF property (phase or amplitude)')
        else:
            print('timed out waiting LLRF.')
