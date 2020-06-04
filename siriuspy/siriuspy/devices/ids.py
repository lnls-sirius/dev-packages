"""Define Insertion Devices."""

import numpy as _np

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch

from .device import Device as _Device
from .device import Devices as _Devices
from .device import DeviceApp as _DeviceApp


class IDFeedForward(_DeviceApp):
    """."""

    class DEVICES:
        """."""

        APU22_09SA = 'SI-09SA:ID-APU22'
        ALL = (APU22_09SA, )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in IDFeedForward.DEVICES.ALL:
            raise NotImplementedError(devname)

        # get correctors names
        self._psnames_orb = _IDSearch.conv_idname_2_orbitcorr(devname)

        # get orbit fftable from idname:
        self._orbitffwd = _IDSearch.conv_idname_2_orbitffwd(devname)

        # get deviceapp properties
        properties, \
            self._orb_sp, self._orb_rb, self._orb_refmon, self._orb_mon = \
            self._get_properties()

        # call base class constructor
        super().__init__(properties=properties, devname=devname)

    @property
    def psnames_orbitcorr(self):
        """Return orbit corrector names."""
        return self._psnames_orb

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

    def conv_phase_2_orbcorr_currents(self, phase):
        """Return orbit correctors currents for a given ID phase."""
        ffwd = self._orbitffwd.interp_curr2mult(phase)
        # NOTE: assumes same number of CHs and CVs
        nr_chs = len(self._psnames_orb) // 2
        nr_cvs = nr_chs
        chs = [ffwd['normal'][i] for i in range(nr_chs)]
        cvs = [ffwd['skew'][i] for i in range(nr_cvs)]
        currents = _np.array(chs + cvs)
        return currents

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

        # create IDFeedForward
        self._idffwd = IDFeedForward(devname)

        # call base class constructor
        devices = (self._apu, self._idffwd)
        super().__init__(devname, devices)

    @property
    def apu(self):
        """Return APU device."""
        return self._apu

    @property
    def idffwd(self):
        """Return IDFeedForward device."""
        return self._idffwd

    def ffwd_get_orbit_current(self):
        """Return feedforward orbit correctors currents."""
        phase = self.apu.phase
        currents = self.idffwd.conv_phase_2_orbcorr_currents(phase)
        return currents

    def ffwd_update_orbit(self):
        """Update orbit feedforward."""
        currents = self.ffwd_get_orbit_current()
        self.idffwd.orbitcorr_current = currents

    def update_ffwd(self):
        """Update feedforward."""
        self.ffwd_update_orbit()
