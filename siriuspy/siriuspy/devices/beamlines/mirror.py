"""Mirror Control."""

# import inspect as _inspect

from ..device import Device as _Device
from ..device import _PVAccessor, _PVNames


class MirrorBase(_PVAccessor, _Device):
    """Base Mirror device."""

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]
    _THRESHOLD_POS = 0.01  # [mm]
    _THRESHOLD_ANG = 0.01  # [mrad]

    # --- PVS ---
    PVS = _PVNames()

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        super().__init__(devname, props2init=props2init, **kwargs)

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

    @temperature_ref.setter
    def temperature_ref(self, value):
        """Set M1 temperature reference [°C]."""
        self[self.PVS.TEMP_SP] = value


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
        pvprefix = "A:PB01:"

        # X Translation
        self.PVS.TX      = pvprefix + "m1"        # Motor base name
        self.PVS.TX_SP   = pvprefix + "m1.VAL"    # Setpoint value
        self.PVS.TX_MON  = pvprefix + "m1.RBV"    # Readback value
        self.PVS.TX_HILM = pvprefix + "m1.HLM"    # High limit
        self.PVS.TX_LOLM = pvprefix + "m1.LLM"    # Low limit
        self.PVS.TX_ENBL = pvprefix + "m1.CNEN"   # Enable/Disable
        self.PVS.TX_DMVN = pvprefix + "m1.DMOV"   # Done moving
        self.PVS.TX_MVN  = pvprefix + "m1.MOVN"   # Motor is moving
        self.PVS.TX_STOP = pvprefix + "m1.STOP"   # Stop command
        self.PVS.TX_DESC = pvprefix + "m1.DESC"   # Description

        # Y Rotation
        self.PVS.RY      = pvprefix + "m2"        # Motor base name
        self.PVS.RY_SP   = pvprefix + "m2.VAL"    # Setpoint value
        self.PVS.RY_MON  = pvprefix + "m2.RBV"    # Readback value
        self.PVS.RY_HILM = pvprefix + "m2.HLM"    # High limit
        self.PVS.RY_LOLM = pvprefix + "m2.LLM"    # Low limit
        self.PVS.RY_ENBL = pvprefix + "m2.CNEN"   # Enable/Disable
        self.PVS.RY_DMVN = pvprefix + "m2.DMOV"   # Done moving
        self.PVS.RY_MVN  = pvprefix + "m2.MOVN"   # Motor is moving
        self.PVS.RY_STOP = pvprefix + "m2.STOP"   # Stop command
        self.PVS.RY_DESC = pvprefix + "m2.DESC"   # Description

        # Called Leveler Z- in the front end.
        self.PVS.Y1      = pvprefix + "m3"        # Motor base name
        self.PVS.Y1_SP   = pvprefix + "m3.VAL"    # Setpoint value
        self.PVS.Y1_MON  = pvprefix + "m3.RBV"    # Readback value
        self.PVS.Y1_HILM = pvprefix + "m3.HLM"    # High limit
        self.PVS.Y1_LOLM = pvprefix + "m3.LLM"    # Low limit
        self.PVS.Y1_ENBL = pvprefix + "m3.CNEN"   # Enable/Disable
        self.PVS.Y1_DMVN = pvprefix + "m3.DMOV"   # Done moving
        self.PVS.Y1_MVN  = pvprefix + "m3.MOVN"   # Motor is moving
        self.PVS.Y1_STOP = pvprefix + "m3.STOP"   # Stop command
        self.PVS.Y1_DESC = pvprefix + "m3.DESC"   # Description

        # Called Leveler X+ in the front end.
        self.PVS.Y2      = pvprefix + "m4"        # Motor base name
        self.PVS.Y2_SP   = pvprefix + "m4.VAL"    # Setpoint value
        self.PVS.Y2_MON  = pvprefix + "m4.RBV"    # Readback value
        self.PVS.Y2_HILM = pvprefix + "m4.HLM"    # High limit
        self.PVS.Y2_LOLM = pvprefix + "m4.LLM"    # Low limit
        self.PVS.Y2_ENBL = pvprefix + "m4.CNEN"   # Enable/Disable
        self.PVS.Y2_DMVN = pvprefix + "m4.DMOV"   # Done moving
        self.PVS.Y2_MVN  = pvprefix + "m4.MOVN"   # Motor is moving
        self.PVS.Y2_STOP = pvprefix + "m4.STOP"   # Stop command
        self.PVS.Y2_DESC = pvprefix + "m4.DESC"   # Description

        # Called Leveler Z+ in the front end.

        self.PVS.Y3      = pvprefix + "m5"        # Motor base name
        self.PVS.Y3_SP   = pvprefix + "m5.VAL"    # Setpoint value
        self.PVS.Y3_MON  = pvprefix + "m5.RBV"    # Readback value
        self.PVS.Y3_HILM = pvprefix + "m5.HLM"    # High limit
        self.PVS.Y3_LOLM = pvprefix + "m5.LLM"    # Low limit
        self.PVS.Y3_ENBL = pvprefix + "m5.CNEN"   # Enable/Disable
        self.PVS.Y3_DMVN = pvprefix + "m5.DMOV"   # Done moving
        self.PVS.Y3_MVN  = pvprefix + "m5.MOVN"   # Motor is moving
        self.PVS.Y3_STOP = pvprefix + "m5.STOP"   # Stop command
        self.PVS.Y3_DESC = pvprefix + "m5.DESC"   # Description

        # Kinematic actuators for Rx, Ry, Rz and Ty

        pvprefixk = "A:PB01:CS1:"

        # X rotation
        self.PVS.CS_RX      = pvprefixk + "m1"        # Motor base name
        self.PVS.CS_RX_SP   = pvprefixk + "m1.VAL"    # Setpoint value
        self.PVS.CS_RX_MON  = pvprefixk + "m1.RBV"    # Readback value
        self.PVS.CS_RX_HILM = pvprefixk + "m1.HLM"    # High limit
        self.PVS.CS_RX_LOLM = pvprefixk + "m1.LLM"    # Low limit
        self.PVS.CS_RX_ENBL = pvprefixk + "m1.CNEN"   # Enable/Disable
        self.PVS.CS_RX_DMVN = pvprefixk + "m1.DMOV"   # Done moving
        self.PVS.CS_RX_MVN  = pvprefixk + "m1.MOVN"   # Motor is moving
        self.PVS.CS_RX_STOP = pvprefixk + "m1.STOP"   # Stop command
        self.PVS.CS_RX_DESC = pvprefixk + "m1.DESC"   # Description

        # Y rotation
        self.PVS.CS_RY      = pvprefixk + "m2"        # Motor base name
        self.PVS.CS_RY_SP   = pvprefixk + "m2.VAL"    # Setpoint value
        self.PVS.CS_RY_MON  = pvprefixk + "m2.RBV"    # Readback value
        self.PVS.CS_RY_HILM = pvprefixk + "m2.HLM"    # High limit
        self.PVS.CS_RY_LOLM = pvprefixk + "m2.LLM"    # Low limit
        self.PVS.CS_RY_ENBL = pvprefixk + "m2.CNEN"   # Enable/Disable
        self.PVS.CS_RY_DMVN = pvprefixk + "m2.DMOV"   # Done moving
        self.PVS.CS_RY_MVN  = pvprefixk + "m2.MOVN"   # Motor is moving
        self.PVS.CS_RY_STOP = pvprefixk + "m2.STOP"   # Stop command
        self.PVS.CS_RY_DESC = pvprefixk + "m2.DESC"   # Description

        # Z rotation
        self.PVS.CS_RZ      = pvprefixk + "m3"        # Motor base name
        self.PVS.CS_RZ_SP   = pvprefixk + "m3.VAL"    # Setpoint value
        self.PVS.CS_RZ_MON  = pvprefixk + "m3.RBV"    # Readback value
        self.PVS.CS_RZ_HILM = pvprefixk + "m3.HLM"    # High limit
        self.PVS.CS_RZ_LOLM = pvprefixk + "m3.LLM"    # Low limit
        self.PVS.CS_RZ_ENBL = pvprefixk + "m3.CNEN"   # Enable/Disable
        self.PVS.CS_RZ_DMVN = pvprefixk + "m3.DMOV"   # Done moving
        self.PVS.CS_RZ_MVN  = pvprefixk + "m3.MOVN"   # Motor is moving
        self.PVS.CS_RZ_STOP = pvprefixk + "m3.STOP"   # Stop command
        self.PVS.CS_RZ_DESC = pvprefixk + "m3.DESC"   # Description

        # X translation
        self.PVS.CS_TX      = pvprefixk + "m7"        # Motor base name
        self.PVS.CS_TX_SP   = pvprefixk + "m7.VAL"    # Setpoint value
        self.PVS.CS_TX_MON  = pvprefixk + "m7.RBV"    # Readback value
        self.PVS.CS_TX_HILM = pvprefixk + "m7.HLM"    # High limit
        self.PVS.CS_TX_LOLM = pvprefixk + "m7.LLM"    # Low limit
        self.PVS.CS_TX_ENBL = pvprefixk + "m7.CNEN"   # Enable/Disable
        self.PVS.CS_TX_DMVN = pvprefixk + "m7.DMOV"   # Done moving
        self.PVS.CS_TX_MVN  = pvprefixk + "m7.MOVN"   # Motor is moving
        self.PVS.CS_TX_STOP = pvprefixk + "m7.STOP"   # Stop command
        self.PVS.CS_TX_DESC = pvprefixk + "m7.DESC"   # Description

        # Y translation
        self.PVS.CS_TY      = pvprefixk + "m8"        # Motor base name
        self.PVS.CS_TY_SP   = pvprefixk + "m8.VAL"    # Setpoint value
        self.PVS.CS_TY_MON  = pvprefixk + "m8.RBV"    # Readback value
        self.PVS.CS_TY_HILM = pvprefixk + "m8.HLM"    # High limit
        self.PVS.CS_TY_LOLM = pvprefixk + "m8.LLM"    # Low limit
        self.PVS.CS_TY_ENBL = pvprefixk + "m8.CNEN"   # Enable/Disable
        self.PVS.CS_TY_DMVN = pvprefixk + "m8.DMOV"   # Done moving
        self.PVS.CS_TY_MVN  = pvprefixk + "m8.MOVN"   # Motor is moving
        self.PVS.CS_TY_STOP = pvprefixk + "m8.STOP"   # Stop command
        self.PVS.CS_TY_DESC = pvprefixk + "m8.DESC"   # Description

        # SENSORS
        self.PVS.PHOTOCOLLECTOR = "A:RIO01:9215A:ai0"
        self.PVS.TEMP0_MON      = "A:RIO01:9226B:temp0"
        self.PVS.TEMP1_MON      = "A:RIO01:9226B:temp1"
        self.PVS.TEMP2_MON      = "A:RIO01:9226B:temp2"
        self.PVS.TEMP3_MON      = "A:RIO01:9226B:temp3"
        self.PVS.TEMP4_MON      = "A:RIO01:9226B:temp4"
        self.PVS.TEMP_SP        = "A:RIO01:M1_CtrltempSp"
        self.PVS.TEMP_RB        = "A:RIO01:M1_CtrltempSp"

        # FLOWMETERS
        self.PVS.FLOWMETER1_MON = "F:EPS01:MR1FIT1"
        self.PVS.FLOWMETER2_MON = "F:EPS01:MR1FIT2"

        self.PROPERTIES_DEFAULT = tuple(
            set(value for key, value in vars(self.PVS).items())
        )
