"""."""

from functools import partial as _part
from epics import PV as _PV

import mathphys.constants as _consts

from ...thread import RepeaterThread as _Repeater

from ..util import BaseClass as _BaseClass, ProcessImage as _ProcessImage

from .csdev import Const as _Const

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-6  # in MeV


class MeasParameters(_BaseClass, _Const):
    """."""

    def __init__(self, callback=None):
        """."""
        self.image_processor = _ProcessImage(callback=callback)
        self._profile = self.DEF_PROFILE
        self.image_processor.px2mmscalex = self.DEF_COEFX
        self.image_processor.px2mmscaley = self.DEF_COEFY

        self._width_source = _PV(self._profile + 'cam1:ArraySizeX_RBV')
        self._image_source = _PV(
            self._profile+'image1:ArrayData', auto_monitor=False)
        super().__init__(callback=callback)
        self._thread = _Repeater(1/self.DEF_RATE, self.process_image, niter=0)
        self._thread.pause()
        self._thread.start()

    def get_map2write(self):
        """."""
        dic_ = self.image_processor.get_map2write()
        dic_.update({
            'MeasureCtrl-Sel': _part(self.write, 'measuring'),
            'MeasureRate-SP': _part(self.write, 'rate'),
            })
        return dic_

    def get_map2read(self):
        """."""
        dic_ = self.image_processor.get_map2read()
        dic_.update({
            'MeasureCtrl-Sts': _part(self.read, 'measuring'),
            'MeasureRate-RB': _part(self.read, 'rate'),
            })
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
        conn = self._width_source.connected
        conn &= self._image_source.connected
        return conn

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

    def process_image(self):
        """."""
        self.image_processor.imageflipx = self.image_processor.ImgFlip.On
        self.image_processor.imageflipy = self.image_processor.ImgFlip.Off
        value = self._width_source.value
        if isinstance(value, (float, int)):
            self.image_processor.imagewidth = int(value)

        self.image_processor.image = self._image_source.get()
