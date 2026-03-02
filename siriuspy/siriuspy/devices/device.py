"""Epics Devices and Device Application."""

import math as _math
import operator as _opr
import time as _time
from types import SimpleNamespace as _SimpleNamespace
from functools import partial as _partial

import numpy as _np
from epics.ca import (
    CASeverityException as _CASeverityException,
    ChannelAccessGetFailure as _ChannelAccessGetFailure,
)

from ..envars import VACA_PREFIX as _VACA_PREFIX
from ..epics import (
    CONNECTION_TIMEOUT as _CONN_TIMEOUT,
    GET_TIMEOUT as _GET_TIMEOUT,
    PV as _PV,
)
from ..namesys import SiriusPVName as _SiriusPVName
from ..simul import SimPV as _PVSim, Simulation as _Simulation

_DEF_TIMEOUT = 10  # s
_TINY_INTERVAL = 0.050  # s

class _PVNames(_SimpleNamespace):
    def __getattr__(self, name):
        """."""
        return None


class _PVAccessor:
    """Dynamic motor PV accessor with robust, retried movement.

    This mixin adds transparent attribute-style access to any motor that is
    defined in the concrete device's PVS namespace. The convention used is:

        {BASE}        motor record base PV  (reads .VAL field by default)
        {BASE}_MON    readback (monitor) PV (.RBV)
        {BASE}_SP     setpoint PV           (.VAL)
        {BASE}_LOLM   low  hardware limit   (.LLM)
        {BASE}_HILM   high hardware limit   (.HLM)

    Any PVS entry is accessible by lowercasing its name:
        mirror.ry       → self[PVS.RY]       (motor base / VAL)
        mirror.ry_mon   → self[PVS.RY_MON]   (readback, .RBV)
        mirror.tx_lolm  → self[PVS.TX_LOLM]  (low limit)
        mirror.cs_rz    → self[PVS.CS_RZ]
        mirror.cs_rz_hilm → self[PVS.CS_RZ_HILM]

    No additional mapping dictionary is required; any motor added to PVS in a
    subclass becomes immediately accessible here.

    Usage
    -----
    Reading:   mirror.ry_mon        → current readback value [mrad]
    Writing:   mirror.ry = 5.0      → blocks until motor reaches 5 mrad

    The write path calls _move_robust_device_motor, which:
      1. Validates the value against [LOLM, HILM] limits.
      2. Writes the setpoint.
      3. Polls the readback until the error is below threshold.
      4. Retries up to _TRIALS times before giving up.

    Direct setpoint write (no blocking):
        mirror['A:PB01:m2.VAL'] = 5.0   ← bypass the accessor if needed
    """
    # Default parameters for motor movement;
    # can be overridden per-motor in move().
    _COUNT_LIM = 8
    _DELAY     = 4    # [s]
    _TRIALS    = 3

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
        if f"{candidate}" in pvs:
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
        """Read from the corresponding PVS when a motor attribute is accessed.

        Only called when normal lookup (class dict, instance dict) fails.
        The name is uppercased and looked up verbatim in PVS, so any PVS
        entry is reachable:

            mirror.ry         → self[PVS.RY]       (motor base / VAL)
            mirror.ry_mon     → self[PVS.RY_MON]   (readback, .RBV)
            mirror.ry_sp      → self[PVS.RY_SP]    (setpoint, .VAL)
            mirror.tx_lolm    → self[PVS.TX_LOLM]  (low limit)
            mirror.cs_rz_hilm → self[PVS.CS_RZ_HILM]
        """
        # Check if this is a motor attribute by looking for its base in PVS.
        base = self._motor_base(name)
        if base is not None:
            pv = getattr(self.PVS, base)
            if pv is not None:
                return self[pv]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name, value):
        """Write an attribute, routing through the appropriate mechanism.

        Three cases:
        1. Full motors (PVS has both {BASE}_SP and {BASE}_MON) → robust
           blocking move via _move_robust_device_motor.
        2. Other PVS entries (limits, enable flags, …) → direct PV write,
           consistent with how slit.py and dvf.py handle these.
        3. Anything else → regular instance attribute.

        No special-casing of private names or 'PVS' is needed: _pvs_motor_bases
        uses the class-level PVS (always present), and _PVNames.__getattr__
        safely returns None for any undefined attribute, so everything
        falls through to object.__setattr__ correctly.
        """
        base = name.upper()

        # Motor attribute: route through the movement engine.
        if base in self._pvs_motor_bases():
            self._move_robust_device_motor(
                motor=name,
                value=value,
                threshold=self._motor_threshold(name),
                max_count=self._COUNT_LIM,
                delay=self._DELAY,
                trials=self._TRIALS,
            )
            return

        # Non-motor PVS entry (limit, enable, …): write directly.
        pv = getattr(self.PVS, base)
        if pv is not None:
            self[pv] = value
            return

        # Regular attribute: set as usual.
        object.__setattr__(self, name, value)

    # ── motor movement engine ─────────────────────────────────────────────

    def _move_device_motor(self, motor, value, threshold, max_count, delay):
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
            mb = sorted(b.lower() for b in self._pvs_motor_bases())
            raise ValueError(
                f"Motor '{motor}' not found in PVS. "
                f"Available: {mb}"
            )

        sp_pv   = getattr(self.PVS, f"{base}_SP")
        mon_pv  = getattr(self.PVS, f"{base}_MON")
        lolm_pv = getattr(self.PVS, f"{base}_LOLM")
        hilm_pv = getattr(self.PVS, f"{base}_HILM")
        movn_pv = getattr(self.PVS, f"{base}_MVN")

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

            # Check for convergence. If the motor is still moving
            # (MOVN == 1), continue loop.
            if diff <= threshold and self[movn_pv] == 0:
                return True
            if icount < max_count:
                _time.sleep(delay)

        print(
            f"\nWARNING: '{motor}' did not reach {value}."
            f" Current: {self[mon_pv]:.4f}"
        )
        return False

    def _move_robust_device_motor(
        self, motor, value, threshold, max_count, delay, trials
    ):
        """Retry _move_device_motor up to *trials* times.

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
            if self._move_device_motor(motor, value, threshold,
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
        return self._move_robust_device_motor(
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

class Device:
    """Epics Device.

    Parameters
    ----------
        devname: str
            Device name, to be used as PVs prefix.
        props2init: ('all', None or (tuple, list)), optional
            Define which PVs will be connected in the class instantiation. If
            equal to 'all', all properties listed in PROPERTIES_DEFAULT will
            be initialized. If None or empty iterable, no property will be
            initialized. If iterable of strings, only the properties listed
            will be initialized. In this last option, it is possible to add
            properties that are not in PROPERTIES_DEFAULT. The other properties
            will be created whenever they are needed. Defaults to 'all'.
        auto_monitor: bool, optional
            Whether to automatically monitor PVs for changes. Used for PVs
            that do not end with '-Mon' or 'Data'. Defaults to True.
        auto_monitor_mon: bool, optional
            Whether to automatically monitor '-Mon' or 'Data' PVs for changes.
            Defaults to False (to avoid overloading the client). Set to False
            when using PV.get_timevars() to know when a PV has been updated.

    """

    CONNECTION_TIMEOUT = _CONN_TIMEOUT
    GET_TIMEOUT = _GET_TIMEOUT
    PROPERTIES_DEFAULT = ()

    PROPERTY_SEP = ":"

    def __init__(
        self,
        devname,
        props2init="all",
        auto_monitor=True,
        auto_monitor_mon=False,
    ):
        """."""
        self._devname = _SiriusPVName(devname) if devname else devname
        self._auto_monitor = auto_monitor
        self._auto_monitor_mon = auto_monitor_mon

        if isinstance(props2init, str) and props2init.lower() == "all":
            propties = self.PROPERTIES_DEFAULT
        elif not props2init:
            propties = []
        elif isinstance(props2init, (list, tuple)):
            propties = props2init
        else:
            raise ValueError("Wrong value for props2init.")
        self._pvs = {prpt: self._create_pv(prpt) for prpt in propties}

    @property
    def devname(self):
        """Return device name."""
        return self._devname

    @property
    def properties_in_use(self):
        """Return properties that were already added to the PV list."""
        return tuple(sorted(self._pvs.keys()))

    @property
    def properties_added(self):
        """Return properties added to PV list not in PROPERTIES_DEFAULT."""
        return tuple(
            sorted(set(self.properties_in_use) - set(self.PROPERTIES_DEFAULT))
        )

    @property
    def properties_all(self):
        """Return all properties of the device, connected or not."""
        return tuple(
            sorted(set(self.PROPERTIES_DEFAULT + self.properties_in_use))
        )

    @property
    def simulators(self):
        """Return simulator."""
        sims = set()
        for pvname in self.pvnames:
            sims.update(_Simulation.simulator_find(pvname))
        return sims

    @property
    def pvnames(self):
        """Return device PV names."""
        pvnames = {pv.pvname for pv in self._pvs.values()}
        return pvnames

    @property
    def connected(self):
        """Return PVs connection status."""
        for pvobj in self._pvs.values():
            if not pvobj.connected:
                return False
        return True

    @property
    def auto_monitor_status(self):
        """Return PVs auto_monitor statuses."""
        return {pvn: pv.auto_monitor for pvn, pv in self._pvs.items()}

    @property
    def disconnected_pvnames(self):
        """Return list of disconnected device PVs."""
        set_ = set()
        for pvobj in self._pvs.values():
            if not pvobj.connected:
                set_.add(pvobj.pvname)
        return set_

    def set_auto_monitor(self, pvname, value):
        """Set auto_monitor state of individual PVs."""
        if pvname not in self._pvs:
            return False
        pvobj = self._pvs[pvname]
        try:
            # TODO verify need of int
            pvobj.auto_monitor = int(value)
        except (_ChannelAccessGetFailure, _CASeverityException):
            # exceptions raised in a Virtual Circuit Disconnect (192)
            # event. If the PV IOC goes down, for example.
            print("Could not set auto_monitor of {}".format(pvobj.pvname))
            return False
        return True

    def update(self):
        """Update device properties."""
        for pvobj in self._pvs.values():
            pvobj.get()

    def pv_object(self, propty):
        """Return PV object for a given device property."""
        if propty not in self._pvs:
            pvobj = self._create_pv(propty)
            pvobj.wait_for_connection(Device.CONNECTION_TIMEOUT)
            self._pvs[propty] = pvobj
        return self._pvs[propty]

    def pv_ctrlvars(self, propty):
        """Return PV object control variable."""
        return self._pvs[propty].get_ctrlvars()

    def pv_attribute_values(self, attribute):
        """Return pvname-value dict of a given attribute for all PVs."""
        attributes = dict()
        for pvobj in self._pvs.values():
            attributes[pvobj.pvname] = getattr(pvobj, attribute)
        return attributes

    @property
    def hosts(self):
        """Return dict of IOC hosts providing device properties."""
        return self.pv_attribute_values("host")

    @property
    def values(self):
        """Return dict of property values."""
        return self.pv_attribute_values("value")

    def wait_for_connection(self, timeout=None):
        """Wait for connection."""
        for pvobj in self._pvs.values():
            res = pvobj.wait_for_connection(timeout)
            if not res:
                return False
        return True

    def __getitem__(self, propty):
        """Return value of property."""
        pvobj = self.pv_object(propty)
        try:
            value = pvobj.get(timeout=Device.GET_TIMEOUT)
        except (_ChannelAccessGetFailure, _CASeverityException):
            # exceptions raised in a Virtual Circuit Disconnect (192)
            # event. If the PV IOC goes down, for example.
            print("Could not get value of {}".format(pvobj.pvname))
            value = None
        return value

    def __setitem__(self, propty, value):
        """Set value of property."""
        pvobj = self.pv_object(propty)
        try:
            pvobj.value = value
        except (_ChannelAccessGetFailure, _CASeverityException):
            print("Could not set value of {}".format(pvobj.pvname))

    # --- private methods ---
    def _create_pv(self, propty):
        pvname = self._get_pvname(propty)
        auto_monitor = self._auto_monitor
        if pvname.endswith(("-Mon", "Data")):
            auto_monitor = self._auto_monitor_mon
        in_sim = _Simulation.pv_check(pvname)
        pvclass = _PVSim if in_sim else _PV
        return pvclass(
            pvname,
            auto_monitor=auto_monitor,
            connection_timeout=Device.CONNECTION_TIMEOUT,
        )

    def _wait(self, propty, value, timeout=None, comp="eq"):
        """."""

        def comp_(val):
            boo = comp(self[propty], val)
            if isinstance(boo, _np.ndarray):
                boo = _np.all(boo)
            return boo

        if isinstance(comp, str):
            comp = getattr(_opr, comp)

        if not isinstance(timeout, str) and timeout != "never":
            timeout = _DEF_TIMEOUT if timeout is None else timeout
            timeout = 0 if timeout <= 0 else timeout
        t0_ = _time.time()
        while not comp_(value):
            if isinstance(timeout, str) and timeout == "never":
                pass
            else:
                if _time.time() - t0_ > timeout:
                    return False
            _time.sleep(_TINY_INTERVAL)
        return True

    def _wait_float(
        self, propty, value, rel_tol=0.0, abs_tol=0.1, timeout=None
    ):
        """Wait until float value gets close enough of desired value."""
        isc = _np.isclose if isinstance(value, _np.ndarray) else _math.isclose
        func = _partial(isc, abs_tol=abs_tol, rel_tol=rel_tol)
        return self._wait(propty, value, comp=func, timeout=timeout)

    def _wait_set(self, props_values, timeout=None, comp="eq"):
        timeout = _DEF_TIMEOUT if timeout is None else timeout
        t0_ = _time.time()
        for propty, value in props_values.items():
            timeout_left = max(0, timeout - (_time.time() - t0_))
            if timeout_left == 0:
                return False
            if not self._wait(propty, value, timeout=timeout_left, comp=comp):
                return False
        return True

    def _get_pvname(self, propty):
        if propty is None:
            raise ValueError("Property does not exist for this Base Device")
        dev = self._devname
        pref = _VACA_PREFIX + ("-" if _VACA_PREFIX else "")
        if isinstance(dev, _SiriusPVName) and dev.is_standard(
            name_type="devname"
        ):
            ppt = dev.propty
            pvname = dev.substitute(prefix=_VACA_PREFIX, propty=ppt + propty)
        elif dev:
            pvname = pref + dev + self.PROPERTY_SEP + propty
        else:
            pvname = pref + propty
        return pvname

    def _enum_setter(self, propty, value, enums):
        value = self._enum_selector(value, enums)
        if value is not None:
            self[propty] = value

    @staticmethod
    def _enum_selector(value, enums):
        if value is None:
            return
        if hasattr(enums, "_fields"):
            enums = enums._fields
        if isinstance(value, str) and value in enums:
            return enums.index(value)
        elif 0 <= int(value) < len(enums):
            return value


class DeviceSet:
    """."""

    def __init__(self, devices, devname=""):
        """."""
        self._devices = devices
        self._devname = _SiriusPVName(devname)

    _enum_selector = staticmethod(Device._enum_selector)

    @property
    def devname(self):
        """Name of the Device set. May be empty in some cases."""
        return self._devname

    @property
    def simulators(self):
        """Return list of simulators."""
        sims = set()
        for dev in self._devices:
            sims.update(dev.simulators)
        return sims

    @property
    def pvnames(self):
        """Return device PV names."""
        set_ = set()
        for dev in self._devices:
            set_.update(dev.pvnames)
        return set_

    @property
    def connected(self):
        """Return PVs connection status."""
        for dev in self._devices:
            if not dev.connected:
                return False
        return True

    @property
    def disconnected_pvnames(self):
        """Return list of disconnected device PVs."""
        set_ = set()
        for dev in self._devices:
            set_.update(dev.disconnected_pvnames)
        return set_

    @property
    def auto_monitor_status(self):
        """Return PVs auto_monitor statuses."""
        dic_ = dict()
        for dev in self._devices:
            dic_.update(dev.auto_monitor_status)
        return dic_

    def update(self):
        """Update device properties."""
        for dev in self._devices:
            dev.update()

    def pv_attribute_values(self, attribute):
        """Return property-value dict of a given attribute for all PVs."""
        attributes = dict()
        for dev in self._devices:
            attrs = dev.pv_attribute_values(attribute)
            attributes.update(attrs)
        return attributes

    @property
    def hosts(self):
        """Return dict of IOC hosts providing device properties."""
        return self.pv_attribute_values("host")

    @property
    def values(self):
        """Return dict of property values."""
        return self.pv_attribute_values("value")

    def wait_for_connection(self, timeout=None):
        """Wait for connection."""
        for dev in self._devices:
            if not dev.wait_for_connection(timeout=timeout):
                return False
        return True

    @property
    def devices(self):
        """Return devices."""
        return self._devices

    # --- private methods ---

    def _set_devices_propty(self, devices, propty, values, wait=0):
        """Set devices property to value(s)."""
        dev2val = self._get_dev_2_val(devices, values)
        for dev, val in dev2val.items():
            if dev.pv_object(propty).wait_for_connection():
                dev[propty] = val
                _time.sleep(wait)

    def _wait_devices_propty(
        self,
        devices,
        propty,
        values,
        comp="eq",
        timeout=None,
        return_prob=False,
    ):
        """Wait for devices property to reach value(s)."""
        if isinstance(comp, str):
            comp = getattr(_opr, comp)
        dev2val = self._get_dev_2_val(devices, values)

        timeout = _DEF_TIMEOUT if timeout is None else timeout
        tini = _time.time()
        for _ in range(int(timeout / _TINY_INTERVAL)):
            okdevs = set()
            for k, v in dev2val.items():
                boo = comp(k[propty], v)
                if isinstance(boo, _np.ndarray):
                    boo = _np.all(boo)
                if boo:
                    okdevs.add(k)
                if _time.time() - tini > timeout:
                    break
            list(map(dev2val.__delitem__, okdevs))
            if not dev2val:
                break
            if _time.time() - tini > timeout:
                break
            _time.sleep(_TINY_INTERVAL)

        allok = not dev2val
        if return_prob:
            return allok, [dev.pv_object(propty).pvname for dev in dev2val]
        return allok

    def _get_dev_2_val(self, devices, values):
        """Get devices to values dict."""
        # always use an iterable object
        if not isinstance(devices, (tuple, list)):
            devices = [devices]
        # if 'values' is not iterable, consider the same value for all devices
        if not isinstance(values, (tuple, list)):
            values = len(devices) * [values]
        return {k: v for k, v in zip(devices, values, strict=False)}

    def __getitem__(self, devidx):
        """Return device."""
        return self._devices[devidx]
