"""Mirror Control."""

# import inspect as _inspect
import time as _time
from types import SimpleNamespace as _SimpleNamespace

from ..device import Device as _Device


class _PVNames(_SimpleNamespace):
    def __getattr__(self, name):
        """."""
        return None


class _PVAccessor:
    """Dynamic motor PV accessor with robust, retried movement.

    This mixin adds transparent attribute-style access to any motor that is
    defined in the concrete device's PVS namespace following the convention:

        {BASE}_MON    readback (monitor) PV
        {BASE}_SP     setpoint PV
        {BASE}_LOLM   low  hardware limit PV   (optional but recommended)
        {BASE}_HILM   high hardware limit PV   (optional but recommended)

    The user-facing attribute name is the base name lowercased:
        PVS.RY_MON / PVS.RY_SP  →  motor name "ry"
        PVS.CS_RX_MON / …       →  motor name "cs_rx"

    No additional mapping dictionary is required; any motor added to PVS in a
    subclass becomes immediately accessible here.

    Usage
    -----
    Reading:    mirror.ry          → float (current readback)
    Writing:    mirror.ry = 5.0   → blocks until motor reaches 5 mrad

    The write path calls _move_robust_mirror_motor, which:
      1. Validates the value against [LOLM, HILM] limits.
      2. Writes the setpoint.
      3. Polls the readback until the error is below threshold.
      4. Retries up to _TRIALS times before giving up.

    Direct setpoint write (no blocking):
        mirror['A:PB01:m2.VAL'] = 5.0   ← bypass the accessor if needed
    """

    # Motors whose motion threshold is angular rather than positional.
    _ANGULAR_MOTORS = frozenset({
        "rx", "ry", "rz",
        "cs_rx", "cs_ry", "cs_rz",
    })

    # ── private helpers ───────────────────────────────────────────────────

    def _pvs_motor_bases(self):
        """Return the set of PVS base names that have both _MON and _SP.

        Example: if PVS has RY_MON and RY_SP, "RY" is in the result set.
        """
        pvs = vars(self.PVS)
        bases_mon = {k[:-4] for k in pvs if k.endswith("_MON")}
        bases_sp  = {k[:-3] for k in pvs if k.endswith("_SP")}
        return bases_mon & bases_sp

    def _motor_base(self, name):
        """Translate user-facing motor name to its PVS base, or None.

        "ry"    → "RY"
        "cs_rx" → "CS_RX"
        Anything not found in PVS → None
        """
        candidate = name.upper()
        pvs = vars(self.PVS)
        if f"{candidate}_MON" in pvs or f"{candidate}_SP" in pvs:
            return candidate
        return None

    def _motor_threshold(self, name):
        """Return the convergence threshold appropriate for this motor."""
        return (
            self._THRESHOLD_ANG
            if name in self._ANGULAR_MOTORS
            else self._THRESHOLD_POS
        )

    # ── attribute interception ────────────────────────────────────────────

    def __getattr__(self, name):
        """Read from the _MON PV when a motor name is accessed as an attribute.

        Only called when normal lookup (class dict, instance dict) fails.
        Private / dunder attributes and 'PVS' raise AttributeError immediately
        to avoid infinite recursion.
        """
        if name.startswith("_") or name in ("PVS",):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        base = self._motor_base(name)
        if base is not None:
            mon_pv = getattr(self.PVS, f"{base}_MON")
            if mon_pv is not None:
                return self[mon_pv]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name, value):
        """Write to motor via robust movement when a motor name is assigned.

        Non-motor attributes (private, 'PVS', or anything not in PVS) are
        stored normally via object.__setattr__ so that regular instance
        attributes (e.g. PROPERTIES_DEFAULT) are unaffected.
        """
        if name.startswith("_") or name == "PVS":
            object.__setattr__(self, name, value)
            return
        base = self._motor_base(name)
        if base is not None:
            self._move_robust_mirror_motor(
                motor=name,
                value=value,
                threshold=self._motor_threshold(name),
                max_count=self._COUNT_LIM,
                delay=self._DELAY,
                trials=self._TRIALS,
            )
            return
        object.__setattr__(self, name, value)

    # ── motor movement engine ─────────────────────────────────────────────

    def _move_mirror_motor(self, motor, value, threshold, max_count, delay):
        """Write setpoint and poll readback until convergence or timeout.

        Args:
            motor     : user-facing motor name ('ry', 'tx', 'cs_rx', …).
            value     : target position.
            threshold : convergence criterion (|readback - value| < threshold).
            max_count : number of polling iterations before giving up.
            delay     : seconds to wait between iterations.

        Returns:
            True  if the motor reached the target within max_count iterations.
            False on timeout.

        Raises:
            ValueError : if value is outside [LOLM, HILM] limits.
            IOError    : if the setpoint PUT fails unexpectedly.
        """
        base = self._motor_base(motor)
        if base is None:
            raise ValueError(
                f"Motor '{motor}' not found in PVS. "
                f"Available: {sorted(b.lower()
                                     for b in self._pvs_motor_bases())}"
            )

        sp_pv   = getattr(self.PVS, f"{base}_SP")
        mon_pv  = getattr(self.PVS, f"{base}_MON")
        lolm_pv = getattr(self.PVS, f"{base}_LOLM")
        hilm_pv = getattr(self.PVS, f"{base}_HILM")

        # Limit validation — EPICS hardware limits are the source of truth.
        if lolm_pv is not None and hilm_pv is not None:
            low, high = self[lolm_pv], self[hilm_pv]
            if not (low <= value <= high):
                raise ValueError(
                    f"'{motor}' target {value} is outside hardware limits "
                    f"[{low}, {high}]."
                )

        # Send setpoint.
        try:
            self[sp_pv] = value
        except Exception as err:
            current = self[mon_pv]
            raise IOError(
                f"PUT error for '{motor}': current={current:.4f}\n{err}"
            ) from err

        # Poll readback.
        for icount in range(max_count + 1):
            current = self[mon_pv]
            diff = abs(current - value)
            print(
                f"Moving '{motor}' → {value} | now: {current:.4f}"
                f" | Δ: {diff:.4f}", end="\r",
            )
            if diff <= threshold:
                return True
            if icount < max_count:
                _time.sleep(delay)

        print(
            f"\nWARNING: '{motor}' did not reach {value}."
            f" Current: {self[mon_pv]:.4f}"
        )
        return False

    def _move_robust_mirror_motor(
        self, motor, value, threshold, max_count, delay, trials
    ):
        """Retry _move_mirror_motor up to *trials* times.

        Args:
            motor     : user-facing motor name.
            value     : target position.
            threshold : convergence criterion.
            max_count : polling iterations per trial.
            delay     : seconds between polling iterations.
            trials    : maximum number of move attempts.

        Returns:
            True if the motor reached the target; False otherwise.
        """
        for attempt in range(1, trials + 1):
            if self._move_mirror_motor(motor, value, threshold,
                                       max_count, delay):
                print(f"\n'{motor}' reached {value}"
                      f" (attempt {attempt}/{trials}).")
                return True
        current = getattr(self, motor)
        print(
            f"\n'{motor}' failed after {trials} attempt(s)."
            f" Current: {current:.4f}"
        )
        return False

    def move(self, motor, value, threshold=None, max_count=None, delay=None):
        """Move *motor* to *value* with full retry logic.

        Generic replacement for the individual move_rx / move_ry / move_tx / …
        methods.  Those explicit methods may still exist in MirrorBase for
        backward compatibility, but they all delegate here.

        Args:
            motor     : user-facing motor name ('ry', 'tx', 'cs_rx', …).
            value     : target position.
            threshold : override default threshold (optional).
            max_count : override _COUNT_LIM (optional).
            delay     : override _DELAY (optional).

        Returns:
            True on success, False on failure.
        """
        return self._move_robust_mirror_motor(
            motor=motor,
            value=value,
            threshold=(threshold if threshold is not None
                       else self._motor_threshold(motor)),
            max_count=max_count if max_count is not None else self._COUNT_LIM,
            delay=delay if delay is not None else self._DELAY,
            trials=self._TRIALS,
        )

    def stop(self, motor, timeout=None):
        """Send stop command to *motor* and wait for it to finish moving.

        Args:
            motor   : user-facing motor name ('ry', 'tx', 'y1', …).
            timeout : seconds to wait for the motor to stop.
                      Defaults to _DEFAULT_MOTOR_TIMEOUT.

        Returns:
            True if the motor stopped within timeout; False otherwise.
        """
        base = self._motor_base(motor)
        if base is None:
            raise ValueError(f"Motor '{motor}' not found in PVS.")
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        stop_pv = getattr(self.PVS, f"{base}_STOP")
        dmvn_pv = getattr(self.PVS, f"{base}_DMVN")
        self[stop_pv] = 1
        if dmvn_pv is not None:
            return self._wait(dmvn_pv, 0, timeout=timeout)
        return True


class MirrorBase(_PVAccessor, _Device):
    """Base Mirror device."""

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]
    _THRESHOLD_POS = 0.01  # [mm]
    _THRESHOLD_ANG = 0.01  # [mrad]
    _COUNT_LIM = 8
    _DELAY     = 4                # [s]
    _TRIALS    = 3

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
        self.PVS.TX_DMVN = pvprefix + "m1.DMOVN"  # Done moving
        self.PVS.TX_MVN  = pvprefix + "m1.MOVN"   # Motor is moving
        self.PVS.TX_STOP = pvprefix + "m1.STOP"   # Stop command

        # Y Rotation
        self.PVS.RY      = pvprefix + "m2"        # Motor base name
        self.PVS.RY_SP   = pvprefix + "m2.VAL"    # Setpoint value
        self.PVS.RY_MON  = pvprefix + "m2.RBV"    # Readback value
        self.PVS.RY_HILM = pvprefix + "m2.HLM"    # High limit
        self.PVS.RY_LOLM = pvprefix + "m2.LLM"    # Low limit
        self.PVS.RY_ENBL = pvprefix + "m2.CNEN"   # Enable/Disable
        self.PVS.RY_DMVN = pvprefix + "m2.DMOVN"  # Done moving
        self.PVS.RY_MVN  = pvprefix + "m2.MOVN"   # Motor is moving
        self.PVS.RY_STOP = pvprefix + "m2.STOP"   # Stop command

        # Called Leveler Z- in the front end.
        self.PVS.Y1      = pvprefix + "m3"        # Motor base name
        self.PVS.Y1_SP   = pvprefix + "m3.VAL"    # Setpoint value
        self.PVS.Y1_MON  = pvprefix + "m3.RBV"    # Readback value
        self.PVS.Y1_HILM = pvprefix + "m3.HLM"    # High limit
        self.PVS.Y1_LOLM = pvprefix + "m3.LLM"    # Low limit
        self.PVS.Y1_ENBL = pvprefix + "m3.CNEN"   # Enable/Disable
        self.PVS.Y1_DMVN = pvprefix + "m3.DMOVN"  # Done moving
        self.PVS.Y1_MVN  = pvprefix + "m3.MOVN"   # Motor is moving
        self.PVS.Y1_STOP = pvprefix + "m3.STOP"   # Stop command

        # Called Leveler X+ in the front end.
        self.PVS.Y2      = pvprefix + "m4"        # Motor base name
        self.PVS.Y2_SP   = pvprefix + "m4.VAL"    # Setpoint value
        self.PVS.Y2_MON  = pvprefix + "m4.RBV"    # Readback value
        self.PVS.Y2_HILM = pvprefix + "m4.HLM"    # High limit
        self.PVS.Y2_LOLM = pvprefix + "m4.LLM"    # Low limit
        self.PVS.Y2_ENBL = pvprefix + "m4.CNEN"   # Enable/Disable
        self.PVS.Y2_DMVN = pvprefix + "m4.DMOVN"  # Done moving
        self.PVS.Y2_MVN  = pvprefix + "m4.MOVN"   # Motor is moving
        self.PVS.Y2_STOP = pvprefix + "m4.STOP"   # Stop command

        # Called Leveler Z+ in the front end.

        self.PVS.Y3      = pvprefix + "m5"        # Motor base name
        self.PVS.Y3_SP   = pvprefix + "m5.VAL"    # Setpoint value
        self.PVS.Y3_MON  = pvprefix + "m5.RBV"    # Readback value
        self.PVS.Y3_HILM = pvprefix + "m5.HLM"    # High limit
        self.PVS.Y3_LOLM = pvprefix + "m5.LLM"    # Low limit
        self.PVS.Y3_ENBL = pvprefix + "m5.CNEN"   # Enable/Disable
        self.PVS.Y3_DMVN = pvprefix + "m5.DMOVN"  # Done moving
        self.PVS.Y3_MVN  = pvprefix + "m5.MOVN"   # Motor is moving
        self.PVS.Y3_STOP = pvprefix + "m5.STOP"   # Stop command

        # Kinematic actuators for Rx, Ry, Rz and Ty

        pvprefixk = "A:PB01:CS1:"

        # X rotation
        self.PVS.CS_RX      = pvprefixk + "m1"        # Motor base name
        self.PVS.CS_RX_SP   = pvprefixk + "m1.VAL"    # Setpoint value
        self.PVS.CS_RX_MON  = pvprefixk + "m1.RBV"    # Readback value
        self.PVS.CS_RX_HILM = pvprefixk + "m1.HLM"    # High limit
        self.PVS.CS_RX_LOLM = pvprefixk + "m1.LLM"    # Low limit
        self.PVS.CS_RX_ENBL = pvprefixk + "m1.CNEN"   # Enable/Disable
        self.PVS.CS_RX_DMVN = pvprefixk + "m1.DMOVN"  # Done moving
        self.PVS.CS_RX_MVN  = pvprefixk + "m1.MOVN"   # Motor is moving
        self.PVS.CS_RX_STOP = pvprefixk + "m1.STOP"   # Stop command

        # Y rotation
        self.PVS.CS_RY      = pvprefixk + "m2"        # Motor base name
        self.PVS.CS_RY_SP   = pvprefixk + "m2.VAL"    # Setpoint value
        self.PVS.CS_RY_MON  = pvprefixk + "m2.RBV"    # Readback value
        self.PVS.CS_RY_HILM = pvprefixk + "m2.HLM"    # High limit
        self.PVS.CS_RY_LOLM = pvprefixk + "m2.LLM"    # Low limit
        self.PVS.CS_RY_ENBL = pvprefixk + "m2.CNEN"   # Enable/Disable
        self.PVS.CS_RY_DMVN = pvprefixk + "m2.DMOVN"  # Done moving
        self.PVS.CS_RY_MVN  = pvprefixk + "m2.MOVN"   # Motor is moving
        self.PVS.CS_RY_STOP = pvprefixk + "m2.STOP"   # Stop command

        # Z rotation
        self.PVS.CS_RZ      = pvprefixk + "m3"        # Motor base name
        self.PVS.CS_RZ_SP   = pvprefixk + "m3.VAL"    # Setpoint value
        self.PVS.CS_RZ_MON  = pvprefixk + "m3.RBV"    # Readback value
        self.PVS.CS_RZ_HILM = pvprefixk + "m3.HLM"    # High limit
        self.PVS.CS_RZ_LOLM = pvprefixk + "m3.LLM"    # Low limit
        self.PVS.CS_RZ_ENBL = pvprefixk + "m3.CNEN"   # Enable/Disable
        self.PVS.CS_RZ_DMVN = pvprefixk + "m3.DMOVN"  # Done moving
        self.PVS.CS_RZ_MVN  = pvprefixk + "m3.MOVN"   # Motor is moving
        self.PVS.CS_RZ_STOP = pvprefixk + "m3.STOP"   # Stop command

        # X translation
        self.PVS.CS_TX      = pvprefixk + "m7"        # Motor base name
        self.PVS.CS_TX_SP   = pvprefixk + "m7.VAL"    # Setpoint value
        self.PVS.CS_TX_MON  = pvprefixk + "m7.RBV"    # Readback value
        self.PVS.CS_TX_HILM = pvprefixk + "m7.HLM"    # High limit
        self.PVS.CS_TX_LOLM = pvprefixk + "m7.LLM"    # Low limit
        self.PVS.CS_TX_ENBL = pvprefixk + "m7.CNEN"   # Enable/Disable
        self.PVS.CS_TX_DMVN = pvprefixk + "m7.DMOVN"  # Done moving
        self.PVS.CS_TX_MVN  = pvprefixk + "m7.MOVN"   # Motor is moving
        self.PVS.CS_TX_STOP = pvprefixk + "m7.STOP"   # Stop command

        # Y translation
        self.PVS.CS_TY      = pvprefixk + "m8"        # Motor base name
        self.PVS.CS_TY_SP   = pvprefixk + "m8.VAL"    # Setpoint value
        self.PVS.CS_TY_MON  = pvprefixk + "m8.RBV"    # Readback value
        self.PVS.CS_TY_HILM = pvprefixk + "m8.HLM"    # High limit
        self.PVS.CS_TY_LOLM = pvprefixk + "m8.LLM"    # Low limit
        self.PVS.CS_TY_ENBL = pvprefixk + "m8.CNEN"   # Enable/Disable
        self.PVS.CS_TY_DMVN = pvprefixk + "m8.DMOVN"  # Done moving
        self.PVS.CS_TY_MVN  = pvprefixk + "m8.MOVN"   # Motor is moving
        self.PVS.CS_TY_STOP = pvprefixk + "m8.STOP"   # Stop command

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
