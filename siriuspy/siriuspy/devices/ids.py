"""Define Insertion Devices."""

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch
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

        # get deviceapp properties
        properties, \
            self._orb_sp, self._orb_rb, self._orb_refmon, self._orb_mon = \
            self._get_properties(devname)

        # call base class constructor
        super().__init__(properties=properties, devname=devname)

    @property
    def orbitcorr_current(self):
        """Return orbit SOFBCurrent Mon."""
        return self[self._orb_mon]

    @orbitcorr_current.setter
    def orbitcorr_current(self, value):
        """Set orbit SOFBCurrent SP."""
        self[self._orb_sp] = value

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

    def _get_properties(self, devname):
        psnames_orb = _IDSearch.conv_idname_2_orbitcorr(devname)
        corrname = psnames_orb[0]
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

        # bumps
        self._posx, self._angx, self._posy, self._angy = \
            self._init_posang()

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

    @property
    def posx(self):
        """Return posx bump value."""
        return self._posx

    @posx.setter
    def posx(self, value):
        """Return posx bump value."""
        self._posx = value

    @property
    def angx(self):
        """Return angx bump value."""
        return self._angx

    @angx.setter
    def angx(self, value):
        """Return angx bump value."""
        self._angx = value

    @property
    def posy(self):
        """Return posy bump value."""
        return self._posy

    @posy.setter
    def posy(self, value):
        """Return posy bump value."""
        self._posy = value

    @property
    def angy(self):
        """Return angy bump value."""
        return self._angy

    @angy.setter
    def angy(self, value):
        """Return angy bump value."""
        self._angy = value

    def bump_get_orbitcorr_current(self):
        """Return bump orbit correctors currents."""
        kicks = self.ffwdcalc.conv_posang2kick(
            self.posx, self.angx, self.posy, self.angy)

        # TODO: yet to be implemented!
        # currents = self.conv_kick2curr(kicks)
        currents = 0 * kicks

        return currents

    def ffwd_get_orbitcorr_current(self):
        """Return feedforward orbit correctors currents."""
        phase = self.apu.phase
        currents = self.ffwdcalc.conv_phase_2_orbcorr_currents(phase)
        return currents

    def ffwd_update_orbitcorr(self):
        """Update orbit feedforward."""
        currents_ffwd = self.ffwd_get_orbitcorr_current()
        currents_bump = self.bump_get_orbitcorr_current()
        self.correctors.orbitcorr_current = currents_ffwd + currents_bump

    def update(self):
        """Update feedforward with bump."""
        self.ffwd_update_orbitcorr()

    # --- private methods ---

    def _init_posang(self):
        _ = self  # throaway arguments (temporary)
        posx, angx = 0.0, 0.0
        posy, angy = 0.0, 0.0
        # NOTE: we could initialize posang with corrector values.
        return posx, angx, posy, angy
