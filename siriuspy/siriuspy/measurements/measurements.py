
from functools import partial as _part
import numpy as _np
from epics import PV as _PV
import mathphys.constants as _consts
from threading import Event as _Event
from siriuspy.thread import RepeaterThread as _Repeater
from siriuspy.search import PSSearch as _PSS
from siriuspy.factory import NormalizerFactory as _NormFact
from .calculations import CalcEnergy, ProcessImage
from .base import BaseClass as _BaseClass

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-9  # in GeV


class MeasEnergy(_BaseClass):
    """."""

    def __init__(self):
        """."""
        prof = 'LA-BI:PRF4'
        self.energy_calculator = CalcEnergy()
        self.image_processor = ProcessImage()
        self.image_processor.readingorder = self.image_processor.CLIKE
        self._profile = prof
        self._coefx = _PV(
            prof+':X:Gauss:Coef', callback=_part(self._update_coef, pln='x'))
        self._coefy = _PV(
            prof+':Y:Gauss:Coef', callback=_part(self._update_coef, pln='y'))
        self._width_source = _PV(
            prof + ':ROI:MaxSizeX_RBV', callback=self._update_width)
        self._image_source = _PV(prof + ':RAW:ArrayData')
        self._current_source = _PV('LA-CN:H1DPPS-1:seti')
        self._thread = _Repeater(0.5, self._meas_energy, niter=0)
        self._thread.pause()
        self._thread.start()

    def get_map2write(self):
        database = dict()
        dic_ = self.image_processor.get_map2write()
        dic_.update(self.energy_calculator.get_map2write())
        dic_.update({'MeasureCtrl-Cmd': _part(self.write, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    def get_map2read(self):
        database = dict()
        dic_ = self.image_processor.get_map2read()
        dic_.update(self.energy_calculator.get_map2read())
        dic_.update({'MeasureSts-Mon': _part(self.read, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    def start(self):
        """."""
        self._thread.resume()

    def stop(self):
        """."""
        self._thread.pause()

    @property
    def rate(self):
        """."""
        return 1/self._thread.interval

    @rate.setter
    def rate(self, val):
        if isinstance(val, (float, int)) and 0 < val < 4:
            self._thread.interval = 1/val

    @property
    def measuring(self):
        """."""
        return not self._thread.is_paused()

    @measuring.setter
    def measuring(self, val):
        return self.start() if val else self.stop()

    def _update_coef(self, _, val, pln='x', **kwargs):
        if val is None:
            return
        if pln.startswith('x'):
            self.image_processor.pxl2mmscalex = val
        elif pln.startswith('y'):
            self.image_processor.pxl2mmscaley = val

    def _update_width(self, _, val, **kwargs):
        if isinstance(val, (float, int)):
            self.image_processor.imagewidth = int(val)

    def _meas_energy(self):
        self.image_processor.image = self._image_source.get()
        self.energy_calculator.set_data(
            self._current_source.get(),
            self.image_processor.beamcentermmx,
            self.image_processor.beamsizemmx)


class CalcEmmitance(_BaseClass):
    X = 0
    Y = 1
    PLACES = ('li', 'tb-qd2a', 'tb-qf2a')

    def __init__(self):
        super().__init__()
        self._measuring = _Event()
        self.emittance_calculator = CalcEmmitance()
        self.image_processor = ProcessImage()
        self.image_processor.readingorder = self.image_processor.CLIKE
        self._place = 'li'
        self._select_experimental_setup()

    def get_map2write(self):
        database = dict()
        dic_ = self.image_processor.get_map2write()
        dic_.update(self.emittance_calculator.get_map2write())
        dic_.update({'MeasureCtrl-Cmd': _part(self.write, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    def get_map2read(self):
        database = dict()
        dic_ = self.image_processor.get_map2read()
        dic_.update(self.emittance_calculator.get_map2read())
        dic_.update({'MeasureSts-Mon': _part(self.read, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, val):
        if val in self.PLACES:
            self._place = val
            self._select_experimental_setup()

    def _select_experimental_setup(self):
        self.emittance_calculator.place = self._place
        if self._place.lower().startswith('li'):
            prof = 'LA-BI:PRF5'
            self._image_source = _PV(prof+':RAW:ArrayData')
            self._width_source = _PV(
                prof+':ROI:MaxSizeX_RBV', callback=self._update_width)
            self._coefx = _PV(
                prof+':X:Gauss:Coef',
                callback=_part(self._update_coef, pln='x'))
            self._coefy = _PV(
                prof+':Y:Gauss:Coef',
                callback=_part(self._update_coef, pln='y'))
            self.quad_I_sp = _PV('LI-01:PS-QF3:seti')
            self.quad_I_rb = _PV('LI-01:PS-QF3:rdi')
        elif self._place.lower().startswith('tb'):
            self._image_source = _PV('TB-02:DI-Scrn-2:ImgData-Mon')
            self._width_source = _PV(
                'TB-02:DI-Scrn-2:ImgMaxWidth-Cte', callback=self._update_width)
            self._coefx = _PV(
                'TB-02:DI-ScrnCam-2:ImgScaleFactorX-RB',
                callback=_part(self._update_coef, pln='x'))
            self._coefy = _PV(
                'TB-02:DI-ScrnCam-2:ImgScaleFactorY-RB',
                callback=_part(self._update_coef, pln='y'))
            quad = self.emittance_calculator.quadname
            self.quad_I_sp = _PV(quad + ':Current-SP')
            self.quad_I_rb = _PV(quad + ':Current-RB')

    def _update_coef(self, _, val, pln='x', **kwargs):
        if val is None:
            return
        if pln.startswith('x'):
            self.image_processor.pxl2mmscalex = val
        elif pln.startswith('y'):
            self.image_processor.pxl2mmscaley = val

    def _update_width(self, _, val, **kwargs):
        if isinstance(val, (float, int)):
            self.image_processor.imagewidth = int(val)

    def _acquire_data(self):
        samples = self.spbox_samples.value()
        nsteps = self.spbox_steps.value()
        I_ini = self.spbox_I_ini.value()
        I_end = self.spbox_I_end.value()

        pl = 'y' if self.cbbox_plane.currentIndex() else 'x'
        curr_list = np.linspace(I_ini, I_end, nsteps)
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
