"""."""

import time as _time

from ..pwrsupply.psctrl.pscstatus import PSCStatus as _PSCStatus

from .device import Device as _Device


class DCCT(_Device):
    """."""

    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        BO = 'BO-35D:DI-DCCT'
        SI_13C4 = 'SI-13C4:DI-DCCT'
        SI_14C4 = 'SI-14C4:DI-DCCT'
        ALL = (BO, SI_13C4, SI_14C4)

    _properties = (
        'RawReadings-Mon', 'Current-Mon',
        'FastMeasPeriod-SP', 'FastMeasPeriod-RB',
        'FastSampleCnt-SP', 'FastSampleCnt-RB',
        'MeasTrg-Sel', 'MeasTrg-Sts',
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in DCCT.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=DCCT._properties)

    @property
    def nrsamples(self):
        """."""
        return self['FastSampleCnt-RB']

    @nrsamples.setter
    def nrsamples(self, value):
        """."""
        self['FastSampleCnt-SP'] = value

    @property
    def period(self):
        """."""
        return self['FastMeasPeriod-RB']

    @period.setter
    def period(self, value):
        self['FastMeasPeriod-SP'] = value

    @property
    def acq_ctrl(self):
        """."""
        return self['MeasTrg-Sts']

    @acq_ctrl.setter
    def acq_ctrl(self, value):
        """."""
        self['MeasTrg-Sel'] = DCCT.PWRSTATE.On if value else DCCT.PWRSTATE.Off

    @property
    def current_fast(self):
        """."""
        return self['RawReadings-Mon']

    @property
    def current(self):
        """."""
        return self['Current-Mon']

    def wait(self, timeout=10):
        """."""
        nrp = int(timeout/0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if self._isok():
                return True
        print('timed out waiting DCCT.')
        return False

    def cmd_turn_on(self, timeout=10):
        """."""
        self.acq_ctrl = DCCT.PWRSTATE.On
        return self.wait(timeout)

    def cmd_turn_off(self, timeout=10):
        """."""
        self.acq_ctrl = DCCT.PWRSTATE.Off
        return self.wait(timeout)

    # --- private methods ---

    def _isok(self):
        if self['MeasTrg-Sel']:
            return self.acq_ctrl == DCCT.PWRSTATE.On
        return self.acq_ctrl != DCCT.PWRSTATE.On
