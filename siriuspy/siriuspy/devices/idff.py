"""Define Insertion Devices."""

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch
from ..magnet.idffwd import APUFFWDCalc as _APUFFWDCalc

from .device import Devices as _Devices
from .pwrsupply import PowerSupply as _PowerSupply


class IDFF(_Devices):
    """."""
    class DEVICES:
        """."""
        APU22_06SB = 'SI-06SB:ID-APU22'
        APU22_07SP = 'SI-07SP:ID-APU22'
        APU22_08SB = 'SI-08SB:ID-APU22'
        APU22_09SA = 'SI-09SA:ID-APU22'
        APU58_11SP = 'SI-11SP:ID-APU58'
        EPU50_10SB = 'SI-10SB:ID-EPU50'
        WIG180_14SB = 'SI-14SB:ID-WIG180'
        ALL = (
            EPU50_10SB, WIG180_14SB,
            APU22_06SB, APU22_07SP, APU22_08SB, APU22_09SA, APU58_11SP,
            )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in IDFF.DEVICES.ALL:
            raise NotImplementedError(devname)

        # get correctors names
        self._chnames = _IDSearch.conv_idname_2_idff_ch(devname)
        self._cvnames = _IDSearch.conv_idname_2_idff_cv(devname)
        self._qsnames = _IDSearch.conv_idname_2_idff_qs(devname)

        # get ffwd
        self._ffwd = None

        devices = list()
        devices.append([_PowerSupply(devname=dev) for dev in self._chnames])
        devices.append([_PowerSupply(devname=dev) for dev in self._cvnames])
        devices.append([_PowerSupply(devname=dev) for dev in self._qsnames])

        # call base class constructor
        super().__init__(devname=devname, devices=devices)

    @property
    def chnames(self):
        """Return CH corrector power supply names."""
        return self._chnames

    @property
    def cvnames(self):
        """Return CV corrector power supply names."""
        return self._cvnames

    @property
    def qsnames(self):
        """Return QS corrector power supply names."""
        return self._qsnames

    @property
    def id_polarizations(self):
        """Return list of possible ligh polarizations for the ID."""
        return IDFF.conv_idnames_2_polarizations[self.devname]

    def get_currents(self, polarization, config):
        """Return correctors currents for a particular ID config.

        The parameter 'config' can be a gap or phase value, depending on the
        insertion device.
        """
        # NOTE: not implemented yet
        currents = dict()
        return currents


class WIGIDFF(IDFF):
    """."""
    class DEVICES(WIG.DEVICES):
        """."""

    def __init__(self, devname):
        """."""
        # call base class constructor
        super().__init__(devname)


class APUIDFF(_Devices):
    """Insertion Device APU FeedForward."""
    # NOTE: deprecated! needs revision!

    DEVICES = APU.DEVICES

    def __init__(self, devname):
        """."""
        # create APU device
        self._apu = APU(devname)

        # create IDCorrectors
        # self._idcorrs = IDCorrectors(devname)

        # create FFWDCalc
        self._ffwdcalc = _APUFFWDCalc(devname)

        # create normalizers
        # self._strenconv_chs, self._strenconv_cvs = self._create_strenconv()

        # call base class constructor
        # devices = (
        #     self._apu, self._idcorrs,
        #     self._strenconv_chs, self._strenconv_cvs)
        devices = (self._apu, )
        super().__init__(devname, devices)

        # bumps
        self._posx, self._angx, self._posy, self._angy = \
            self._init_posang()

    @property
    def apu(self):
        """Return APU device."""
        return self._apu

    # @property
    # def correctors(self):
    #     """Return IDCorrectors device."""
    #     return self._idcorrs

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

    def conv_orbitcorr_kick2curr(self, kickx, kicky):
        """."""
        curr_chs = self._strenconv_chs.conv_strength_2_current(kickx)
        curr_cvs = self._strenconv_cvs.conv_strength_2_current(kicky)
        return curr_chs, curr_cvs

    def bump_get_orbitcorr_current(self):
        """Return bump orbit correctors currents."""
        kickx, kicky = self.ffwdcalc.conv_posang2kick(
            self.posx, self.angx, self.posy, self.angy)
        curr_chs, curr_cvs = self.conv_orbitcorr_kick2curr(kickx, kicky)
        return curr_chs, curr_cvs

    def ffwd_get_orbitcorr_current(self, phase=None):
        """Return feedforward orbitcorr currents for a given ID phase."""
        # 157 µs ± 3.93 µs per loop [if phase is passed]
        if phase is None:
            phase = self.apu.phase
        currents = self.ffwdcalc.conv_phase_2_orbcorr_currents(phase)
        return currents

    def ffwd_update_orbitcorr(self, phase=None):
        """Update orbit feedforward."""
        currents_ffwd = self.ffwd_get_orbitcorr_current(phase)
        curr_bump_ch, curr_bump_cv = self.bump_get_orbitcorr_current()
        self.correctors.orbitcorr_current = currents_ffwd + currents_bump

    def ffwd_update(self, phase=None):
        """Update feedforward with bump."""
        # 305 µs ± 45.5 µs per loop
        self.ffwd_update_orbitcorr(phase)

    # --- private methods ---

    def _init_posang(self):
        _ = self  # throaway arguments (temporary)
        posx, angx = 0.0, 0.0
        posy, angy = 0.0, 0.0
        # NOTE: we could initialize posang with corrector values.
        return posx, angx, posy, angy

    # def _create_strenconv(self):
    #     """."""
    #     psnames = self.correctors.orbitcorr_psnames

    #     maname = psnames[0].replace(':PS-', ':MA-')
    #     strenconv_chs = _StrengthConv(
    #         maname, proptype='Ref-Mon', auto_mon=True)
    #     maname = psnames[self.ffwdcalc.nr_chs].replace(':PS-', ':MA-')
    #     strenconv_cvs = _StrengthConv(
    #         maname, proptype='Ref-Mon', auto_mon=True)

    #     return strenconv_chs, strenconv_cvs
