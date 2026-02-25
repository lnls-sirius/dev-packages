"""Slit Control."""

# import inspect as _inspect
import time as _time
from types import SimpleNamespace as _SimpleNamespace

from ..device import Device as _Device


class _PVNames(_SimpleNamespace):
    def __getattr__(self, name):
        """."""
        return None


class SlitBase(_Device):
    """Base Slit device."""

    _DEFAULT_MOTOR_TIMEOUT = 2.0  # [s]
    _THRESHOLD = 0.01  # [mm]
    _COUNT_LIM = 8
    _DELAY = 4  # [s]
    _TRIALS = 3

    # --- PVS ---
    PVS = _PVNames()

    PROPERTIES_DEFAULT = tuple(set(value for key, value in vars(PVS).items()))

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        # check if device exists
        if devname not in self.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init, **kwargs)

    @property
    def top_pos(self):
        """Return slit top position [mm]."""
        return self[self.PVS.TOP_MON]

    @property
    def bottom_pos(self):
        """Return slit bottom position [mm]."""
        return self[self.PVS.BOTTOM_MON]

    @property
    def left_pos(self):
        """Return slit left position [mm]."""
        return self[self.PVS.LEFT_MON]

    @property
    def right_pos(self):
        """Return slit right position [mm]."""
        return self[self.PVS.RIGHT_MON]

    @top_pos.setter
    def top_pos(self, value):
        """Set slit top position [mm]."""
        self[self.PVS.TOP_SP] = value

    @bottom_pos.setter
    def bottom_pos(self, value):
        """Set slit bottom position [mm]."""
        self[self.PVS.BOTTOM_SP] = value

    @left_pos.setter
    def left_pos(self, value):
        """Set slit left position [mm]."""
        self[self.PVS.LEFT_SP] = value

    @right_pos.setter
    def right_pos(self, value):
        """Set slit right position [mm]."""
        self[self.PVS.RIGHT_SP] = value

    def _cmd_motor_stop(self, propty, timeout):
        timeout = self._DEFAULT_MOTOR_TIMEOUT if timeout is None else timeout
        self[propty] = 1
        return self._wait(propty, 0, timeout=timeout)

    def _move_slit(self, side, value, threshold, max_count, delay):
        """Moves the slit indicated by 'side'.

        Side is one of ('left', 'right', 'top', 'bottom')
        to the given value, returning True if reached, False on timeout.
        """
        if side not in ("left", "right", "top", "bottom"):
            raise ValueError(f"Invalid dide: {side}")

        attr_name = "{}_pos".format(side)

        try:
            setattr(self, attr_name, value)
        except Exception as err:
            current = getattr(self, attr_name)
            raise IOError(f"PUT error: pv, pos = ({current})\n{err}") from err

        # Check for acknowledgement. Avoid endless loop if command
        # is not properly received.
        icount = 0
        current_value = getattr(self, attr_name)
        while abs(current_value - value) > threshold:
            _time.sleep(delay)
            current_value = getattr(self, attr_name)
            print(
                f"Slit is Moving... | New pos: {value}"
                f" | Curr: {current_value:.2f}"
                f" | Dif: {abs(current_value - value)}",
                end="\r",
            )
            if icount >= max_count:
                print(
                    f"\nWARNING: a lâmina '{side}' não se moveu."
                    f"\nPosição atual: {current_value:.4f}"
                )
                return False
            icount += 1

        return True

    def _move_robust_slit(
        self, side, value, threshold, max_count, delay, trials
    ):
        """Tries to move the blade indicated by `side` up to `value`.

        Repeat up to `trials` times if it fails, and returns True on success.

        Args:
            side : 'top', 'bottom', 'left' or 'right'
            value : target position.
            threshold: parameters for move_*_slit
            max_count: parameters for move_*_slit
            delay : parameters for move_*_slit
            trials : how many times to restart the movement if it fails

        Returns:
            bool : True or False.
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
                    f"WARNING: maximum number of trials to move {side}"
                    f" slit reached. \nCurrent position: {current_value}"
                )
            print("Done!")
            return True
        except Exception:
            print("Not moved!")
            return False

    def cmd_top_stop(self, timeout=None):
        """Stop Slit top motor."""
        return self._cmd_motor_stop(self.PVS.TOP_STOP, timeout)

    def cmd_bottom_stop(self, timeout=None):
        """Stop Slit bottom motor."""
        return self._cmd_motor_stop(self.PVS.BOTTOM_STOP, timeout)

    def cmd_left_stop(self, timeout=None):
        """Stop Slit left motor."""
        return self._cmd_motor_stop(self.PVS.LEFT_STOP, timeout)

    def cmd_right_stop(self, timeout=None):
        """Stop Slit right motor."""
        return self._cmd_motor_stop(self.PVS.RIGHT_STOP, timeout)

    def move_top(
        self, value, threshold=_THRESHOLD, max_count=_COUNT_LIM, delay=_DELAY
    ):
        """."""
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
        """."""
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
        """."""
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
        """."""
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
        """."""
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
        """."""
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
        """."""
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
        """."""
        return self._move_robust_slit(
            side="right",
            value=value,
            threshold=threshold,
            max_count=max_count,
            delay=delay,
            trials=trials,
        )


class CAXSlit(SlitBase):
    """."""

    class DEVICES:
        """Devices names."""

        CAX_A1 = "CAX:A:PP02"  # WBS1
        CAX_B1 = "CAX:B:PP01"  # WBS2

        ALL = (CAX_A1, CAX_B1)

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        super().__init__(devname, props2init, **kwargs)

        self.PVS.TOP_SP      = "A.VAL"
        self.PVS.TOP_RB      = "A.VAL"   # That doesn't have a RB PV
        self.PVS.TOP_MON     = "A.RBV"   # RBV is not the pv of readback
        self.PVS.TOP_STOP    = "A.STOP"

        self.PVS.BOTTOM_SP   = "B.VAL"
        self.PVS.BOTTOM_RB   = "B.VAL"   # That doesn't have a RB PV
        self.PVS.BOTTOM_MON  = "B.RBV"   # RBV is not the pv of readback
        self.PVS.BOTTOM_STOP = "B.STOP"

        self.PVS.LEFT_SP     = "C.VAL"
        self.PVS.LEFT_RB     = "C.VAL"   # That doesn't have a RB PV
        self.PVS.LEFT_MON    = "C.RBV"   # RBV is not the pv of readback
        self.PVS.LEFT_STOP   = "C.STOP"

        self.PVS.RIGHT_SP    = "D.VAL"
        self.PVS.RIGHT_RB    = "D.VAL"   # That doesn't have a RB PV
        self.PVS.RIGHT_MON   = "D.RBV"   # RBV is not the pv of readback
        self.PVS.RIGHT_STOP  = "D.STOP"

        self.PROPERTIES_DEFAULT = tuple(
            set(value for key, value in vars(self.PVS).items())
        )
