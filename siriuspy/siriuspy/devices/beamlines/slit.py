"""Slit Control."""

import inspect as _inspect
import time as _time

from ..device import Device as _Device


class _PVs:
    # SLITS
    # --- TOP ---
    TOP_SP = None
    TOP_RB = None
    TOP_MON = None
    TOP_STOP = None

    # --- BOTTOM ---
    BOTTOM_SP = None
    BOTTOM_RB = None
    BOTTOM_MON = None
    BOTTOM_STOP = None

    # --- LEFT ---
    LEFT_SP = None
    LEFT_RB = None
    LEFT_MON = None
    LEFT_STOP = None

    # --- RIGHT ---
    RIGHT_SP = None
    RIGHT_RB = None
    RIGHT_MON = None
    RIGHT_STOP = None


class Slit(_Device):
    """Slit device."""

    class DEVICES:
        """Devices names."""

        SLIT1 = "CAX:A:PP02"  # WBS1
        SLIT2 = "CAX:B:PP01"  # WBS2

        ALL = (SLIT1, SLIT2)

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]
    _THRESHOLD = 0.01  # [mm]
    _COUNT_LIM = 8
    _DELAY = 4  # [s]
    _TRIALS = 3

    # --- PARAM_PVS ---
    PARAM_PVS = _PVs()

    PARAM_PVS.TOP_SP = "A.VAL"
    PARAM_PVS.TOP_RB = "A.VAL"  # That doesn't have a RB PV
    PARAM_PVS.TOP_MON = "A.RBV"  # RBV is not the pv of readback
    PARAM_PVS.TOP_STOP = "A.STOP"

    PARAM_PVS.BOTTOM_SP = "B.VAL"
    PARAM_PVS.BOTTOM_RB = "B.VAL"  # That doesn't have a RB PV
    PARAM_PVS.BOTTOM_MON = "B.RBV"  # RBV is not the pv of readback
    PARAM_PVS.BOTTOM_STOP = "B.STOP"

    PARAM_PVS.LEFT_SP = "C.VAL"
    PARAM_PVS.LEFT_RB = "C.VAL"  # That doesn't have a RB PV
    PARAM_PVS.LEFT_MON = "C.RBV"  # RBV is not the pv of readback
    PARAM_PVS.LEFT_STOP = "C.STOP"

    PARAM_PVS.RIGHT_SP = "D.VAL"
    PARAM_PVS.RIGHT_RB = "D.VAL"  # That doesn't have a RB PV
    PARAM_PVS.RIGHT_MON = "D.RBV"  # RBV is not the pv of readback
    PARAM_PVS.RIGHT_STOP = "D.STOP"

    PROPERTIES_DEFAULT = tuple(
        set(
            value
            for key, value in _inspect.getmembers(PARAM_PVS)
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
    def top_pos(self):
        """Return slit top position [mm]."""
        return self[self.PARAM_PVS.TOP_MON]

    @property
    def bottom_pos(self):
        """Return slit bottom position [mm]."""
        return self[self.PARAM_PVS.BOTTOM_MON]

    @property
    def left_pos(self):
        """Return slit left position [mm]."""
        return self[self.PARAM_PVS.LEFT_MON]

    @property
    def right_pos(self):
        """Return slit right position [mm]."""
        return self[self.PARAM_PVS.RIGHT_MON]

    @top_pos.setter
    def top_pos(self, value):
        """Set slit top position [mm]."""
        self[self.PARAM_PVS.TOP_SP] = value

    @bottom_pos.setter
    def bottom_pos(self, value):
        """Set slit bottom position [mm]."""
        self[self.PARAM_PVS.BOTTOM_SP] = value

    @left_pos.setter
    def left_pos(self, value):
        """Set slit left position [mm]."""
        self[self.PARAM_PVS.LEFT_SP] = value

    @right_pos.setter
    def right_pos(self, value):
        """Set slit right position [mm]."""
        self[self.PARAM_PVS.RIGHT_SP] = value

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)

    def _move_slit(self, side, value, threshold, max_count, delay):
        """Moves the slit indicated by 'side' ('left', 'right', 'top', 'bottom')
        to the given value, returning True if reached, False on timeout.
        """

        if side not in ("left", "right", "top", "bottom"):
            raise ValueError(f"Invalid dide: {side}")

        attr_name = "{}_pos".format(side)

        try:
            setattr(self, attr_name, value)
        except Exception as err:
            current = getattr(self, attr_name)
            raise IOError("PUT error: pv, pos = ({})\n{}".format(current, err))

        # Check for acknowledgement. Avoid endless loop if command is not properly received.
        icount = 0
        current_value = getattr(self, attr_name)
        while abs(current_value - value) > threshold:
            _time.sleep(delay)
            current_value = getattr(self, attr_name)
            print(
                "Slit is Moving... | New pos: {:} | Curr: {:.2f} | Dif: {:}".format(
                    value, current_value, abs(current_value - value)
                ),
                end="\r",
            )
            if icount >= max_count:
                print(
                    "\nWARNING: a lâmina '{:}' não se moveu.\nPosição atual: {:.4f}".format(
                        side, current_value
                    )
                )
                return False
            icount += 1

        return True

    def _move_robust_slit(
        self, side, value, threshold, max_count, delay, trials
    ):
        """
            Tries to move the blade indicated by `side` up to `value`, repeating
            up to `trials` times if it fails, and returns True on success.

        Args:
            side : 'top', 'bottom', 'left' or 'right'
            value : target position
            threshold, max_count, delay : parameters for move_*_slit
            trials : how many times to restart the movement if it fails

        Return:
            bool : True or False
        """
        if side not in ("top", "bottom", "left", "right"):
            raise ValueError("Invalid side: {}".format(side))

        method_name = "move_{}".format(side)
        move_method = getattr(self, method_name)
        if not callable(move_method):
            raise AttributeError("Method {} not exist.".format(method_name))

        ctrials = 0
        status = False
        try:
            while ctrials < trials and not status:
                status = move_method(
                    value=value,
                    threshold=threshold,
                    max_count=max_count,
                    delay=delay,
                )
                ctrials += 1
            current_value = getattr(self, "{}_pos".format(side))
            if not status:
                raise Exception(
                    "WARNING: maximum number of trials to move {} slit reached.\nCurrent position:".format(
                        side, current_value
                    )
                )
            print("Done!")
            return True
        except Exception:
            print("Not moved!")
            return False

    def cmd_top_stop(self, timeout=None):
        """Stop Slit top motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.TOP_STOP, timeout)

    def cmd_bottom_stop(self, timeout=None):
        """Stop Slit bottom motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.BOTTOM_STOP, timeout)

    def cmd_left_stop(self, timeout=None):
        """Stop Slit left motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.LEFT_STOP, timeout)

    def cmd_right_stop(self, timeout=None):
        """Stop Slit right motor."""
        return self._cmd_motor_stop(self.PARAM_PVS.RIGHT_STOP, timeout)

    def move_top(
        self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY
    ):
        return self._move_slit(
            side="top",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
        )

    def move_bottom(
        self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY
    ):
        return self._move_slit(
            side="bottom",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
        )

    def move_left(
        self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY
    ):
        return self._move_slit(
            side="left",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
        )

    def move_right(
        self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY
    ):
        return self._move_slit(
            side="right",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
        )

    def move_robust_top(
        self,
        value,
        threshold=_THRESHOLD,
        max_count=_COUNT_LIM,
        delay=_DELAY,
        trials=_TRIALS,
    ):
        return self._move_robust_slit(
            side="top",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
            trials=trials,
        )

    def move_robust_bottom(
        self,
        value,
        threshold=_THRESHOLD,
        max_count=_COUNT_LIM,
        delay=_DELAY,
        trials=_TRIALS,
    ):
        return self._move_robust_slit(
            side="bottom",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
            trials=trials,
        )

    def move_robust_left(
        self,
        value,
        threshold=_THRESHOLD,
        max_count=_COUNT_LIM,
        delay=_DELAY,
        trials=_TRIALS,
    ):
        return self._move_robust_slit(
            side="left",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
            trials=trials,
        )

    def move_robust_right(
        self,
        value,
        threshold=_THRESHOLD,
        max_count=_COUNT_LIM,
        delay=_DELAY,
        trials=_TRIALS,
    ):
        return self._move_robust_slit(
            side="right",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
            trials=trials,
        )
