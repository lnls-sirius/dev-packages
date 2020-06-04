"""Define Insertion Devices."""

from ..namesys import SiriusPVName as _SiriusPVName
from ..magnet.idffwd import APUFFWDCalc as _APUFFWDCalc

from .device import Device as _Device
from .device import Devices as _Devices
from .device import DeviceApp as _DeviceApp


class IDCorrectors(_DeviceApp):
    """."""

    class DEVICES:
        """."""

        APU22_09SA = 'SI-09SA:ID-APU22'
        ALL = (APU22_09SA, )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in IDCorrectors.DEVICES.ALL:
            raise NotImplementedError(devname)

        self._ffwdcalc = APUFFWDCalc(devname)

        # get deviceapp properties
        properties, \
            self._orb_sp, self._orb_rb, self._orb_refmon, self._orb_mon = \
            self._get_properties()

        # call base class constructor
        super().__init__(properties=properties, devname=devname)

    @property
    def orbitcorr_current(self):
        """Return orbit SOFBCurrent Mon."""
        return self[self._orb_mon]

    @orbitcorr_current.setter
    def orbitcorr_current(self, value):
        """Set orbit SOFBCurrent SP."""
        # self[self._orb_sp] = value

    @property
    def orbitcorr_current_sp(self):
        """Return orbit SOFBCurrent setpoint."""
        return self[self._orb_sp]

    @property
    def orbitcorr_current_rb(self):
        """Return orbit SOFBCurrent readback."""
        return self[self._orb_rb]

    @property
    def orbitcorr_current_mon(self):
        """Return orbit SOFBCurrent monitor."""
        return self[self._orb_mon]

    def _get_properties(self):
        corrname = self._psnames_orb[0]
        orb_sp = corrname + ':SOFBCurrent-SP'
        orb_rb = corrname + ':SOFBCurrent-RB'
        orb_refmon = corrname + ':SOFBCurrentRef-Mon'
        orb_mon = corrname + ':SOFBCurrent-Mon'
        properties = (
            orb_sp, orb_rb, orb_refmon, orb_mon
        )
        return properties, orb_sp, orb_rb, orb_refmon, orb_mon


class APU(_Device):
    """Insertion Device APU."""

    class DEVICES:
        """."""

        APU22_09SA = 'SI-09SA:ID-APU22'
        ALL = (APU22_09SA, )

    _properties = (
        'Phase-SP', 'Phase-Mon',
        'Kx-SP', 'Kx-Mon',
    )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in APU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=APU._properties, auto_mon=True)

    @property
    def phase(self):
        """Return APU phase [mm]."""
        return self['Phase-Mon']

    @phase.setter
    def phase(self, value):
        """Set APU phase [mm]."""
        self['Phase-SP'] = value

    @property
    def phase_sp(self):
        """Return APU phase SP [mm]."""
        return self['Phase-SP']

    @property
    def idkx(self):
        """Return APU Kx."""
        return self['Kx-SP']


class APUFeedForward(_Devices):
    """Insertion Device APU FeedForward."""

    DEVICES = APU.DEVICES

    def __init__(self, devname):
        """."""
        # create APU device
        self._apu = APU(devname)

        # create IDCorrectors
        self._idcorrs = IDCorrectors(devname)

        # create FFWDCalc
        self._ffwdcalc = _APUFFWDCalc(devname)

        # call base class constructor
        devices = (self._apu, self._idcorrs)
        super().__init__(devname, devices)

    @property
    def apu(self):
        """Return APU device."""
        return self._apu

    @property
    def correctors(self):
        """Return IDCorrectors device."""
        return self._idcorrs

    @property
    def ffwdcalc(self):
        """."""
        return self._ffwdcalc

    def ffwd_get_orbitcorr_current(self):
        """Return feedforward orbit correctors currents."""
        phase = self.apu.phase
        currents = self.ffwdcalc.conv_phase_2_orbcorr_currents(phase)
        return currents

    def ffwd_update_orbitcorr(self):
        """Update orbit feedforward."""
        currents = self.ffwd_get_orbitcorr_current()
        self.correctors.orbitcorr_current = currents

    def update_ffwd(self):
        """Update feedforward."""
        self.ffwd_update_orbit()
