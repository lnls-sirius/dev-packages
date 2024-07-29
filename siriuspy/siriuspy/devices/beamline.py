"""Beamline devices."""

from .device import Device as _Device


class BeamLineMirror(_Device):
    """Beamline control."""

    class DEVICES:
        """Devices names."""

        CAX = 'CAX:A:PP01'
        ALL = (CAX, )

    PROPERTIES_DEFAULT = (
        ':A', ':A.RBV',
        ':B', ':B.RBV',
        ':C', ':C.RBV',
        ':D', ':D.RBV',
        ':E', ':E.RBV',
        )

    def __init__(self, devname, props2init='all', **kwargs):
        """Init."""
        if devname not in BeamLineMirror.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init, **kwargs)

    @property
    def m1_pos_ry(self):
        """Return mirror M1 linear position axis for Ry [mm]."""
        return [':A.RBV']

    @m1_pos_ry.setter
    def m1_pos_ry(self, value):
        """Set mirror M1 linear position axis for Ry [mm]."""
        self[':A'] = value

    @property
    def m1_pos_tx(self):
        """Return mirror M1 linear position axis for Tx [mm]."""
        return [':B.RBV']

    @m1_pos_tx.setter
    def m1_pos_tx(self, value):
        """Set mirror M1 linear position axis for Tx [mm]."""
        self[':B.RBV'] = value

    @property
    def m1_pos_y1(self):
        """Return mirror M1 linear position y1 for Rx, Rz and Ty [mm]."""
        return [':C.RBV']

    @m1_pos_y1.setter
    def m1_pos_y1(self, value):
        """Set mirror M1 linear position y1 for Rx, Rz and Ty [mm]."""
        self[':C.RBV'] = value

    @property
    def m1_pos_y2(self):
        """Return mirror M1 linear position y2 for Rx, Rz and Ty [mm]."""
        return [':D.RBV']

    @m1_pos_y2.setter
    def m1_pos_y2(self, value):
        """Set mirror M1 linear position y2 for Rx, Rz and Ty [mm]."""
        self[':D.RBV'] = value

    @property
    def m1_pos_y3(self):
        """Return mirror M1 linear position y3 for Rx, Rz and Ty [mm]."""
        return [':E.RBV']

    @m1_pos_y3.setter
    def m1_pos_y3(self, value):
        """Set mirror M1 linear position y3 for Rx, Rz and Ty [mm]."""
        self[':E.RBV'] = value
