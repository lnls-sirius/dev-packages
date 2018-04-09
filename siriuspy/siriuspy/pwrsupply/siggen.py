"""Test module."""
import time as _t


class Trapezoidal:
    """Trapezoidal signal."""

    def __init__(self, n, a, o, aux):
        """Signal parameters."""
        self.n = n
        self.a = a
        self.o = o
        # times
        self.up = aux[0]
        self.plateau = aux[1]
        self.down = aux[2]
        self._check()
        self.cycle_time = self.up + self.plateau + self.down
        self.enable = True
        self.init = _t.time()
        self.last_delta = self.init

    def duration(self):
        """Return total duration. Zero is infinite time."""
        return self.cycle_time * self.n

    def get_value(self):
        """Return current signal value."""
        if self.enable:
            self.last_delta = _t.time() - self.init
        return self._get_value(self.last_delta)

    def _get_value(self, delta):
        if self.duration() > 0 and delta > self.duration():
            self.enable = False
            return self.o
        else:
            cycle_pos = delta % self.cycle_time
            target = self.o + self.a
            if cycle_pos < self.up:
                return self.o + (cycle_pos/self.up)*(target - self.o)
            elif cycle_pos < (self.up + self.plateau):
                return target
            else:
                down_time = cycle_pos - (self.up + self.plateau)
                return target - (down_time / self.down)*(target - self.o)

    def _check(self):
        if self.up == 0:
            self.up = 0.1
        if self.plateau == 0:
            self.plateau = 0.1
        if self.down == 0:
            self.down = 0.1
