"""."""

from functools import partial as _part
from threading import Event as _Event
import numpy as _np
from epics import PV as _PV

import mathphys.constants as _consts

from ..thread import RepeaterThread as _Repeater
from .calculations import CalcEnergy, ProcessImage
from .base import BaseClass as _BaseClass

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-9  # in GeV


class MeasEnergy(_BaseClass):
    """."""

    def __init__(self, callback=None):
        """."""
        self.energy_calculator = CalcEnergy(callback=callback)
        self.image_processor = ProcessImage(callback=callback)
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
        self.image_processor.imageflipx = self.image_processor.ImgFlip.On
        self.image_processor.imageflipy = self.image_processor.ImgFlip.Off
        value = self._width_source.value
        if isinstance(value, (float, int)):
            self.image_processor.imagewidth = int(value)

        self.image_processor.image = self._image_source.get()
        self.energy_calculator.set_data(
            self.current,
            self.image_processor.beamcentermmx,
            self.image_processor.beamsizemmx)


class CalcEmmitance(_BaseClass):
    X = 0
    Y = 1
    PLACES = ('li', 'tb-qd2a', 'tb-qf2a')

    def __init__(self):
        """."""
        super().__init__()
        self._measuring = _Event()
        self.emittance_calculator = CalcEmmitance()
        self.image_processor = ProcessImage()
        self.image_processor.readingorder = \
            self.image_processor.ReadingOrder.CLike
        self._place = 'li'
        self._select_experimental_setup()

    def get_map2write(self):
        """."""
        database = dict()
        dic_ = self.image_processor.get_map2write()
        dic_.update(self.emittance_calculator.get_map2write())
        dic_.update({'MeasureCtrl-Sel': _part(self.write, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    def get_map2read(self):
        """."""
        database = dict()
        dic_ = self.image_processor.get_map2read()
        dic_.update(self.emittance_calculator.get_map2read())
        dic_.update({'MeasureCtrl-Sts': _part(self.read, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    @property
    def place(self):
        """."""
        return self._place

    @place.setter
    def place(self, val):
        """."""
        if val in self.PLACES:
            self._place = val
            self._select_experimental_setup()

    def _select_experimental_setup(self):
        """."""
        self.emittance_calculator.place = self._place
        if self._place.lower().startswith('li'):
            prof = 'LA-BI:PRF5'
            self._image_source = _PV(prof+':RAW:ArrayData')
            self._width_source = _PV(
                prof+':ROI:MaxSizeX_RBV', callback=self._update_width)
            self._coefx = _PV(
                prof+':X:Gauss:Coef',
                callback=self._update_coefx)
            self._coefy = _PV(
                prof+':Y:Gauss:Coef',
                callback=self._update_coefy)
            self.quad_I_sp = _PV('LI-01:PS-QF3:Current-SP')
            self.quad_I_rb = _PV('LI-01:PS-QF3:Current-Mon')
        elif self._place.lower().startswith('tb'):
            self._image_source = _PV('TB-02:DI-Scrn-2:ImgData-Mon')
            self._width_source = _PV(
                'TB-02:DI-Scrn-2:ImgMaxWidth-Cte', callback=self._update_width)
            self._coefx = _PV(
                'TB-02:DI-ScrnCam-2:ImgScaleFactorX-RB',
                callback=self._update_coefx)
            self._coefy = _PV(
                'TB-02:DI-ScrnCam-2:ImgScaleFactorY-RB',
                callback=self._update_coefy)
            quad = self.emittance_calculator.quadname
            self.quad_I_sp = _PV(quad + ':Current-SP')
            self.quad_I_rb = _PV(quad + ':Current-RB')

    def _update_coefx(self, pvname, value, **kwargs):
        """."""
        if value is None:
            return
        self.image_processor.pxl2mmscalex = value

    def _update_coefy(self, pvname, value, **kwargs):
        """."""
        if value is None:
            return
        self.image_processor.pxl2mmscaley = value

    def _update_width(self, pvname, value, **kwargs):
        """."""
        if isinstance(value, (float, int)):
            self.image_processor.imagewidth = int(value)

    def _acquire_data(self):
        """."""
        samples = self.spbox_samples.value()
        nsteps = self.spbox_steps.value()
        I_ini = self.spbox_I_ini.value()
        I_end = self.spbox_I_end.value()

        pl = 'y' if self.cbbox_plane.currentIndex() else 'x'
        curr_list = _np.linspace(I_ini, I_end, nsteps)
        sigma = []
        I_meas = []
        for i, I in enumerate(curr_list):
            print('setting Quadrupole to ', I)
            if not SIMUL:
                self.quad_I_sp.put(I, wait=True)
            self._measuring.wait(5 if i else 15)
            j = 0
            I_tmp = []
            sig_tmp = []
            while j < samples:
                if self._measuring.is_set():
                    print('Stopped')
                    return
                print('measuring sample', j)
                I_now = self.quad_I_rb.value
                cen_x, sigma_x, cen_y, sigma_y = self.plt_image.get_params()
                mu, sig = (cen_x, sigma_x) if pl == 'x' else (cen_y, sigma_y)
                max_size = self.spbox_threshold.value()*1e-3
                if sig > max_size:
                    self._measuring.wait(1)
                    continue
                I_tmp.append(I_now)
                sig_tmp.append(abs(sig))
                self._measuring.wait(0.5)
                j += 1
            ind = np.argsort(sig_tmp)
            I_tmp = np.array(I_tmp)[ind]
            sig_tmp = np.array(sig_tmp)[ind]
            I_meas.extend(I_tmp[6:-6])
            sigma.extend(sig_tmp[6:-6])
        self._measuring.set()
        print('Finished!')
        self.I_meas = I_meas
        self.sigma = sigma
        self.plane_meas = pl
