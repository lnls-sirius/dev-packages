"""Definition of ComputedPV class that simulates a PV composed of epics PVs."""
from epics import get_pv
from threading import Thread
import time as _time


class MyThread(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self._funcs = []
        self.running = False

    def add_callback(self, func, pvname, value):
        self._funcs.append((func, [pvname, value]))

    def run(self):
        self.running = True
        while True:
            if self._funcs:
                self._funcs[0][0](*self._funcs[0][1])
                self._funcs.pop(0)
            else:
                _time.sleep(0.1)


class ComputedPV:
    """Simulates an epics PV object."""

    thread = MyThread()

    def __init__(self, pvname, computer, *pvs):
        """Initialize PVs."""
        # ComputedPV properties
        if not ComputedPV.thread.running:
            ComputedPV.thread.start()
        self.value = None
        self.upper_warning_limit = None
        self.lower_warning_limit = None
        self.upper_alarm_limit = None
        self.lower_alarm_limit = None
        self.upper_disp_limit = None
        self.lower_disp_limit = None

        self.pvname = pvname
        # List with PVs used by the computed PV
        self.pvs = list()
        # self.pvs = dict()
        # Object that know how to compute the PV props based on the PV list
        self.computer = computer
        # Thread used to update values, thus letting the callback return
        self._thread = None
        self._callbacks = []
        # Get pvs
        for pv in pvs:
            if isinstance(pv, str):
                self.pvs.append(get_pv(pv))
            else:
                self.pvs.append(pv)
            # self.pvs[pv] = get_pv(pv)
        # Add callback
        for pv in self.pvs:
            pv.add_callback(self._value_update_callback)
        # Init limits
        if self.connected:
            self.computer.compute_limits(self)
        # Wait
        # for pv in self.pvs:
        #     print("Waiting for connection to {}".format(pv))
        #     pv.wait_for_connection(timeout=1e-3)

    # Public interface
    @property
    def connected(self):
        """Return wether all pvs are connected."""
        for pv in self.pvs:
            if not pv.connected:
                return False
        return True

    def get(self):
        """Return current value of computed PV."""
        return self.value

    def put(self, value):
        """Put `value` to the first pv of the pv list."""
        self.value = value
        self.computer.compute_put(self, value)

    def add_callback(self, func):
        """Add callback to computed PV."""
        self._callbacks.append(func)
        return len(self._callbacks) - 1

    def wait_for_connection(self, timeout):
        """Wait util computed PV is connected or until timeout."""
        pass

    # Private methods
    def _update_value(self, pvname, value):
        # Get dict with pv props that changed
        kwargs = self.computer.compute_update(self, pvname, value)

        if kwargs is not None:
            self.value = kwargs["value"]
            # Check if limits are in the return dict and update them
            if "high" in kwargs:
                self.upper_warning_limit = kwargs["high"]
                self.lower_warning_limit = kwargs["low"]
                self.upper_alarm_limit = kwargs["hihi"]
                self.lower_alarm_limit = kwargs["lolo"]
                self.upper_disp_limit = kwargs["hilim"]
                self.lower_disp_limit = kwargs["lolim"]

            self._issue_callback(pvname=self.pvname, **kwargs)

    def _value_update_callback(self, pvname, value, **kwargs):
        if self.connected:
            # Update value in a thread, this way callback can finish
            # self._thread = Thread(target=self._update_value,
            #                       args=[pvname, value])
            # self._thread.start()
            ComputedPV.thread.add_callback(self._update_value, pvname, value)

    def _issue_callback(self, **kwargs):
        if self._callbacks:
            for cb in self._callbacks:
                cb(**kwargs)
