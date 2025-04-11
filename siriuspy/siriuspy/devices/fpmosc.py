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
        'UpdateTime-SP',
        'UpdateTime-RB',
        'FiducialOffset-SP',
        'FiducialOffset-RB',
        'FillPatternRef-SP',
        'FillPatternRef-RB',
        'UniFillEqCurrent-Mon',
        'ErrorRelStd-Mon',
        'ErrorKLDiv-Mon',
        'FillPatternRef-Mon',
        'FillPattern-Mon',
        # 'TimeOffset-Mon',
        # 'Time-Mon',
        # 'Raw-Mon',
        # 'RawAmp-Mon',
        # 'RawTime-Mon',
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
        return self['UpdateTime-RB']

    @update_time.setter
    def update_time(self, value):
        """."""
        self['UpdateTime-SP'] = value

    @property
    def fiducial_offset(self):
        """."""
        return self['FiducialOffset-RB']

    @fiducial_offset.setter
    def fiducial_offset(self, value):
        self['FiducialOffset-SP'] = value

    @property
    def fill_pattern_ref(self):
        """."""
        return self['FillPatternRef-RB']

    @fill_pattern_ref.setter
    def fill_pattern_ref(self, value):
        """."""
        if not isinstance(value, (_np.ndarray, list, tuple)):
            raise TypeError('Value must be list, tuple or numpy.ndarray.')
        value = _np.array(value)
        if value.size != _Const.FP_HARM_NUM:
            raise ValueError('Value size must be the harmonic number.')
        self['FillPatternRef-SP'] = value

    @property
    def fill_pattern_ref_mon(self):
        """."""
        return self['FillPatternRef-Mon']

    @property
    def fill_pattern(self):
        """."""
        return self['FillPattern-Mon']

    @property
    def uniform_fill_equiv_current(self):
        """."""
        return self['UniFillEqCurrent-Mon']

    @property
    def error_relative_std(self):
        """."""
        return self['ErrorRelStd-Mon']

    @property
    def error_kl_divergence(self):
        """."""
        return self['ErrorKLDiv-Mon']

    @property
    def time_offset(self):
        """."""
        return self['TimeOffset-Mon']

    @property
    def fill_pattern_time(self):
        """."""
        return self['Time-Mon']

    @property
    def fill_pattern_raw(self):
        """."""
        return self['Raw-Mon']

    @property
    def fill_pattern_raw_time(self):
        """."""
        return self['RawTime-Mon']
