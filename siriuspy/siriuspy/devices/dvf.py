"""DVF devices."""

import numpy as _np

from .device import DeviceNC as _DeviceNC


class DVF(_DeviceNC):
    """."""

    class DEVICES:
        """Devices names."""
        CAX_DVF1 = 'CAX:A:BASLER01'
        CAX_DVF2 = 'CAX:B:BASLER01'
        ALL = (CAX_DVF1, CAX_DVF2)

    MIN_ACQUISITION_PERIOD = 0.5  # [s]

    _default_timeout = 10  # [s]
    _DEV2SHAPE = {
        DEVICES.CAX_DVF1 : (1024, 1280),
        DEVICES.CAX_DVF2 : (1024, 1280),
    }

    _properties = (
        'ffmstream1:EnableCallbacks', 'ffmstream1:EnableCallbacks_RBV',
        'Trans1:EnableCallbacks', 'Trans1:EnableCallbacks_RBV',
        'cam1:ArrayCallbacks', 'cam1:ArrayCallbacks_RBV',
        'cam1:AcquireTime', 'cam1:AcquireTime_RBV',
        'cam1:AcquirePeriod', 'cam1:AcquirePeriod_RBV',
        'cam1:Acquire',
        'image1:EnableCallbacks', 'image1:EnableCallbacks_RBV',
        'image1:ArrayData',
        )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in DVF.DEVICES.ALL:
            raise NotImplementedError(devname)
        # call base class constructor
        super().__init__(devname, properties=DVF._properties)

    @property
    def exposure_time(self):
        """Camera exposure time [s]."""
        return self['cam1:AcquireTime']

    @exposure_time.setter
    def exposure_time(self, value):
        """Camera exposure time [s]."""
        value = max(value, 0)
        self['cam1:AcquireTime'] = value

    @property
    def acquisition_period(self):
        """Camera acquisition period [s]."""
        return self['cam1:AcquirePeriod']

    @acquisition_period.setter
    def acquisition_period(self, value):
        """Camera acquisition period [s]."""
        value = max(value, DVF.MIN_ACQUISITION_PERIOD)
        self['cam1:AcquirePeriod'] = value

    @property
    def acquisition_status(self):
        """Return IOC acquisition status."""
        return self['cam1:Acquire']

    def reset_device(self):
        """."""
        self['cam1:EnableCallbacks'] = 1  # Enable
        self['image1:EnableCallbacks'] = 1  # Enable
        self['ffmstream1:EnableCallbacks'] = 1  # Enable
        self['Trans1:EnableCallbacks'] = 1  # Enable

    def acquire_image(self):
        """."""
        data = self['image1:ArrayData']
        shape = DVF._DEV2SHAPE[self.devname]
        image = _np.reshape(data, shape)
        return image

    def cmd_acquire_on(self, timeout=None):
        """."""
        self._cmd_acquire(1, timeout=timeout)

    def cmd_acquire_off(self, timeout=None):
        """."""
        self._cmd_acquire(0, timeout=timeout)

    def _cmd_acquire(self, value, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        propty = 'cam1:Acquire'
        self[propty] = value
        self._wait(propty + '_RBV', value, timeout=timeout, comp='eq')

