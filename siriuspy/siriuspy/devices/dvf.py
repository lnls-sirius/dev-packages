"""DVF devices."""

import numpy as _np

from .device import DeviceNC as _DeviceNC


class DVF(_DeviceNC):
    """Beam Visualization Device ("Dispositivo de Visualização de Feixe")."""

    class DEVICES:
        """Devices names."""
        CAX_DVF1 = 'CAX:A:BASLER01'
        CAX_DVF2 = 'CAX:B:BASLER01'
        ALL = (CAX_DVF1, CAX_DVF2)

    MIN_ACQUISITION_PERIOD = 0.5  # [s]
    DEF_EXPOSURE_TIME = 0.005  # [s]
    DEF_ACQUISITION_PERIOD = MIN_ACQUISITION_PERIOD

    _default_timeout = 10  # [s]

    # NOTE: for DVF2 preliminary bem bump measurements show that
    # the conversion pixel -> source size is close to nominal 1.0
    # within 10%
    _DEV2PROPTIES = {
        # DVF device       ((sizey, sizex), conv_pixel_2_srcsize
        DEVICES.CAX_DVF1 : ((1024, 1280), None),  # NOTE: not implemented
        DEVICES.CAX_DVF2 : ((1024, 1280), 1.0),
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
        """Init."""
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

    @property
    def image_sizex(self):
        """Image horizontal size (pixels)."""
        shape, *_ = DVF._DEV2PROPTIES[self.devname]
        return shape[1]

    @property
    def image_sizey(self):
        """Image vertical size (pixels)."""
        shape, *_ = DVF._DEV2PROPTIES[self.devname]
        return shape[0]

    @property
    def image(self):
        """Return DVF image formatted as a (sizey, sizex) matriz."""
        data = self['image1:ArrayData']
        shape, *_ = DVF._DEV2PROPTIES[self.devname]
        image = _np.reshape(data, shape)
        return image

    @property
    def conv_pixel_2_srcsize(self):
        """Image horizontal size (pixels)."""
        _, conv_pixel_2_physize, *_ = DVF._DEV2PROPTIES[self.devname]
        return conv_pixel_2_physize

    def reset_device(self):
        """Reset DVF to a standard configuration."""
        self['cam1:EnableCallbacks'] = 1  # Enable
        self['image1:EnableCallbacks'] = 1  # Enable
        self['ffmstream1:EnableCallbacks'] = 1  # Enable
        self['Trans1:EnableCallbacks'] = 1  # Enable
        self.exposure_time = DVF.DEF_EXPOSURE_TIME
        self.acquisition_period = DVF.DEF_ACQUISITION_PERIOD

    def cmd_acquire_on(self, timeout=None):
        """Tune IOC image acquisition on."""
        self._set_and_wait('cam1:Acquire', 1, timeout=timeout)

    def cmd_acquire_off(self, timeout=None):
        """Tune IOC image acquisition off."""
        self._set_and_wait('cam1:Acquire', 0, timeout=timeout)

    def _set_and_wait(self, propty, value, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        self[propty] = value
        self._wait(propty + '_RBV', value, timeout=timeout, comp='eq')

