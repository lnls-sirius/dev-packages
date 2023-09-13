"""PosAng Device."""

from .device import Device as _Device


class PosAng(_Device):
    """Device to control position and angle correction IOC."""

    class DEVICES:
        """Devices names."""

        TB = 'TB-Glob:AP-PosAng'
        TS = 'TS-Glob:AP-PosAng'
        ALL = (TB, TS)

    PROPERTIES_DEFAULT = (
        'DeltaPosX-SP', 'DeltaPosX-RB',
        'DeltaAngX-SP', 'DeltaAngX-RB',
        'DeltaPosY-SP', 'DeltaPosY-RB',
        'DeltaAngY-SP', 'DeltaAngY-RB',
        'SetNewRefKick-Cmd', 'NeedRefUpdate-Mon',
        'ConfigName-SP', 'ConfigName-RB',
        'RespMatX-Mon', 'RespMatY-Mon',
        )

    def __init__(self, devname, props2init='all'):
        """Init."""
        # check if device exists
        if devname not in PosAng.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def delta_posx(self):
        """Delta PosX."""
        return self['DeltaPosX-RB']

    @delta_posx.setter
    def delta_posx(self, value):
        self['DeltaPosX-SP'] = value

    @property
    def delta_angx(self):
        """Delta AngX."""
        return self['DeltaAngX-RB']

    @delta_angx.setter
    def delta_angx(self, value):
        self['DeltaAngX-SP'] = value

    @property
    def delta_posy(self):
        """Delta PosY."""
        return self['DeltaPosY-RB']

    @delta_posy.setter
    def delta_posy(self, value):
        self['DeltaPosY-SP'] = value

    @property
    def delta_angy(self):
        """Delta AngY."""
        return self['DeltaAngY-RB']

    @delta_angy.setter
    def delta_angy(self, value):
        self['DeltaAngY-SP'] = value

    @property
    def config_name(self):
        """PosAng configuration name."""
        return self['ConfigName-RB']

    @config_name.setter
    def config_name(self, value):
        self['ConfigName-SP'] = value

    @property
    def respmat_x(self):
        """Response matrix for PosAngX."""
        return self['RespMatX-Mon'].reshape(2, -1)

    @property
    def respmat_y(self):
        """Response matrix for PosAngY."""
        return self['RespMatY-Mon'].reshape(2, -1)

    @property
    def need_ref_update(self):
        """Need Reference Update."""
        return self['NeedRefUpdate-Mon']

    def cmd_update_reference(self):
        """Update PosAng reference kicks."""
        self['SetNewRefKick-Cmd'] = 1
        return True
