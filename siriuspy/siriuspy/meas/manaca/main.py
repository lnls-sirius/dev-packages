"""."""

from functools import partial as _part
from epics import PV as _PV

from ...thread import RepeaterThread as _Repeater
from ..util import BaseClass as _BaseClass, ProcessImage as _ProcessImage
from .csdev import Const as _Const


class MeasParameters(_BaseClass, _Const):
    """."""

    def __init__(self, callback=None):
        """."""
        self.image_processor = _ProcessImage(callback=callback)
        self._profile = self.DEF_PROFILE
        self._target_posx = self.TARGETX
        self._target_posy = self.TARGETY
        self._sofb_bumpx = 0.0
        self._sofb_bumpy = 0.0
        self.image_processor.px2mmscalex = self.DEF_COEFX
        self.image_processor.px2mmscaley = self.DEF_COEFY
        self.image_processor.roiautocenter = self.AutoCenter.Manual
        self.image_processor.imageflipx = self.image_processor.ImgFlip.On
        self.image_processor.imageflipy = self.image_processor.ImgFlip.Off
        self.image_processor.roisizex = self.DEF_ROISIZE
        self.image_processor.roisizey = self.DEF_ROISIZE
        self.image_processor.roicenterx = self.TARGETX
        self.image_processor.roicentery = self.TARGETY
        self.image_processor.method = self.Method.Moments

        self._width_source = _PV(self._profile + 'cam1:ArraySizeX_RBV')
        self._image_source = _PV(
            self._profile+'image1:ArrayData', auto_monitor=True)
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
            'TargetPosX-SP': _part(self.write, 'target_posx'),
            'TargetPosY-SP': _part(self.write, 'target_posy'),
            })
        return dic_

    def get_map2read(self):
        """."""
        dic_ = self.image_processor.get_map2read()
        dic_.update({
            'MeasureCtrl-Sts': _part(self.read, 'measuring'),
            'MeasureRate-RB': _part(self.read, 'rate'),
            'TargetPosX-RB': _part(self.read, 'target_posx'),
            'TargetPosY-RB': _part(self.read, 'target_posy'),
            'SOFBBumpX-RB': _part(self.read, 'sofb_bumpx'),
            'SOFBBumpY-RB': _part(self.read, 'sofb_bumpy'),
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
        if isinstance(val, (float, int)) and 0 < val < 30:
            self._thread.interval = 1/val
            self.run_callbacks('MeasureRate-RB', val)

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

    @property
    def target_posx(self):
        """."""
        return self._target_posx

    @target_posx.setter
    def target_posx(self, val):
        """."""
        if isinstance(val, (float, int)):
            self._target_posx = val
            self.run_callbacks('TargetPosX-RB', val)

    @property
    def target_posy(self):
        """."""
        return self._target_posy

    @target_posy.setter
    def target_posy(self, val):
        """."""
        if isinstance(val, (float, int)):
            self._target_posy = val
            self.run_callbacks('TargetPosY-RB', val)

    @property
    def sofb_bumpx(self):
        """."""
        return self._sofb_bumpx

    @property
    def sofb_bumpy(self):
        """."""
        return self._sofb_bumpy

    def process_image(self):
        """."""
        value = self._width_source.value
        if isinstance(value, (float, int)):
            self.image_processor.imagewidth = int(value)

        self.image_processor.image = self._image_source.value
        dltx = self.image_processor.beamcenterx - self._target_posx
        dlty = self.image_processor.beamcentery - self._target_posy
        dltx *= self.image_processor.px2mmscalex * 1e-3  # mm --> m
        dlty *= self.image_processor.px2mmscaley * 1e-3  # mm --> m

        self._sofb_bumpx = -dltx / self.DIST_FROM_SRC * 1e6  # rad --> urad
        # NOTE: this signal asymmetry is due to the x-flip of the image and
        # the beamline optics.
        self._sofb_bumpy = dlty / self.DIST_FROM_SRC * 1e6  # rad --> urad

        self.run_callbacks('SOFBBumpX-Mon', self._sofb_bumpx)
        self.run_callbacks('SOFBBumpY-Mon', self._sofb_bumpy)
