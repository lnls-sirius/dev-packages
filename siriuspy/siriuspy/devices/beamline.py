"""Beamline devices."""

from .device import Device as _Device


class CAXCtrl(_Device):
    """Carcara beamline control.

    * Beamline commissionning:
    https://cnpemcamp.sharepoint.com/:p:/s/lnls/groups/opt/EZB-ePPBFvRPqi5IM1fjTsoB7uwtUhUrw3inlGnRfDm1KA?e=4lP3Bi&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIxNDE1LzI0MDYyNzI0ODE0In0%3D

    * DVF:
    https://cnpemcamp.sharepoint.com/:p:/s/lnls/groups/opt/EfXWP0gm-URPt1mzEZEWxbABzJxfJg3kt86jOJrV3KQoMg?e=eaT4T1&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIxNDE1LzI0MDYyNzI0ODE0In0%3D

    * M1 online autodesk drawing:
    https://drive.autodesk.com/de29ccb7d/shares/SH9285eQTcf875d3c5396deb53e725438482
    """

    PROPERTIES_DEFAULT = (
        ':A:PP01:A', ':A:PP01:A.RBV',
        ':A:PP01:B', ':A:PP01:B.RBV',
        ':A:PP01:C', ':A:PP01:C.RBV',
        ':A:PP01:D', ':A:PP01:D.RBV',
        ':A:PP01:E', ':A:PP01:E.RBV',
        ':B:PP01:E', ':B:PP01:E.RBV',
        )

    def __init__(self, devname=None, props2init='all', **kwargs):
        """Init."""
        devname = 'CAX' if devname is None else devname
        super().__init__(devname, props2init=props2init, **kwargs)

    @property
    def mirror_m1_roty_pos(self):
        """Return the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        return [':A:PP01:A.RBV']

    @mirror_m1_roty_pos.setter
    def mirror_m1_roty(self, value):
        """Set the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        self[':A:PP01:A'] = value

    @property
    def mirror_m1_tx_pos(self):
        """Return the linear actuator pos related to Tx translation [mm].

        This linear actuator translates directly to the horizontal
        transverse position of the mirror.
        """
        return [':A:PP01:B.RBV']

    @mirror_m1_tx_pos.setter
    def mirror_m1_tx_pos(self, value):
        """Set the linear actuator pos related to Tx translation [mm].

        This linear actuator is directly related to the horizontal
        transverse position of the mirror.
        """
        self[':A:PP01:B'] = value

    @property
    def mirror_m1_y1_pos(self):
        """Return the first linear actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in oposite horizontal ends.
        """
        return [':A:PP01:C.RBV']

    @mirror_m1_y1_pos.setter
    def mirror_m1_y1_pos(self, value):
        """Set the first linear actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[':A:PP01:C'] = value

    @property
    def mirror_m1_y2_pos(self):
        """Return the second linear actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return [':A:PP01:D.RBV']

    @mirror_m1_y2_pos.setter
    def mirror_m1_y2_pos(self, value):
        """Set the second linear actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[':A:PP01:D'] = value

    @property
    def mirror_m1_y3_pos(self):
        """Return the third linear actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return [':A:PP01:E.RBV']

    @mirror_m1_y3_pos.setter
    def mirror_m1_y3_pos(self, value):
        """Set the third linear actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[':A:PP01:E'] = value

    @property
    def dvf2_z_pos(self):
        """Return DVF2 base motor longitudinal position [mm]."""
        return [':B:PP01:E.RBV']

    @dvf2_z_pos.setter
    def dvf2_z_pos(self, value):
        """Set DVF2 base motor longitudinal position [mm]."""
        self[':B:PP01:E'] = value
