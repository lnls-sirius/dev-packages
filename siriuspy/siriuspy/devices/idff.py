"""Insertion Devices Feedforward Devices."""

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch
from ..magnet.idffwd import APUFFWDCalc as _APUFFWDCalc
from ..idff.config import IDFFConfig as _IDFFConfig

from .device import Device as _Device, Devices as _Devices
from .pwrsupply import PowerSupply as _PowerSupply
from .ids import WIG as _WIG, APU as _APU


class IDFF(_Devices):
    """Insertion Device Feedforward Device."""

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

        self._devname = devname  # needed for _create_devices
        self._idffconfig = _IDFFConfig()

        self._kparametername = \
            _IDSearch.conv_idname_2_kparameter_propty(devname)

        self._devkp, self._devsch, self._devscv, self._devsqs = \
            self._create_devices(devname)

        # call base class constructor
        devices = [self._devkp, ]
        devices += self._devsch
        devices += self._devscv
        devices += self._devsqs
        super().__init__(devname=devname, devices=devices)

    @property
    def chnames(self):
        """Return CH corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_chnames(self.devname)

    @property
    def cvnames(self):
        """Return CV corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_cvnames(self.devname)

    @property
    def qsnames(self):
        """Return QS corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_qsnames(self.devname)

    @property
    def kparametername(self):
        """Return corresponding to ID kparameter."""
        return self._kparametername

    @property
    def polarizations(self):
        """Return list of possible light polarizations for the ID."""
        return _IDSearch.conv_idname_2_polarizations(self.devname)

    @property
    def kparameter(self):
        """Return kparameter value."""
        return self._devkp[self._kparametername]

    @property
    def idffconfig(self):
        """."""
        return self._idffconfig

    def load_config(self, name):
        """Load IDFF configuration."""
        self._idffconfig.load_config(name=name)
        if not self._config_is_ok():
            raise ValueError('Config is incompatible with ID configdb type.')

    @property
    def kparameter_pvname(self):
        """Return pvname corresponding to ID kparameter pvname."""
        return self._idffconfig.kparameter_pvname

    def interpolate_setpoints(self, polarization):
        """Return correctors setpoints for a particular ID config.

        The parameter 'config' can be a gap or phase value, depending on the
        insertion device.
        """
        if not self._idffconfig:
            ValueError('IDFFConfig is not loaded!')

        if polarization not in self.idffconfig.polarizations:
            raise ValueError('Polarization is not compatible with ID.')
        kparameter = self.kparameter
        setpoints = self.idffconfig.interpolate_setpoints(
            polarization, kparameter)
        return polarization, setpoints

    def implement_setpoints(self, polarization, setpoints=None):
        """Implement setpoints in correctors."""
        if not setpoints:
            _, setpoints = self.interpolate_setpoints(polarization)
        corrs = self._devsch + self._devscv
        for pvname, value in setpoints.items():
            for dev in corrs:
                if dev.devname in pvname:
                    *_, propty = pvname.split(':')
                    dev[propty] = value
                    break

    def _create_devices(self, devname):
        kparm_auto_mon = False
        devkp = _Device(
            devname=devname,
            properties=(self._kparametername, ), auto_mon=kparm_auto_mon)
        devsch = [_PowerSupply(devname=dev) for dev in self.chnames]
        devscv = [_PowerSupply(devname=dev) for dev in self.cvnames]
        devsqs = [_PowerSupply(devname=dev) for dev in self.qsnames]

        return devkp, devsch, devscv, devsqs

    def _config_is_ok(self):
        # TODO: to be implemented
        return True


class WIGIDFF(IDFF):
    """."""

    class DEVICES(_WIG.DEVICES):
        """."""

    def __init__(self, devname):
        """."""
        # call base class constructor
        super().__init__(devname)

    @property
    def gap_mon(self):
        """."""
        return self.kparameter


class APUIDFF(_Devices):
    """Insertion Device APU FeedForward."""

    # NOTE: deprecated! needs revision!

    class DEVICES(_APU.DEVICES):
        """."""

    def __init__(self, devname):
        """."""
        # create APU device
        self._apu = _APU(devname)

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

    # def ffwd_update_orbitcorr(self, phase=None):
    #     """Update orbit feedforward."""
    #     currents_ffwd = self.ffwd_get_orbitcorr_current(phase)
    #     curr_bump_ch, curr_bump_cv = self.bump_get_orbitcorr_current()
    #     self.correctors.orbitcorr_current = currents_ffwd + currents_bump

    # def ffwd_update(self, phase=None):
    #     """Update feedforward with bump."""
    #     # 305 µs ± 45.5 µs per loop
    #     self.ffwd_update_orbitcorr(phase)

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
