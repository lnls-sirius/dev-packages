"""Beamline devices."""

import inspect as _inspect

from .device import Device as _Device

class _ParamPVs:
    
    # SLITS
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

    # MIRROR
    # --- ROTY ---
    ROTY_PARAM_SP = None
    ROTY_PARAM_RB = None
    ROTY_PARAM_MON = None
    ROTY_PARAM_STOP = None

    # --- Tx ---
    TX_PARAM_SP = None
    TX_PARAM_RB = None
    TX_PARAM_MON = None
    TX_PARAM_STOP = None

    # --- Y1 ---
    Y1_PARAM_SP = None
    Y1_PARAM_RB = None
    Y1_PARAM_MON = None
    Y1_PARAM_STOP = None

    # --- Y2 ---
    Y2_PARAM_SP = None
    Y2_PARAM_RB = None
    Y2_PARAM_MON = None
    Y2_PARAM_STOP = None

    # --- Y3 ---
    Y3_PARAM_SP = None
    Y3_PARAM_RB = None
    Y3_PARAM_MON = None
    Y3_PARAM_STOP = None


class Slit(_Device):
    """Slit device."""

    class DEVICES:
        """Devices names."""

        SLIT1 = "CAX:A:PP02" # WBS1
        SLIT2 = "CAX:B:PP01" # WBS2

        ALL = (
            SLIT1, SLIT2,
        )

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]

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
    
    @property
    def top_pos(self):
        """Return slit top position [mm]."""
        return self[self.PARAM_PVS.TOP_PARAM_MON]

    @top_pos.setter
    def top_pos(self, value):
        """Set slit top position [mm]."""
        self[self.PARAM_PVS.TOP_PARAM_SP] = value

    @property
    def bottom_pos(self):
        """Return slit bottom position [mm]."""
        return self[self.PARAM_PVS.BOTTOM_PARAM_MON]

    @bottom_pos.setter
    def bottom_pos(self, value):
        """Set slit bottom position [mm]."""
        self[self.PARAM_PVS.BOTTOM_PARAM_SP] = value
    
    @property
    def left_pos(self):
        """Return slit left position [mm]."""
        return self[self.PARAM_PVS.LEFT_PARAM_MON]

    @left_pos.setter
    def left_pos(self, value):
        """Set slit left position [mm]."""
        self[self.PARAM_PVS.LEFT_PARAM_SP] = value
    
    @property
    def right_pos(self):
        """Return slit right position [mm]."""
        return self[self.PARAM_PVS.RIGHT_PARAM_MON]

    @right_pos.setter
    def right_pos(self, value):
        """Set slit right position [mm]."""
        self[self.PARAM_PVS.RIGHT_PARAM_SP] = value

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)
    
    def cmd_top_stop(self, timeout=None):
        """Stop Slit top motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.TOP_PARAM_STOP, timeout)

    def cmd_bottom_stop(self, timeout=None):
        """Stop Slit bottom motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.BOTTOM_PARAM_STOP, timeout)

    def cmd_left_stop(self, timeout=None):
        """Stop Slit left motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.LEFT_PARAM_STOP, timeout)

    def cmd_right_stop(self, timeout=None):
        """Stop Slit right motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.RIGHT_PARAM_STOP, timeout)


class Mirror(_Device):
    """Mirror device.
    
    * M1 online autodesk drawing:
    https://drive.autodesk.com/de29ccb7d/shares/SH9285eQTcf875d3c5396deb53e725438482
    """

    class DEVICES:
        """Devices names."""

        MIRROR1 = "CAX:A:PP01"

        ALL = (
            MIRROR1,
        )
    
    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]

    # --- PARAM_PVS ---
    PARAM_PVS = _ParamPVs()

    # --- mirror motors suffix initialization --- 
    PARAM_PVS.ROTY_PARAM_SP = "A.VAL"
    PARAM_PVS.ROTY_PARAM_RB = "A.VAL" # That doesn't have a RB PV
    PARAM_PVS.ROTY_PARAM_MON = "A.RBV" # RBV is not the pv of readback
    PARAM_PVS.ROTY_PARAM_STOP = "A.STOP"

    PARAM_PVS.TX_PARAM_SP = "B.VAL"
    PARAM_PVS.TX_PARAM_RB = "B.VAL" # That doesn't have a RB PV
    PARAM_PVS.TX_PARAM_MON = "B.RBV" # RBV is not the pv of readback
    PARAM_PVS.TX_PARAM_STOP = "B.STOP"

    PARAM_PVS.Y1_PARAM_SP = "C.VAL"
    PARAM_PVS.Y1_PARAM_RB = "C.VAL" # That doesn't have a RB PV
    PARAM_PVS.Y1_PARAM_MON = "C.RBV" # RBV is not the pv of readback
    PARAM_PVS.Y1_PARAM_STOP = "C.STOP"

    PARAM_PVS.Y2_PARAM_SP = "D.VAL"
    PARAM_PVS.Y2_PARAM_RB = "D.VAL" # That doesn't have a RB PV
    PARAM_PVS.Y2_PARAM_MON = "D.RBV" # RBV is not the pv of readback
    PARAM_PVS.Y2_PARAM_STOP = "D.STOP"

    PARAM_PVS.Y3_PARAM_SP = "E.VAL"
    PARAM_PVS.Y3_PARAM_RB = "E.VAL" # That doesn't have a RB PV
    PARAM_PVS.Y3_PARAM_MON = "E.RBV" # RBV is not the pv of readback
    PARAM_PVS.Y3_PARAM_STOP = "E.STOP"

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

    @property
    def roty_pos(self):
        """Return the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        return self[self.PARAM_PVS.ROTY_PARAM_MON]

    @roty_pos.setter
    def roty_pos(self, value):
        """Set the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        self[self.PARAM_PVS.ROTY_PARAM_SP] = value
    
    @property
    def tx_pos(self):
        """Return the linear actuator pos related to Tx translation [mm].

        This linear actuator translates directly to the horizontal
        transverse position of the mirror.
        """
        return self[self.PARAM_PVS.TX_PARAM_MON]

    @tx_pos.setter
    def tx_pos(self, value):
        """Set the linear actuator pos related to Tx translation [mm].

        This linear actuator is directly related to the horizontal
        transverse position of the mirror.
        """
        self[self.PARAM_PVS.TX_PARAM_SP] = value
    
    @property
    def y1_pos(self):
        """Return the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in oposite horizontal ends.
        """
        return self[self.PARAM_PVS.Y1_PARAM_MON]

    @y1_pos.setter
    def y1_pos(self, value):
        """Set the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PARAM_PVS.Y1_PARAM_SP] = value

    @property
    def y2_pos(self):
        """Return the second linear vertical actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self[self.PARAM_PVS.Y2_PARAM_MON]

    @y2_pos.setter
    def y2_pos(self, value):
        """Set the second linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PARAM_PVS.Y2_PARAM_SP] = value

    @property
    def y3_pos(self):
        """Return the third linear actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self[self.PARAM_PVS.Y3_PARAM_MON]

    @y3_pos.setter
    def y3_pos(self, value):
        """Set the third linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PARAM_PVS.Y3_PARAM_SP] = value
    
    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)

    def cmd_roty_stop(self, timeout=None):
        """Stop linear actuator for RotY rotation."""
        return self._cmd_motor_stop(self.PARAM_PVS.ROTY_PARAM_STOP, timeout)

    def cmd_tx_stop(self, timeout=None):
        """Stop linear actuator for Tx translation."""
        return self._cmd_motor_stop(self.PARAM_PVS.TX_PARAM_STOP, timeout)

    def cmd_y1_stop(self, timeout=None):
        """Stop linear actuator Y1."""
        return self._cmd_motor_stop(self.PARAM_PVS.Y1_PARAM_STOP, timeout)

    def cmd_y2_stop(self, timeout=None):
        """Stop linear actuator Y2."""
        return self._cmd_motor_stop(self.PARAM_PVS.Y2_PARAM_STOP, timeout)

    def cmd_y3_stop(self, timeout=None):
        """Stop linear actuator Y3."""
        return self._cmd_motor_stop(self.PARAM_PVS.Y3_PARAM_STOP, timeout)


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
