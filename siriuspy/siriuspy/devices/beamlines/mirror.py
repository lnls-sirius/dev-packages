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


"""From the EPICS Motor Record Homepage
https://bcda.xray.aps.anl.gov/synApps/motor/motorRecord.htm

#Name    Access	Prompt	                Data type	Comment

CNEN	R/W     Enable control          RECCHOICE	(0:"Disable", 1:"Enable")
DMOV	R	    Done moving to value	SHORT	    The "done" flag

HLM     R/W*	User High Limit         DOUBLE
LLM     R/W*	User Low Limit          DOUBLE

MOVN	R	    Motor is moving         SHORT	    Don't confuse with DMOV
RBV     R       User Readback Value     DOUBLE
STOP    R/W*	Stop	                SHORT
VAL     R/W*	User Desired Value      DOUBLE

Obs.:
CNEN corresponds to the Enable/Disable button in the "Servo" field.

"""


class CAXMirror(MirrorBase):
    """CARCARÁ Mirror Device.

    * M1 online autodesk drawing:
    https://drive.autodesk.com/de29ccb7d/shares/
    SH9285eQTcf875d3c5396deb53e725438482.
    """

    class DEVICES:
        """."""
        CAX_FOE = "CAX"
        ALL = (CAX_FOE,)

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        if devname is None:
            devname = self.DEVICES.CAX_FOE
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        super().__init__(devname=devname, props2init=props2init, **kwargs)

        # MOTORS

        # Real actuators for Ry, Tx, Y1, Y2 and Y3

        # X Translation
        self.PVS.TX      = "A:PB01:m1"        # Motor base name
        self.PVS.TX_SP   = "A:PB01:m1.VAL"    # Setpoint value
        self.PVS.TX_MON  = "A:PB01:m1.RBV"    # Readback value
        self.PVS.TX_HILM = "A:PB01:m1.HLM"    # High limit
        self.PVS.TX_LOLM = "A:PB01:m1.LLM"    # Low limit
        self.PVS.TX_ENBL = "A:PB01:m1.CNEN"   # Enable/Disable
        self.PVS.TX_DMVN = "A:PB01:m1.DMOVN"  # Done moving
        self.PVS.TX_MVN  = "A:PB01:m1.MOVN"   # Motor is moving
        self.PVS.TX_STOP = "A:PB01:m1.STOP"   # Stop command

        # Y Rotation
        self.PVS.RY      = "A:PB01:m2"        # Motor base name
        self.PVS.RY_SP   = "A:PB01:m2.VAL"    # Setpoint value
        self.PVS.RY_MON  = "A:PB01:m2.RBV"    # Readback value
        self.PVS.RY_HILM = "A:PB01:m2.HLM"    # High limit
        self.PVS.RY_LOLM = "A:PB01:m2.LLM"    # Low limit
        self.PVS.RY_ENBL = "A:PB01:m2.CNEN"   # Enable/Disable
        self.PVS.RY_DMVN = "A:PB01:m2.DMOVN"  # Done moving
        self.PVS.RY_MVN  = "A:PB01:m2.MOVN"   # Motor is moving
        self.PVS.RY_STOP = "A:PB01:m2.STOP"   # Stop command

        # Called Leveler Z- in the front end.
        self.PVS.Y1      = "A:PB01:m3"        # Motor base name
        self.PVS.Y1_SP   = "A:PB01:m3.VAL"    # Setpoint value
        self.PVS.Y1_MON  = "A:PB01:m3.RBV"    # Readback value
        self.PVS.Y1_HILM = "A:PB01:m3.HLM"    # High limit
        self.PVS.Y1_LOLM = "A:PB01:m3.LLM"    # Low limit
        self.PVS.Y1_ENBL = "A:PB01:m3.CNEN"   # Enable/Disable
        self.PVS.Y1_DMVN = "A:PB01:m3.DMOVN"  # Done moving
        self.PVS.Y1_MVN  = "A:PB01:m3.MOVN"   # Motor is moving
        self.PVS.Y1_STOP = "A:PB01:m3.STOP"   # Stop command

        # Called Leveler X+ in the front end.
        self.PVS.Y2      = "A:PB01:m4"        # Motor base name
        self.PVS.Y2_SP   = "A:PB01:m4.VAL"    # Setpoint value
        self.PVS.Y2_MON  = "A:PB01:m4.RBV"    # Readback value
        self.PVS.Y2_HILM = "A:PB01:m4.HLM"    # High limit
        self.PVS.Y2_LOLM = "A:PB01:m4.LLM"    # Low limit
        self.PVS.Y2_ENBL = "A:PB01:m4.CNEN"   # Enable/Disable
        self.PVS.Y2_DMVN = "A:PB01:m4.DMOVN"  # Done moving
        self.PVS.Y2_MVN  = "A:PB01:m4.MOVN"   # Motor is moving
        self.PVS.Y2_STOP = "A:PB01:m4.STOP"   # Stop command

        # Called Leveler Z+ in the front end.

        self.PVS.Y3      = "A:PB01:m5"        # Motor base name
        self.PVS.Y3_SP   = "A:PB01:m5.VAL"    # Setpoint value
        self.PVS.Y3_MON  = "A:PB01:m5.RBV"    # Readback value
        self.PVS.Y3_HILM = "A:PB01:m5.HLM"    # High limit
        self.PVS.Y3_LOLM = "A:PB01:m5.LLM"    # Low limit
        self.PVS.Y3_ENBL = "A:PB01:m5.CNEN"   # Enable/Disable
        self.PVS.Y3_DMVN = "A:PB01:m5.DMOVN"  # Done moving
        self.PVS.Y3_MVN  = "A:PB01:m5.MOVN"   # Motor is moving
        self.PVS.Y3_STOP = "A:PB01:m5.STOP"   # Stop command

        # Kinematic actuators for Rx, Ry, Rz and Ty

        # X rotation
        self.PVS.CS_RX      = "A:PB01:CS1:m1"        # Motor base name
        self.PVS.CS_RX_SP   = "A:PB01:CS1:m1.VAL"    # Setpoint value
        self.PVS.CS_RX_MON  = "A:PB01:CS1:m1.RBV"    # Readback value
        self.PVS.CS_RX_HILM = "A:PB01:CS1:m1.HLM"    # High limit
        self.PVS.CS_RX_LOLM = "A:PB01:CS1:m1.LLM"    # Low limit
        self.PVS.CS_RX_ENBL = "A:PB01:CS1:m1.CNEN"   # Enable/Disable
        self.PVS.CS_RX_DMVN = "A:PB01:CS1:m1.DMOVN"  # Done moving
        self.PVS.CS_RX_MVN  = "A:PB01:CS1:m1.MOVN"   # Motor is moving
        self.PVS.CS_RX_STOP = "A:PB01:CS1:m1.STOP"   # Stop command

        # Y rotation
        self.PVS.CS_RY      = "A:PB01:CS1:m2"        # Motor base name
        self.PVS.CS_RY_SP   = "A:PB01:CS1:m2.VAL"    # Setpoint value
        self.PVS.CS_RY_MON  = "A:PB01:CS1:m2.RBV"    # Readback value
        self.PVS.CS_RY_HILM = "A:PB01:CS1:m2.HLM"    # High limit
        self.PVS.CS_RY_LOLM = "A:PB01:CS1:m2.LLM"    # Low limit
        self.PVS.CS_RY_ENBL = "A:PB01:CS1:m2.CNEN"   # Enable/Disable
        self.PVS.CS_RY_DMVN = "A:PB01:CS1:m2.DMOVN"  # Done moving
        self.PVS.CS_RY_MVN  = "A:PB01:CS1:m2.MOVN"   # Motor is moving
        self.PVS.CS_RY_STOP = "A:PB01:CS1:m2.STOP"   # Stop command

        # Z rotation
        self.PVS.CS_RZ      = "A:PB01:CS1:m3"        # Motor base name
        self.PVS.CS_RZ_SP   = "A:PB01:CS1:m3.VAL"    # Setpoint value
        self.PVS.CS_RZ_MON  = "A:PB01:CS1:m3.RBV"    # Readback value
        self.PVS.CS_RZ_HILM = "A:PB01:CS1:m3.HLM"    # High limit
        self.PVS.CS_RZ_LOLM = "A:PB01:CS1:m3.LLM"    # Low limit
        self.PVS.CS_RZ_ENBL = "A:PB01:CS1:m3.CNEN"   # Enable/Disable
        self.PVS.CS_RZ_DMVN = "A:PB01:CS1:m3.DMOVN"  # Done moving
        self.PVS.CS_RZ_MVN  = "A:PB01:CS1:m3.MOVN"   # Motor is moving
        self.PVS.CS_RZ_STOP = "A:PB01:CS1:m3.STOP"   # Stop command

        # X translation
        self.PVS.CS_TX      = "A:PB01:CS1:m7"        # Motor base name
        self.PVS.CS_TX_SP   = "A:PB01:CS1:m7.VAL"    # Setpoint value
        self.PVS.CS_TX_MON  = "A:PB01:CS1:m7.RBV"    # Readback value
        self.PVS.CS_TX_HILM = "A:PB01:CS1:m7.HLM"    # High limit
        self.PVS.CS_TX_LOLM = "A:PB01:CS1:m7.LLM"    # Low limit
        self.PVS.CS_TX_ENBL = "A:PB01:CS1:m7.CNEN"   # Enable/Disable
        self.PVS.CS_TX_DMVN = "A:PB01:CS1:m7.DMOVN"  # Done moving
        self.PVS.CS_TX_MVN  = "A:PB01:CS1:m7.MOVN"   # Motor is moving
        self.PVS.CS_TX_STOP = "A:PB01:CS1:m7.STOP"   # Stop command

        # Y translation
        self.PVS.CS_TY      = "A:PB01:CS1:m8"        # Motor base name
        self.PVS.CS_TY_SP   = "A:PB01:CS1:m8.VAL"    # Setpoint value
        self.PVS.CS_TY_MON  = "A:PB01:CS1:m8.RBV"    # Readback value
        self.PVS.CS_TY_HILM = "A:PB01:CS1:m8.HLM"    # High limit
        self.PVS.CS_TY_LOLM = "A:PB01:CS1:m8.LLM"    # Low limit
        self.PVS.CS_TY_ENBL = "A:PB01:CS1:m8.CNEN"   # Enable/Disable
        self.PVS.CS_TY_DMVN = "A:PB01:CS1:m8.DMOVN"  # Done moving
        self.PVS.CS_TY_MVN  = "A:PB01:CS1:m8.MOVN"   # Motor is moving
        self.PVS.CS_TY_STOP = "A:PB01:CS1:m8.STOP"   # Stop command

        # SENSORS
        self.PVS.PHOTOCOLLECTOR = "A:RIO01:9215A:ai0"
        self.PVS.TEMP0_MON = "A:RIO01:9226B:temp0"
        self.PVS.TEMP1_MON = "A:RIO01:9226B:temp1"
        self.PVS.TEMP2_MON = "A:RIO01:9226B:temp2"
        self.PVS.TEMP3_MON = "A:RIO01:9226B:temp3"
        self.PVS.TEMP4_MON = "A:RIO01:9226B:temp4"
        self.PVS.TEMP_SP = "A:RIO01:M1_CtrltempSp"
        self.PVS.TEMP_RB = "A:RIO01:M1_CtrltempSp"

        # FLOWMETERS
        self.PVS.FLOWMETER1_MON = "F:EPS01:MR1FIT1"
        self.PVS.FLOWMETER2_MON = "F:EPS01:MR1FIT2"

        self.PROPERTIES_DEFAULT = tuple(
            set(value for key, value in vars(self.PVS).items())
        )
