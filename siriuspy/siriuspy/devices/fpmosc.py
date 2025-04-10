"""."""

import numpy as _np

from ..currinfo.csdev import Const as _Const
from .device import Device as _Device


class FPMOsc(_Device):
    """."""

    OffOn = _Const.OffOn

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:DI-FPMOsc'
        ALL = (SI, )

    PROPERTIES_DEFAULT = (
        'FPUpdateTime-SP',
        'FPUpdateTime-RB',
        'FPFiducialOffset-SP',
        'FPFiducialOffset-RB',
        'FPRef-SP',
        'FPRef-RB',
        'FPUniFillEqCurrent-Mon',
        'FPErrorRelStd-Mon',
        'FPErrorKLDiv-Mon',
        'FPRef-Mon',
        'FP-Mon',
        # 'FPTimeOffset-Mon',
        # 'FPTime-Mon',
        # 'FPRaw-Mon',
        # 'FPRawAmp-Mon',
        # 'FPRawTime-Mon',
    )

    def __init__(self, devname=None, props2init='all'):
        """."""
        # check if device exists
        devname = devname or FPMOsc.DEVICES.SI
        if devname not in FPMOsc.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def update_time(self):
        """."""
        return self['FPUpdateTime-RB']

    @update_time.setter
    def update_time(self, value):
        """."""
        self['FPUpdateTime-SP'] = value

    @property
    def fiducial_offset(self):
        """."""
        return self['FPFiducialOffset-RB']

    @fiducial_offset.setter
    def fiducial_offset(self, value):
        self['FPFiducialOffset-SP'] = value

    @property
    def fill_pattern_ref(self):
        """."""
        return self['FPRef-RB']

    @fill_pattern_ref.setter
    def fill_pattern_ref(self, value):
        """."""
        if not isinstance(value, (_np.ndarray, list, tuple)):
            return
        value = _np.array(value)
        if value.size != _Const.FP_HARM_NUM:
            return
        self['FPRef-SP'] = value

    @property
    def fill_pattern_ref_mon(self):
        """."""
        return self['FPRef-Mon']

    @property
    def fill_pattern(self):
        """."""
        return self['FP-Mon']

    @property
    def uniform_fill_equiv_current(self):
        """."""
        return self['FPUniFillEqCurrent-Mon']

    @property
    def error_relative_std(self):
        """."""
        return self['FPErrorRelStd-Mon']

    @property
    def error_kl_divergence(self):
        """."""
        return self['FPErrorKLDiv-Mon']

    @property
    def time_offset(self):
        """."""
        return self['FPTimeOffset-Mon']

    @property
    def fill_pattern_time(self):
        """."""
        return self['FPTime-Mon']

    @property
    def fill_pattern_raw(self):
        """."""
        return self['FPRaw-Mon']

    @property
    def fill_pattern_raw_time(self):
        """."""
        return self['FPRawTime-Mon']
