"""DVF devices."""

import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from .device import DeviceNC as _DeviceNC


class DVF(_DeviceNC):
    """Beam Visualization Device ("Dispositivo de Visualização de Feixe")."""

    class DEVICES:
        """Devices names."""
        CAX_DVF1 = 'CAX:A:BASLER01'
        CAX_DVF2 = 'CAX:B:BASLER01'
        ALL = (CAX_DVF1, CAX_DVF2)

    _default_timeout = 10  # [s]

    _dvfparam_fields = (
        'ACQUISITION_TIME_MIN',  # [s]
        'ACQUISITION_TIME_DEFAULT',  # [s]
        'EXPOSURE_TIME_DEFAULT',  # [s]
        'IMAGE_SIZE_V',  # [pixel]
        'IMAGE_SIZE_H',  # [pixel]
        'IMAGE_PIXEL_SIZE',  # [um]
        'OPTICS_MAGNIFICATION_FACTOR',  # source to image
    )
    #   DVF device :       ((sizey, sizex), pixel_size_um mag_factor
    _dev2params = {
        DEVICES.CAX_DVF1 :
            # DVF1 Today: pixel size 4.8 um; magnification factor 0.5
            _get_namedtuple('DVFParameters',
            _dvfparam_fields, (0.5, 0.5, 0.005, 1024, 1280, 4.8, 0.5)),
        DEVICES.CAX_DVF2 :
            # DVF2 today: pixel size 4.8 um; magnification factor 5.0
            # DVF2 future hifi: pixel size 2.4 um; magnification factor 5.0
            _get_namedtuple('DVFParameters',
            _dvfparam_fields, (0.5, 0.5, 0.005, 1024, 1280, 4.8, 5.0)),
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

    def parameters(self):
        """Return DVF parameters."""
        return self._dev2params[self.devname]

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
    def acquisition_time(self):
        """Camera acquisition time [s]."""
        return self['cam1:AcquirePeriod']

    @acquisition_time.setter
    def acquisition_time(self, value):
        """Camera acquisition time [s]."""
        params = self.parameters
        value = max(value, params.ACQUISITION_TIME_MIN)
        self['cam1:AcquirePeriod'] = value

    @property
    def acquisition_status(self):
        """Return IOC acquisition status."""
        return self['cam1:Acquire']

    @property
    def image_sizeh(self):
        """Image horizontal size (pixels)."""
        params = self.parameters
        return params.IMAGE_SIZE_H

    @property
    def image_sizev(self):
        """Image vertical size (pixels)."""
        params = self.parameters
        return params.IMAGE_SIZE_V

    @property
    def image(self):
        """Return DVF image formatted as a (sizey, sizex) matriz."""
        params = self.parameters
        shape = (params.IMAGE_SIZE_V, params.IMAGE_SIZE_H)
        data = self['image1:ArrayData']
        image = _np.reshape(data, shape)
        return image

    @property
    def image_pixel_size(self):
        """Image pixel size [um]."""
        params = self.parameters
        return params.IMAGE_PIXEL_SIZE

    @property
    def optics_magnefication_factor(self):
        """Source to image magnefication factor."""
        params = self.parameters
        return params.OPTICS_MAGNIFICATION_FACTOR

    @property
    def conv_pixel_2_srcsize(self):
        """Pixel to source size convertion factor."""
        pixel_size = self.image_pixel_size
        mag_factor = self.optics_magnefication_factor
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
        params = self.parameters
        self.exposure_time = params.EXPOSURE_TIME_DEFAULT
        self.acquisition_time = params.ACQUISITION_TIME_DEFAULT
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

