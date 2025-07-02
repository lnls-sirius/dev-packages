"""Mirror Control."""

import inspect as _inspect
import time as _time

from ..device import Device as _Device


class _PVs:
    # MIRROR MOTORS
    # --- ROTY ---
    ROTY_SP = None
    ROTY_RB = None
    ROTY_MON = None
    ROTY_STOP = None

    # --- Tx ---
    TX_SP = None
    TX_RB = None
    TX_MON = None
    TX_STOP = None

    # --- Y1 ---
    Y1_SP = None
    Y1_RB = None
    Y1_MON = None
    Y1_STOP = None

    # --- Y2 ---
    Y2_SP = None
    Y2_RB = None
    Y2_MON = None
    Y2_STOP = None

    # --- Y3 ---
    Y3_SP = None
    Y3_RB = None
    Y3_MON = None
    Y3_STOP = None

    # MIRROR SENSORS
    # --- PHOTOCOLLECTOR ---
    PHOTOCOLLECTOR = None

    # --- TEMPERATURES ---
    TEMP_SP = None
    TEMP_RB = None
    TEMP0_MON = None
    TEMP1_MON = None
    TEMP2_MON = None
    TEMP3_MON = None
    TEMP4_MON = None


class Mirror(_Device):
    """Mirror device.

    * M1 online autodesk drawing:
    https://drive.autodesk.com/de29ccb7d/shares/SH9285eQTcf875d3c5396deb53e725438482
    """

    class DEVICES:
        """Devices names."""

        MIRROR1 = "CAX:A"

        ALL = (MIRROR1,)

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]

    # --- PVS ---
    PVS = _PVs()

    # MIRROR CONTROL
    PVS.ROTY_SP = "PP01:A.VAL"
    PVS.ROTY_RB = "PP01:A.VAL"  # That doesn't have a RB PV
    PVS.ROTY_MON = "PP01:A.RBV"  # RBV is not the pv of readback
    PVS.ROTY_STOP = "PP01:A.STOP"

    PVS.TX_SP = "PP01:B.VAL"
    PVS.TX_RB = "PP01:B.VAL"  # That doesn't have a RB PV
    PVS.TX_MON = "PP01:B.RBV"  # RBV is not the pv of readback
    PVS.TX_STOP = "PP01:B.STOP"

    PVS.Y1_SP = "PP01:C.VAL"
    PVS.Y1_RB = "PP01:C.VAL"  # That doesn't have a RB PV
    PVS.Y1_MON = "PP01:C.RBV"  # RBV is not the pv of readback
    PVS.Y1_STOP = "PP01:C.STOP"

    PVS.Y2_SP = "PP01:D.VAL"
    PVS.Y2_RB = "PP01:D.VAL"  # That doesn't have a RB PV
    PVS.Y2_MON = "PP01:D.RBV"  # RBV is not the pv of readback
    PVS.Y2_STOP = "PP01:D.STOP"

    PVS.Y3_SP = "PP01:E.VAL"
    PVS.Y3_RB = "PP01:E.VAL"  # That doesn't have a RB PV
    PVS.Y3_MON = "PP01:E.RBV"  # RBV is not the pv of readback
    PVS.Y3_STOP = "PP01:E.STOP"

    # SENSORS
    PVS.PHOTOCOLLECTOR = "RIO01:9215A:ai0"
    PVS.TEMP0_MON = "RIO01:9226B:temp0"
    PVS.TEMP1_MON = "RIO01:9226B:temp1"
    PVS.TEMP2_MON = "RIO01:9226B:temp2"
    PVS.TEMP3_MON = "RIO01:9226B:temp3"
    PVS.TEMP4_MON = "RIO01:9226B:temp4"
    PVS.TEMP_SP = "RIO01:M1_CtrltempSp"
    PVS.TEMP_RB = "RIO01:M1_CtrltempSp"  # That doesn't have a RB PV

    PROPERTIES_DEFAULT = tuple(
        set(
            value
            for key, value in _inspect.getmembers(PVS)
            if not key.startswith("_") and value is not None
        )
    )

    def __init__(self, devname=None, props2init="all", **kwargs):
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
        return self[self.PVS.ROTY_MON]

    @property
    def tx_pos(self):
        """Return the linear actuator pos related to Tx translation [mm].

        This linear actuator translates directly to the horizontal
        transverse position of the mirror.
        """
        return self[self.PVS.TX_MON]

    @property
    def y1_pos(self):
        """Return the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in oposite horizontal ends.
        """
        return self[self.PVS.Y1_MON]

    @property
    def y2_pos(self):
        """Return the second linear vertical actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self[self.PVS.Y2_MON]

    @property
    def y3_pos(self):
        """Return the third linear actuator pos Y2 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        return self[self.PVS.Y3_MON]

    @property
    def photocurrent_signal(self):
        """Return induced voltage in the mirror photocollector [V]."""
        return self[self.PVS.PHOTOCOLLECTOR]

    @property
    def temperature_0(self):
        """Return M1 temperature sensor 0 [°C]."""
        return self[self.PVS.TEMP0_MON]

    @property
    def temperature_1(self):
        """Return M1 temperature sensor 1 [°C]."""
        return self[self.PVS.TEMP1_MON]

    @property
    def temperature_2(self):
        """Return M1 temperature sensor 2 [°C]."""
        return self[self.PVS.TEMP2_MON]

    @property
    def temperature_3(self):
        """Return M1 temperature sensor 3 [°C]."""
        return self[self.PVS.TEMP3_MON]

    @property
    def temperature_4(self):
        """Return M1 temperature sensor 4 [°C]."""
        return self[self.PVS.TEMP4_MON]

    @property
    def temperature_ref(self):
        """Return M1 temperature reference setpoint [°C]."""
        return self[self.PVS.TEMP_RB]

    @roty_pos.setter
    def roty_pos(self, value):
        """Set the linear actuator pos related to RotY rotation [mm].

        RotY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        self[self.PVS.ROTY_SP] = value

    @tx_pos.setter
    def tx_pos(self, value):
        """Set the linear actuator pos related to Tx translation [mm].

        This linear actuator is directly related to the horizontal
        transverse position of the mirror.
        """
        self[self.PVS.TX_SP] = value

    @y1_pos.setter
    def y1_pos(self, value):
        """Set the first linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PVS.Y1_SP] = value

    @y2_pos.setter
    def y2_pos(self, value):
        """Set the second linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PVS.Y2_SP] = value

    @temperature_ref.setter
    def temperature_ref(self, value):
        """Set M1 temperature reference [°C]."""
        self[self.PVS.TEMP_SP] = value

    @y3_pos.setter
    def y3_pos(self, value):
        """Set the third linear vertical actuator pos Y1 [mm].

        Rotations RotX, RotZ and translation Ty are implemented as combinations
        of three vertical independent actuators. Y1 actuator is located in one
        longitudinal side of the mirror base whereas Y2 amd Y3 are located in
        the other side, in opposite horizontal ends.
        """
        self[self.PVS.Y3_SP] = value

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)

    def cmd_roty_stop(self, timeout=None):
        """Stop linear actuator for RotY rotation."""
        return self._cmd_motor_stop(self.PVS.ROTY_STOP, timeout)

    def cmd_tx_stop(self, timeout=None):
        """Stop linear actuator for Tx translation."""
        return self._cmd_motor_stop(self.PVS.TX_STOP, timeout)

    def cmd_y1_stop(self, timeout=None):
        """Stop linear actuator Y1."""
        return self._cmd_motor_stop(self.PVS.Y1_STOP, timeout)

    def cmd_y2_stop(self, timeout=None):
        """Stop linear actuator Y2."""
        return self._cmd_motor_stop(self.PVS.Y2_STOP, timeout)

    def cmd_y3_stop(self, timeout=None):
        """Stop linear actuator Y3."""
        return self._cmd_motor_stop(self.PVS.Y3_STOP, timeout)
