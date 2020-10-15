"""."""

from functools import partial as _part
from epics import PV as _PV

from ...thread import RepeaterThread as _Repeater
from ...clientconfigdb import ConfigDBClient as _ConfigDBClient
from ..util import BaseClass as _BaseClass, ProcessImage as _ProcessImage
from .csdev import Const as _Const


class MeasParameters(_BaseClass, _Const):
    """."""

    def __init__(self, callback=None):
        """."""
        self.image_processor = _ProcessImage(callback=callback)
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
        self._profile = self.DEF_PROFILE
        self._target_posx = self.TARGETX
        self._target_posy = self.TARGETY
        self._needed_dbumpx = 0.0
        self._needed_dbumpy = 0.0
        self._applied_bumpx = 0.0
        self._applied_bumpy = 0.0
        self._need_update = True
        self._apply_status = self.ApplyStatus.Idle
        conf = _ConfigDBClient(config_type='si_orbit')
        self._refs = conf.get_config_value('ref_orb')
        self._sofb_pvs = dict(
            refx_sp=_PV('SI-Glob:AP-SOFB:RefOrbX-SP'),
            refy_sp=_PV('SI-Glob:AP-SOFB:RefOrbY-SP'),
            refx_rb=_PV(
                'SI-Glob:AP-SOFB:RefOrbX-RB', callback=self._set_need_update),
            refy_rb=_PV(
                'SI-Glob:AP-SOFB:RefOrbY-RB', callback=self._set_need_update))

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
            'ApplyBump-Cmd': self.cmd_apply_bump,
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
            'NeededDeltaBumpX-Mon': _part(self.read, 'needed_dbumpx'),
            'NeededDeltaBumpY-Mon': _part(self.read, 'needed_dbumpy'),
            'AppliedBumpX-Mon': _part(self.read, 'applied_bumpx'),
            'AppliedBumpY-Mon': _part(self.read, 'applied_bumpy'),
            'ApplyStatus-Mon': _part(self.read, 'apply_status'),
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
        conn &= all(map(lambda x: x.connected, self._sofb_pvs.values()))
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
    def apply_status(self):
        """Return status of last apply attempt."""
        return self._apply_status

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
    def needed_dbumpx(self):
        """."""
        return self._needed_dbumpx

    @property
    def needed_dbumpy(self):
        """."""
        return self._needed_dbumpy

    @property
    def applied_bumpx(self):
        """."""
        return self._applied_bumpx

    @property
    def applied_bumpy(self):
        """."""
        return self._applied_bumpy

    def cmd_apply_bump(self, *args):
        """Apply Bump to SOFB."""
        _ = args
        if not self.connected:
            self._apply_status = self.ApplyStatus.ConnectionError
            self.run_callbacks('ApplyStatus-Mon', self._apply_status)
            return
        self._update_applied_bumps()
        self._apply_status = self._calc_and_apply_bumps()
        self.run_callbacks('ApplyStatus-Mon', self._apply_status)

    def process_image(self):
        """."""
        if self._need_update:
            self._update_applied_bumps()

        value = self._width_source.value
        if isinstance(value, (float, int)):
            self.image_processor.imagewidth = int(value)

        self.image_processor.image = self._image_source.value
        dltx = self.image_processor.beamcenterx - self._target_posx
        dlty = self.image_processor.beamcentery - self._target_posy
        dltx *= self.image_processor.px2mmscalex * 1e-3  # mm --> m
        dlty *= self.image_processor.px2mmscaley * 1e-3  # mm --> m

        self._needed_dbumpx = -dltx / self.DIST_FROM_SRC * 1e6  # rad --> urad
        # NOTE: this signal asymmetry is due to the x-flip of the image and
        # the beamline optics.
        self._needed_dbumpy = dlty / self.DIST_FROM_SRC * 1e6  # rad --> urad

        self.run_callbacks('NeededDeltaBumpX-Mon', self._needed_dbumpx)
        self.run_callbacks('NeededDeltaBumpY-Mon', self._needed_dbumpy)

    def _update_applied_bumps(self):
        if not self.connected:
            return
        orbx = self._sofb_pvs['refx_rb'].value
        orby = self._sofb_pvs['refy_rb'].value
        if orbx is None or orby is None:
            return

        dx1 = orbx[self.BPM1_INDEX] - self._refs['x'][self.BPM1_INDEX]
        dx2 = orbx[self.BPM2_INDEX] - self._refs['x'][self.BPM2_INDEX]
        dy1 = orby[self.BPM1_INDEX] - self._refs['y'][self.BPM1_INDEX]
        dy2 = orby[self.BPM2_INDEX] - self._refs['y'][self.BPM2_INDEX]

        self._applied_bumpx = (dx2 - dx1) / self.SS_SIZE  # already in [urad]
        self._applied_bumpy = (dy2 - dy1) / self.SS_SIZE

        self.run_callbacks('AppliedBumpX-Mon', self._applied_bumpx)
        self.run_callbacks('AppliedBumpY-Mon', self._applied_bumpy)
        self._need_update = False

    def _calc_and_apply_bumps(self):
        dbumpx = self._needed_dbumpx
        dbumpy = self._needed_dbumpy
        total_bumpx = dbumpx + self._applied_bumpx
        total_bumpy = dbumpy + self._applied_bumpy

        maxb = max(abs(total_bumpx), abs(total_bumpy))
        if maxb > self.MAX_BUMP:
            return self.ApplyStatus.LimitExceeded

        dax = dbumpx * self.SS_SIZE / 2
        day = dbumpy * self.SS_SIZE / 2

        orbx = self._sofb_pvs['refx_rb'].value.copy()
        orby = self._sofb_pvs['refy_rb'].value.copy()
        orbx[self.BPM1_INDEX] -= dax
        orby[self.BPM1_INDEX] -= day
        orbx[self.BPM2_INDEX] += dax
        orby[self.BPM2_INDEX] += day

        self._sofb_pvs['refx_sp'].value = orbx
        self._sofb_pvs['refy_sp'].value = orby
        return self.ApplyStatus.Applied

    def _set_need_update(self, *args, **kwargs):
        _ = args
        _ = kwargs
        self._need_update = True
