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

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]

    PROPERTIES_DEFAULT = (
        # mirror controls
        'A:PP01:A', 'A:PP01:A.RBV', 'A:PP01:A.STOP',  # RotY
        'A:PP01:B', 'A:PP01:B.RBV', 'A:PP01:B.STOP',  # Tx
        'A:PP01:C', 'A:PP01:C.RBV', 'A:PP01:C.STOP',  # Y1
        'A:PP01:D', 'A:PP01:D.RBV', 'A:PP01:D.STOP',  # Y2
        'A:PP01:E', 'A:PP01:E.RBV', 'A:PP01:E.STOP',  # Y3
        # mirror photocollector
        'A:RIO01:9215A:ai0',
        # mirror temperatures
        'A:RIO01:M1_CtrltempSp',
        'A:RIO01:9226B:temp0', 'A:RIO01:9226B:temp1',
        'A:RIO01:9226B:temp2', 'A:RIO01:9226B:temp3',
        'A:RIO01:9226B:temp4',
        # dvf motors
        'B:PP01:E', 'B:PP01:E.RBV', 'B:PP01:E.STOP',  # z pos
        'B:PP01:F', 'B:PP01:F.RBV', 'B:PP01:F.STOP',  # lens
        )

    def __init__(self, devname=None, props2init='all', **kwargs):
        """Init."""
        devname = 'CAX' if devname is None else devname
        super().__init__(devname, props2init=props2init, **kwargs)

    @property
    def m1_roty_pos(self):
        """Return the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        return self['A:PP01:A.RBV']

    @m1_roty_pos.setter
    def m1_roty_pos(self, value):
        """Set the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        self['A:PP01:A'] = value

    @property
    def m1_tx_pos(self):
        """Return the linear actuator pos related to Tx translation [mm].

        This linear actuator translates directly to the horizontal
        transverse position of the mirror.
        """
        return self['A:PP01:B.RBV']

    @m1_tx_pos.setter
    def m1_tx_pos(self, value):
        """Set the linear actuator pos related to Tx translation [mm].

        This linear actuator is directly related to the horizontal
        transverse position of the mirror.
        """
        self['A:PP01:B'] = value

    @property
    def m1_y1_pos(self):
        """Return the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in oposite horizontal ends.
        """
        return self['A:PP01:C.RBV']

    @m1_y1_pos.setter
    def m1_y1_pos(self, value):
        """Set the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self['A:PP01:C'] = value

    @property
    def m1_y2_pos(self):
        """Return the second linear vertical actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self['A:PP01:D.RBV']

    @m1_y2_pos.setter
    def m1_y2_pos(self, value):
        """Set the second linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self['A:PP01:D'] = value

    @property
    def m1_y3_pos(self):
        """Return the third linear actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self['A:PP01:E.RBV']

    @m1_y3_pos.setter
    def m1_y3_pos(self, value):
        """Set the third linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self['A:PP01:E'] = value

    @property
    def m1_photocurrent_signal(self):
        """Return induced voltage in the mirror photocollector [V]."""
        return self['A:RIO01:9215A:ai0']

    @property
    def dvf2_z_pos(self):
        """Return DVF2 base motor longitudinal position [mm]."""
        return self['B:PP01:E.RBV']

    @dvf2_z_pos.setter
    def dvf2_z_pos(self, value):
        """Set DVF2 base motor longitudinal position [mm]."""
        self['B:PP01:E'] = value

    @property
    def dvf2_lens_pos(self):
        """Return DVF2 lens motor position [mm]."""
        return self['B:PP01:F.RBV']

    @dvf2_lens_pos.setter
    def dvf2_lens_pos(self, value):
        """Set DVF2 lens motor position [mm]."""
        self['B:PP01:F'] = value

    @property
    def m1_temperature_ref(self):
        """Return M1 temperature reference setpoint [°C]."""
        return self['A:RIO01:M1_CtrltempSp']

    @m1_temperature_ref.setter
    def m1_temperature_ref(self, value):
        """Set M1 temperature reference [°C]."""
        self['A:RIO01:M1_CtrltempSp'] = value

    @property
    def m1_temperature_0(self):
        """Return M1 temperature at cold finger [°C]."""
        return self['A:RIO01:9226B:temp0']

    @property
    def m1_temperature_1(self):
        """Return M1 temperature at braid mirror [°C]."""
        return self['A:RIO01:9226B:temp1']

    @property
    def m1_temperature_2(self):
        """Return M1 temperature at bar braid cold finger [°C]."""
        return self['A:RIO01:9226B:temp2']

    @property
    def m1_temperature_3(self):
        """Return M1 temperature at peltier cold side [°C]."""
        return self['A:RIO01:9226B:temp3']

    @property
    def m1_temperature_4(self):
        """Return M1 temperature at peltier hot side [°C]."""
        return self['A:RIO01:9226B:temp4']

    @property
    def cmd_m1_roty_stop(self, timeout=None):
        """Stop linear actuator for RotY rotation."""
        return self._cmd_motor_stop('A:PP01:A.STOP', timeout)

    def cmd_m1_tx_stop(self, timeout=None):
        """Stop linear actuator for Tx translation."""
        return self._cmd_motor_stop('A:PP01:B.STOP', timeout)

    def cmd_m1_y1_stop(self, timeout=None):
        """Stop linear actuator Y1."""
        return self._cmd_motor_stop('A:PP01:C.STOP', timeout)

    def cmd_m1_y2_stop(self, timeout=None):
        """Stop linear actuator Y2."""
        return self._cmd_motor_stop('A:PP01:D.STOP', timeout)

    def cmd_m1_y3_stop(self, timeout=None):
        """Stop linear actuator Y3."""
        return self._cmd_motor_stop('A:PP01:E.STOP', timeout)

    def cmd_dvf2_z_stop(self, timeout=None):
        """Stop DVF2 base motor."""
        return self._cmd_motor_stop('B:PP01:E.STOP', timeout)

    def cmd_dvf2_lens_stop(self, timeout=None):
        """Stop DVF2 lens motor."""
        return self._cmd_motor_stop('B:PP01:F.STOP', timeout)

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)
