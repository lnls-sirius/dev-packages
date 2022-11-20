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

    #   DVF device :       ((sizey, sizex), pixel_size_um mag_factor
    _DEV2PROPTIES = {
        # DVF1 Today: pixel size 4.8 um; magnification factor 0.5
        DEVICES.CAX_DVF1 : ((1024, 1280), 4.8, 0.5),
        # DVF2 Today: pixel size 4.8 um; magnification factor 5.0
        # DVF2 Future HiFi: pixel size 2.4 um; magnification factor 5.0
        DEVICES.CAX_DVF2 : ((1024, 1280), 4.8, 5.0),
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
    def image_pixel_size(self):
        """Image pixel size [um]."""
        _, pixel_size, *_ = DVF._DEV2PROPTIES[self.devname]
        return pixel_size

    @property
    def image_magnefication_factor(self):
        """Source to image magnefication factor."""
        _, _, mag_factor, *_ = DVF._DEV2PROPTIES[self.devname]
        return mag_factor

    @property
    def conv_pixel_2_srcsize(self):
        """Pixel to source size convertion factor."""
        pixel_size = self.image_pixel_size
        mag_factor = self.image_magnefication_factor
        pixel2srcsize = pixel_size / mag_factor
        return pixel2srcsize

    def cmd_reset(self, timeout=None):
        """Reset DVF to a standard configuration."""
        props_values = {
            'cam1:EnableCallbacks': 1,  # Enable
            'image1:EnableCallbacks': 1,  # Enable
            'ffmstream1:EnableCallbacks': 1,  # Enable
            'Trans1:EnableCallbacks': 1,  # Enable    
        }
        for propty, value in props_values.items():
            self[propty] = value
        self.exposure_time = DVF.DEF_EXPOSURE_TIME
        self.acquisition_period = DVF.DEF_ACQUISITION_PERIOD
        for propty, value in props_values.items():
            self._wait(propty, value, timeout=timeout, comp='eq')

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

