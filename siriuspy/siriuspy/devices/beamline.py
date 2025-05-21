"""Beamline devices."""

import inspect as _inspect

from .device import Device as _Device

class _ParamPVs:
    
    # --- TOP ---
    TOP_PARAM_SP = None
    TOP_PARAM_RB = None
    TOP_PARAM_MON = None
    TOP_PARAM_STOP = None

    # --- BOTTOM ---
    BOTTOM_PARAM_SP = None
    BOTTOM_PARAM_RB = None
    BOTTOM_PARAM_MON = None
    BOTTOM_PARAM_STOP = None

    # --- LEFT ---
    LEFT_PARAM_SP = None
    LEFT_PARAM_RB = None
    LEFT_PARAM_MON = None
    LEFT_PARAM_STOP = None

    # --- RIGHT ---
    RIGHT_PARAM_SP = None
    RIGHT_PARAM_RB = None
    RIGHT_PARAM_MON = None
    RIGHT_PARAM_STOP = None


class Slit(_Device):
    """Slit device."""

    class DEVICES:
        """Devices names."""

        SLIT1 = "CAX:A:PP02" # WBS1
        SLIT2 = "CAX:B:PP01" # WBS2

        ALL = (
            SLIT1, SLIT2,
        )

    # --- PARAM_PVS ---
    PARAM_PVS = _ParamPVs()

    PARAM_PVS.TOP_PARAM_SP = "A.VAL"
    PARAM_PVS.TOP_PARAM_RB = "A.VAL" # That doesn't have a RB PV
    PARAM_PVS.TOP_PARAM_MON = "A.RBV" # RBV is not the pv of readback
    PARAM_PVS.TOP_PARAM_STOP = "A.STOP"

    PARAM_PVS.BOTTOM_PARAM_SP = "B.VAL"
    PARAM_PVS.BOTTOM_PARAM_RB = "B.VAL" # That doesn't have a RB PV
    PARAM_PVS.BOTTOM_PARAM_MON = "B.RBV" # RBV is not the pv of readback
    PARAM_PVS.BOTTOM_PARAM_STOP = "B.STOP"

    PARAM_PVS.LEFT_PARAM_SP = "C.VAL"
    PARAM_PVS.LEFT_PARAM_RB = "C.VAL" # That doesn't have a RB PV
    PARAM_PVS.LEFT_PARAM_MON = "C.RBV" # RBV is not the pv of readback
    PARAM_PVS.LEFT_PARAM_STOP = "C.STOP"

    PARAM_PVS.RIGHT_PARAM_SP = "D.VAL"
    PARAM_PVS.RIGHT_PARAM_RB = "D.VAL" # That doesn't have a RB PV
    PARAM_PVS.RIGHT_PARAM_MON = "D.RBV" # RBV is not the pv of readback
    PARAM_PVS.RIGHT_PARAM_STOP = "D.STOP"

    PROPERTIES_DEFAULT = \
        tuple(set(
            value for key, value in _inspect.getmembers(PARAM_PVS)
            if not key.startswith('_') and value is not None))

    def __init__(self, devname=None, props2init='all', **kwargs):
        """Init."""
        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init, **kwargs)

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
        # slit 1 controls
        'A:PP02:A', 'A:PP02:A.RBV', 'A:PP02:A.STOP',  # Top slit
        'A:PP02:B', 'A:PP02:B.RBV', 'A:PP02:B.STOP',  # Bottom slit
        'A:PP02:C', 'A:PP02:C.RBV', 'A:PP02:C.STOP',  # Left slit
        'A:PP02:D', 'A:PP02:D.RBV', 'A:PP02:D.STOP',  # Right slit
        # slit 2 controls
        'B:PP01:A', 'B:PP01:A.RBV', 'B:PP01:A.STOP',  # Top slit
        'B:PP01:B', 'B:PP01:B.RBV', 'B:PP01:B.STOP',  # Bottom slit
        'B:PP01:C', 'B:PP01:C.RBV', 'B:PP01:C.STOP',  # Left slit
        'B:PP01:D', 'B:PP01:D.RBV', 'B:PP01:D.STOP',  # Right slit
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
    def slit1_top_pos(self):
        """Return slit1 top position [mm]."""
        return self['A:PP02:A.RBV']

    @slit1_top_pos.setter
    def slit1_top_pos(self, value):
        """Set slit1 top position [mm]."""
        self['A:PP02:A'] = value

    @property
    def slit1_bottom_pos(self):
        """Return slit1 bottom position [mm]."""
        return self['A:PP02:B.RBV']

    @slit1_bottom_pos.setter
    def slit1_bottom_pos(self, value):
        """Set slit1 bottom position [mm]."""
        self['A:PP02:B'] = value

    @property
    def slit1_left_pos(self):
        """Return slit1 left position [mm]."""
        return self['A:PP02:C.RBV']

    @slit1_left_pos.setter
    def slit1_left_pos(self, value):
        """Set slit1 left position [mm]."""
        self['A:PP02:C'] = value

    @property
    def slit1_right_pos(self):
        """Return slit1 right position [mm]."""
        return self['A:PP02:D.RBV']

    @slit1_right_pos.setter
    def slit1_right_pos(self, value):
        """Set slit1 right position [mm]."""
        self['A:PP02:D'] = value

    @property
    def slit2_top_pos(self):
        """Return slit2 top position [mm]."""
        return self['B:PP01:A.RBV']

    @slit2_top_pos.setter
    def slit2_top_pos(self, value):
        """Set slit2 top position [mm]."""
        self['B:PP01:A'] = value

    @property
    def slit2_bottom_pos(self):
        """Return slit2 bottom position [mm]."""
        return self['B:PP01:B.RBV']

    @slit2_bottom_pos.setter
    def slit2_bottom_pos(self, value):
        """Set slit2 bottom position [mm]."""
        self['B:PP01:B'] = value

    @property
    def slit2_left_pos(self):
        """Return slit2 left position [mm]."""
        return self['B:PP01:C.RBV']

    @slit2_left_pos.setter
    def slit2_left_pos(self, value):
        """Set slit2 left position [mm]."""
        self['B:PP01:C'] = value

    @property
    def slit2_right_pos(self):
        """Return slit2 right position [mm]."""
        return self['B:PP01:D.RBV']

    @slit2_right_pos.setter
    def slit2_right_pos(self, value):
        """Set slit2 right position [mm]."""
        self['B:PP01:D'] = value

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

    def cmd_slit1_top_stop(self, timeout=None):
        """Stop Slit1 top motor."""
        return self._cmd_motor_stop('A:PP02:A.STOP', timeout)

    def cmd_slit1_bottom_stop(self, timeout=None):
        """Stop Slit1 bottom motor."""
        return self._cmd_motor_stop('A:PP02:B.STOP', timeout)

    def cmd_slit1_left_stop(self, timeout=None):
        """Stop Slit1 left motor."""
        return self._cmd_motor_stop('A:PP02:C.STOP', timeout)

    def cmd_slit1_right_stop(self, timeout=None):
        """Stop Slit1 right motor."""
        return self._cmd_motor_stop('A:PP02:D.STOP', timeout)

    def cmd_slit2_top_stop(self, timeout=None):
        """Stop Slit2 top motor."""
        return self._cmd_motor_stop('B:PP01:A.STOP', timeout)

    def cmd_slit2_bottom_stop(self, timeout=None):
        """Stop Slit2 bottom motor."""
        return self._cmd_motor_stop('B:PP01:B.STOP', timeout)

    def cmd_slit2_left_stop(self, timeout=None):
        """Stop Slit2 left motor."""
        return self._cmd_motor_stop('B:PP01:C.STOP', timeout)

    def cmd_slit2_right_stop(self, timeout=None):
        """Stop Slit2 right motor."""
        return self._cmd_motor_stop('B:PP01:D.STOP', timeout)

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)
