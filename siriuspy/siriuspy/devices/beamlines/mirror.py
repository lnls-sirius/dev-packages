"""Mirror Control."""

import inspect as _inspect
import time as _time
from types import SimpleNamespace as _SimpleNamespace

from ..device import Device as _Device


class _PVNames(_SimpleNamespace):
    def __getattr__(self, name):
        """."""
        return None


class MirrorBase(_Device):
    """Base Mirror device."""

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]

    # --- PVS ---
    PVS = _PVNames()

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        super().__init__(devname, props2init=props2init, **kwargs)

    @property
    def ry_pos(self):
        """Return the linear actuator pos related to RY rotation [mm].

        RY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        return self[self.PVS.RY_MON]

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

    @property
    def flowmeter_1(self):
        """Return M1 flowmeter 1 value [mL/min]."""
        return self[self.PVS.FLOWMETER1_MON]

    @property
    def flowmeter_2(self):
        """Return M1 flowmeter 2 value [mL/min]."""
        return self[self.PVS.FLOWMETER2_MON]

    @ry_pos.setter
    def ry_pos(self, value):
        """Set the linear actuator pos related to RY rotation [mm].

        RY is performed by a linear actuator in one of
        longitudinal ends of the mirror. The mirror is pivoted
        at its longitudinal center and the linear actuator induces
        a rotation around the Y axis.
        """
        self[self.PVS.RY_SP] = value

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

    def cmd_ry_stop(self, timeout=None):
        """Stop linear actuator for RY rotation."""
        return self._cmd_motor_stop(self.PVS.RY_STOP, timeout)

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


class CAXMirror(MirrorBase):
    """CARCARÁ Mirror Device.

    * M1 online autodesk drawing:
    https://drive.autodesk.com/de29ccb7d/shares/SH9285eQTcf875d3c5396deb53e725438482.
    """

    class DEVICES:
        """."""

        CAX_FOE = "CAX"

        ALL = (CAX_FOE,)

    def __init__(self, devname, props2init="all", **kwargs):
        """Init."""
        if devname is None:
            devname = self.DEVICES.CAX_FOE
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        super().__init__(devname=devname, props2init=props2init, **kwargs)
        # MOTORS
        self.PVS.RY_SP = "A:PP01:A.VAL"
        self.PVS.RY_RB = "A:PP01:A.VAL"  # That doesn't have a RB PV
        self.PVS.RY_MON = "A:PP01:A.RBV"  # RBV is not the pv of readback
        self.PVS.RY_STOP = "A:PP01:A.STOP"

        self.PVS.TX_SP = "A:PP01:B.VAL"
        self.PVS.TX_RB = "A:PP01:B.VAL"  # That doesn't have a RB PV
        self.PVS.TX_MON = "A:PP01:B.RBV"  # RBV is not the pv of readback
        self.PVS.TX_STOP = "A:PP01:B.STOP"

        self.PVS.Y1_SP = "A:PP01:C.VAL"
        self.PVS.Y1_RB = "A:PP01:C.VAL"  # That doesn't have a RB PV
        self.PVS.Y1_MON = "A:PP01:C.RBV"  # RBV is not the pv of readback
        self.PVS.Y1_STOP = "A:PP01:C.STOP"

        self.PVS.Y2_SP = "A:PP01:D.VAL"
        self.PVS.Y2_RB = "A:PP01:D.VAL"  # That doesn't have a RB PV
        self.PVS.Y2_MON = "A:PP01:D.RBV"  # RBV is not the pv of readback
        self.PVS.Y2_STOP = "A:PP01:D.STOP"

        self.PVS.Y3_SP = "A:PP01:E.VAL"
        self.PVS.Y3_RB = "A:PP01:E.VAL"  # That doesn't have a RB PV
        self.PVS.Y3_MON = "A:PP01:E.RBV"  # RBV is not the pv of readback
        self.PVS.Y3_STOP = "A:PP01:E.STOP"

        # SENSORS
        self.PVS.PHOTOCOLLECTOR = "A:RIO01:9215A:ai0"
        self.PVS.TEMP0_MON = "A:RIO01:9226B:temp0"
        self.PVS.TEMP1_MON = "A:RIO01:9226B:temp1"
        self.PVS.TEMP2_MON = "A:RIO01:9226B:temp2"
        self.PVS.TEMP3_MON = "A:RIO01:9226B:temp3"
        self.PVS.TEMP4_MON = "A:RIO01:9226B:temp4"
        self.PVS.TEMP_SP = "A:RIO01:M1_CtrltempSp"
        self.PVS.TEMP_RB = "A:RIO01:M1_CtrltempSp"  # That doesn't have a RB PV

        # FLOWMETERS
        self.PVS.FLOWMETER1_MON = "F:EPS01:MR1FIT1"
        self.PVS.FLOWMETER2_MON = "F:EPS01:MR1FIT2"

        self.PROPERTIES_DEFAULT = tuple(
            set(value for key, value in vars(self.PVS).items())
        )
