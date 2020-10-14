"""."""

from functools import partial as _part
from copy import deepcopy as _dcopy
import numpy as _np
from epics import PV as _PV

import mathphys.constants as _consts

from ...search import PSSearch as _PSS
from ...thread import RepeaterThread as _Repeater

from ..util import BaseClass as _BaseClass, ProcessImage as _ProcessImage

from .csdev import Const as _Const

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-6  # in MeV


class CalcEnergy(_BaseClass, _Const):
    """."""

    def __init__(self, callback=None, dispersion=None, angle=None,
                 spectrometer=None):
        """."""
        super().__init__(callback=callback)
        self._dispersion = dispersion or self.DEFAULT_DISP
        self._angle = angle or self.DEFAULT_B_ANG
        self._spect = spectrometer or self.DEFAULT_SPECT
        self._excdata = _PSS.conv_psname_2_excdata(self._spect)
        self._currents = _np.array([], dtype=float)
        self._intdipole = _np.array([], dtype=float)
        self._energy = _np.array([], dtype=float)
        self._spread = _np.array([], dtype=float)
        self._beamcenter = _np.array([], dtype=float)
        self._beamsize = _np.array([], dtype=float)

    def get_map2write(self):
        """."""
        return {
            'Dispersion-SP': _part(self.write, 'dispersion'),
            'Angle-SP': _part(self.write, 'angle'),
            'Spectrometer-SP': _part(self.write, 'spectrometer'),
            }

    def get_map2read(self):
        """."""
        return {
            'Dispersion-RB': _part(self.read, 'dispersion'),
            'Angle-RB': _part(self.read, 'angle'),
            'Spectrometer-RB': _part(self.read, 'spectrometer'),
            'IntDipole-Mon': _part(self.read, 'intdipole'),
            'Energy-Mon': _part(self.read, 'energy'),
            'Spread-Mon': _part(self.read, 'spread'),
            }

    @property
    def dispersion(self):
        """."""
        return self._dispersion

    @dispersion.setter
    def dispersion(self, val):
        """."""
        if isinstance(val, (float, int)) and val != 0:
            self._dispersion = val
            self.run_callbacks('Dispersion-RB', val)
            self._perform_analysis()

    @property
    def angle(self):
        """."""
        return self._angle

    @angle.setter
    def angle(self, val):
        if isinstance(val, (float, int)) and val != 0 and abs(val) < _np.pi:
            self._angle = val
            self._perform_analysis()
            self.run_callbacks('Angle-RB', val)

    @property
    def spectrometer(self):
        """."""
        return self._spect

    @spectrometer.setter
    def spectrometer(self, val):
        """."""
        try:
            self._excdata = _PSS.conv_psname_2_excdata(val)
        except Exception:
            return
        self._spect = val
        self._perform_analysis()
        self.run_callbacks('Spectrometer-RB', val)

    @property
    def currents(self):
        """."""
        return _dcopy(self._currents)

    @property
    def beamsize(self):
        """."""
        return _dcopy(self._beamsize)

    @property
    def beamcenter(self):
        """."""
        return _dcopy(self._beamcenter)

    @property
    def intdipole(self):
        """."""
        return _dcopy(self._intdipole)

    @property
    def energy(self):
        """."""
        return _dcopy(self._energy)

    @property
    def spread(self):
        """."""
        return _dcopy(self._spread)

    def set_data(self, currents, beam_centers, beam_sizes):
        """."""
        if None in {currents, beam_centers, beam_sizes}:
            return False
        if isinstance(beam_sizes, (int, float)):
            beam_sizes = [beam_sizes]
        if isinstance(beam_centers, (int, float)):
            beam_centers = [beam_centers]
        if isinstance(currents, (int, float)):
            currents = [currents]
        beam_sizes = _np.array(beam_sizes, dtype=float)
        beam_centers = _np.array(beam_centers, dtype=float)
        currents = _np.array(currents, dtype=float)
        cond = beam_sizes.size != currents.size
        cond |= currents.size != beam_centers.size
        if cond:
            return False
        self._beamsize = beam_sizes
        self._beamcenter = beam_centers
        self._currents = currents
        self._perform_analysis()
        return True

    def _update_integrated_dipole(self):
        """."""
        if self._currents.size == 0:
            return
        mult = self._excdata.interp_curr2mult(
            currents=self._currents, only_main_harmonic=True)
        self._intdipole = mult['normal'][0]

    def _perform_analysis(self):
        """."""
        self._update_integrated_dipole()
        cond = self._intdipole.size == 0
        cond |= self._beamcenter.size == 0
        cond |= self._beamsize == 0
        if cond:
            return
        pc_nom = self._intdipole / self._angle * C * 1e-6  # in MeV
        pc = pc_nom * (1 + self._beamcenter / self._dispersion)
        self._energy = _np.sqrt(pc**2 + E0*E0)
        self._spread = self._beamsize / self._dispersion * 100  # in percent%
        self.run_callbacks('Energy-Mon', self._energy)
        self.run_callbacks('Spread-Mon', self._spread)
        self.run_callbacks('IntDipole-Mon', self._intdipole)


class MeasEnergy(_BaseClass, _Const):
    """."""

    def __init__(self, callback=None):
        """."""
        self.energy_calculator = CalcEnergy(callback=callback)
        self.image_processor = _ProcessImage(callback=callback)
        self.image_processor.imageflipx = self.image_processor.ImgFlip.On
        self.image_processor.imageflipy = self.image_processor.ImgFlip.Off
        self._profile = self.DEFAULT_PROFILE
        self._coefx = _PV(
            self.DEFAULT_PROFILE+':X:Gauss:Coef', callback=self._update_coefx)
        self._coefy = _PV(
            self.DEFAULT_PROFILE+':Y:Gauss:Coef', callback=self._update_coefy)
        self._width_source = _PV(self.DEFAULT_PROFILE + ':ROI:MaxSizeX_RBV')
        self._image_source = _PV(
            self.DEFAULT_PROFILE + ':RAW:ArrayData', auto_monitor=False)
        self._current_source = _PV(self.DEFAULT_SPECT + ':Current-Mon')
        super().__init__(callback=callback)
        self._thread = _Repeater(0.5, self.meas_energy, niter=0)
        self._thread.pause()
        self._thread.start()

    def get_map2write(self):
        """."""
        dic_ = self.image_processor.get_map2write()
        dic_.update(self.energy_calculator.get_map2write())
        dic_.update({'MeasureCtrl-Sel': _part(self.write, 'measuring')})
        return dic_

    def get_map2read(self):
        """."""
        dic_ = self.image_processor.get_map2read()
        dic_.update(self.energy_calculator.get_map2read())
        dic_.update({'MeasureCtrl-Sts': _part(self.read, 'measuring')})
        return dic_

    def start(self):
        """."""
        self._thread.resume()
        self.run_callbacks('MeasureCtrl-Sts', 1)

    def stop(self):
        """."""
        self._thread.pause()
        self.run_callbacks('MeasureCtrl-Sts', 0)

    @property
    def connected(self):
        """."""
        conn = self._coefx.connected
        conn &= self._coefy.connected
        conn &= self._width_source.connected
        conn &= self._image_source.connected
        return conn

    @property
    def current(self):
        """."""
        return self._current_source.get()

    @property
    def rate(self):
        """."""
        return 1/self._thread.interval

    @rate.setter
    def rate(self, val):
        """."""
        if isinstance(val, (float, int)) and 0 < val < 4:
            self._thread.interval = 1/val

    @property
    def measuring(self):
        """."""
        return not self._thread.is_paused()

    @measuring.setter
    def measuring(self, val):
        """."""
        if val:
            self.start()
        else:
            self.stop()

    def _update_coefx(self, pvname, value, **kwargs):
        """."""
        if value is None:
            return
        self.image_processor.px2mmscalex = value

    def _update_coefy(self, pvname, value, **kwargs):
        """."""
        if value is None:
            return
        self.image_processor.px2mmscaley = value

    def meas_energy(self):
        """."""
        value = self._width_source.value
        if isinstance(value, (float, int)):
            self.image_processor.imagewidth = int(value)

        self.image_processor.image = self._image_source.get()
        self.energy_calculator.set_data(
            self.current,
            self.image_processor.beamcentermmx,
            self.image_processor.beamsizemmx)
