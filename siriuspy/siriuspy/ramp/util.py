"""wfm utilities."""

from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.ramp.optics import _nominal_intkl
from siriuspy.magnet import util as _mutil


class WfmSet:
    """Class WfmSet."""

    energy_inj_gev = 0.150  # [GeV]
    energy_eje_gev = 3.000  # [GeV]
    _default_wfm = _mutil.get_default_ramp_waveform()

    def __init__(self,
                 dipole_name,
                 dipole_wfm_strength=None,
                 dipole_wfm_current=None):
        """Init method.

        Parameters
        ----------
        dipole_name : str | SiriusPVName
            dipole magnet device name for the wfm set.
        dipole_wfm_strength : list | int | float
            dipole wfm in current units.
        dipole_wfm_current : list | int | float
            dipole wfm in strength units.

        """
        self._magnets = {}
        self._wfms_strength = {}
        self._wfms_current = {}
        self._set_dipole(dipole_name,
                         dipole_wfm_strength,
                         dipole_wfm_current)

    def _set_dipole(self,
                    dipole_name,
                    dipole_wfm_strength,
                    dipole_wfm_current):
        m = _Magnet(dipole_name)
        self._dipole_name = dipole_name
        self._section = m.maname.section
        self._update_magnet_wfm(dipole_name,
                                dipole_wfm_strength,
                                dipole_wfm_current)

    def _process_wfm_inputs(self, magnet, wfm_strength, wfm_current):
        m = self._magnets[magnet]
        # strength or current setpoint?
        if wfm_strength and wfm_current:
            raise Exception('Specify either strength or current wfm for "' +
                            magnet + '"!')
        if wfm_strength is None and wfm_current is None:
            if self._section == 'BO' and m.magfunc == 'dipole':
                wfm_strength = \
                    [WfmSet.energy_eje_gev * v for v in WfmSet._default_wfm]
            elif self._section in ('SI', 'TS') and m.magfunc == 'dipole':
                wfm_strength = \
                    [WfmSet.energy_eje_gev for _ in WfmSet._default_wfm]
            elif self._section == 'TB' and m.magfunc == 'dipole':
                wfm_strength = \
                    [WfmSet.energy_inj_gev for _ in WfmSet._default_wfm]
            else:
                wfm_strength = [0.0 for _ in WfmSet._default_wfm]
            self._wfms_strength[magnet] = wfm_strength
        if type(wfm_strength) in (int, float):
            wfm_strength = [wfm_strength for _ in WfmSet._default_wfm]
        if type(wfm_current) in (int, float):
            wfm_current = [wfm_current for _ in WfmSet._default_wfm]
        return wfm_strength, wfm_current

    def _update_dipole_wfm(self,
                           magnet,
                           wfm_strength,
                           wfm_current):
        m = self._magnets[magnet]
        if wfm_strength:
            wfm_current = \
                [m.conv_strength_2_current(v) for v in wfm_strength]
        else:
            wfm_strength = \
                [m.conv_current_2_strength(v) for v in wfm_current]
        self._wfms_current[magnet] = wfm_current
        self._wfms_strength[magnet] = wfm_strength
        # recursively invoke itself to update families
        for name, mag in self._magnets.items():
            if mag.dipole_name is not None and mag.family_name is None:
                # update all families
                strength = self._wfms_strength[name]
                self._update_family_wfm(name, wfm_strength=strength)

    def _update_family_wfm(self,
                           magnet,
                           wfm_strength,
                           wfm_current):
        m = self._magnets[magnet]
        c_dip = self._wfms_current[self._dipole_name]
        if wfm_strength:
            wfm_current = [m.conv_strength_2_current(
                           wfm_strength[i],
                           current_dipole=c_dip[i])
                           for i in range(len(wfm_strength))]
        else:
            wfm_strength = [m.conv_current_2_strength(
                            wfm_current[i],
                            current_dipole=c_dip[i])
                            for i in range(len(wfm_current))]
        self._wfms_current[magnet] = wfm_current
        self._wfms_strength[magnet] = wfm_strength
        # recursively invoke itself to update trims
        for name, mag in self._magnets.items():
            if mag.dipole_name is not None and mag.family_name is not None:
                # update all trims
                strength = self._wfms_strength[name]
                self._update_trim_wfm(name, wfm_strength=strength)

    def _update_trim_wfm(self,
                         magnet,
                         wfm_strength,
                         wfm_current):
        m = self._magnets[magnet]
        c_dip = self._wfms_current[self._dipole_name]
        c_fam = self._wfms_current[self._family_name]
        if wfm_strength:
            wfm_current = [m.conv_strength_2_current(
                           wfm_strength[i],
                           current_dipole=c_dip[i],
                           current_family=c_fam[i])
                           for i in range(len(wfm_strength))]
        else:
            wfm_strength = [m.conv_current_2_strength(
                            wfm_current[i],
                            current_dipole=c_dip[i],
                            current_family=c_fam[i])
                            for i in range(len(wfm_current))]
        self._wfms_current[magnet] = wfm_current
        self._wfms_strength[magnet] = wfm_strength

    def _update_magnet_wfm(self,
                           magnet,
                           wfm_strength,
                           wfm_current):
        # add magnet in dict if not there yet.
        if magnet not in self._magnets:
            self._magnets[magnet] = _Magnet(magnet)

        wfm_strength, wfm_current = \
            self._process_wfm_inputs(magnet, wfm_strength, wfm_current)

        m = self._magnets[magnet]
        # set wfm acoording to type of magnet
        if m.dipole_name is None:
            self._update_dipole_wfm(magnet, wfm_strength, wfm_current)
        elif m.family_name is None:
            self._update_family_wfm(magnet, wfm_strength, wfm_current)
        else:
            self._update_trim_wfm(magnet, wfm_strength, wfm_current)

    @staticmethod
    def get_default_wfm_form(scale=1.0):
        """Return default wfm form."""
        return [scale * v for v in WfmSet._default_wfm]

    def set_wfm_strength(self, magnet, wfm=None):
        """Set strength wfm for a specific magnet.

        Parameters
        ----------
        magnet : str | SiriusPVName
            magnet device name.
        wfm : list | int | float
            magnet wfm in strength units.
        """
        self._update_magnet_wfm(magnet, wfm_strength=wfm, wfm_current=None)

    def set_wfm_current(self, magnet, wfm=None):
        """Set current wfm for a specific magnet.

        Parameters
        ----------
        magnet : str | SiriusPVName
            magnet device name.
        wfm : list | int | float
            magnet wfm in current units.
        """
        self._update_magnet_wfm(magnet, wfm_strength=None, wfm_current=wfm)

    def set_wfm_default(self):
        """Set wfm of quadrupoles and sextupoles.

        According to default nominal optics.
        """
        # zero trim power supplies first
        for magnet, m in self._magnets.items():
            if m.family_name is not None and m.family_name in _nominal_intkl:
                strength = _nominal_intkl[magnet]
                self._wfms_current[magnet] = \
                    [0.0 for _ in WfmSet._default_wfm]
                self._wfms_strength[magnet] = \
                    [strength for _ in WfmSet._default_wfm]
        # next, update all family power supplies
        for magnet, strength in _nominal_intkl.items():
            maname = _SiriusPVName(magnet)
            if maname.section == self.section:
                self.set_wfm_strength(magnet, strength)

    def get_wfm_strength(self, magnet):
        """Return strength wfm of given magnet."""
        return self._wfms_strength[magnet]

    def get_wfm_current(self, magnet):
        """Return current wfm of given magnet."""
        return self._wfms_current[magnet]

    @property
    def magnets(self):
        """Return list of magnet names in wfm set."""
        return list(self._magnets.keys())

    @property
    def section(self):
        """Return section of wfm set."""
        return self._section

    @property
    def dipole_name(self):
        """Return name of dipole in the wfm set."""
        return self._dipole_name
