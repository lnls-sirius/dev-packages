"""Beamline devices."""

from .device import Device as _Device


class CAXCtrl(_Device):
    """Carcara beamline control."""

    PROPERTIES_DEFAULT = (
        ':A:PP01:A', ':A:PP01:A.RBV',
        ':A:PP01:B', ':A:PP01:B.RBV',
        ':A:PP01:C', ':A:PP01:C.RBV',
        ':A:PP01:D', ':A:PP01:D.RBV',
        ':A:PP01:E', ':A:PP01:E.RBV',
        )

    def __init__(self, devname=None, props2init='all', **kwargs):
        """Init."""
        devname = 'CAX' if devname is None else devname
        super().__init__(devname, props2init=props2init, **kwargs)

    @property
    def mirror_m1_pos_ry(self):
        """Return mirror M1 linear position axis for Ry [mm]."""
        return [':A:PP01::A.RBV']

    @mirror_m1_pos_ry.setter
    def mirror_m1_pos_ry(self, value):
        """Set mirror M1 linear position axis for Ry [mm]."""
        self[':A:PP01:A'] = value

    @property
    def mirror_m1_pos_tx(self):
        """Return mirror M1 linear position axis for Tx [mm]."""
        return [':A:PP01:B.RBV']

    @mirror_m1_pos_tx.setter
    def mirror_m1_pos_tx(self, value):
        """Set mirror M1 linear position axis for Tx [mm]."""
        self[':A:PP01:B'] = value

    @property
    def mirror_m1_pos_y1(self):
        """Return mirror M1 linear position y1 for Rx, Rz and Ty [mm]."""
        return [':A:PP01:C.RBV']

    @mirror_m1_pos_y1.setter
    def mirror_m1_pos_y1(self, value):
        """Set mirror M1 linear position y1 for Rx, Rz and Ty [mm]."""
        self[':A:PP01:C'] = value

    @property
    def mirror_m1_pos_y2(self):
        """Return mirror M1 linear position y2 for Rx, Rz and Ty [mm]."""
        return [':A:PP01:D.RBV']

    @mirror_m1_pos_y2.setter
    def mirror_m1_pos_y2(self, value):
        """Set mirror M1 linear position y2 for Rx, Rz and Ty [mm]."""
        self[':A:PP01:D'] = value

    @property
    def mirror_m1_pos_y3(self):
        """Return mirror M1 linear position y3 for Rx, Rz and Ty [mm]."""
        return [':A:PP01:E.RBV']

    @mirror_m1_pos_y3.setter
    def mirror_m1_pos_y3(self, value):
        """Set mirror M1 linear position y3 for Rx, Rz and Ty [mm]."""
        self[':A:PP01:E'] = value
