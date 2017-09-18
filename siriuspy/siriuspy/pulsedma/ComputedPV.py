"""Definition of ComputedPV class that simulates a PV composed of epics PVs."""
from epics import get_pv
from threading import Thread


class ComputedPV:
    """Simulates an epics PV object."""

    def __init__(self, pvname, computer, *pvs):
        """Initialize PVs."""
        # ComputedPV properties
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
        # Object that know how to compute the PV props based on the PV list
        self.computer = computer
        # Thread used to update values, thus letting the callback return
        self._thread = None
        self._callback = None
        # Get pvs
        for pv in pvs:
            self.pvs.append(get_pv(pv))
        # Add callback
        for pv in self.pvs:
            pv.add_callback(self._value_update_callback)
        # Wait
        # for pv in self.pvs:
        #     print("Waiting for connection to {}".format(pv))
        #     pv.wait_for_connection(timeout=1e-3)

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
        # values = [pv.get() for pv in self.pvs]
        # new_val = self.computer.compute_put(value, *values)
        # print(new_val)
        # self.pvs[0].put(new_val)
        self.computer.compute_put(value, *self.pvs)

    def add_callback(self, func):
        """Add callback to computed PV."""
        self._callback = func

    def wait_for_connection(self, timeout):
        """Wait util computed PV is connected or until timeout."""
        pass

    def _update_value(self, updated_pv):
        # Get dict with pv props that changed
        kwargs = self.computer.compute_get(self, updated_pv, *self.pvs)

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
        # self.values[pvname] = value
        if self.connected:
            # Update value in a thread, this way callback can finish
            self._thread = Thread(target=self._update_value, args=[pvname, ])
            self._thread.start()

    def _issue_callback(self, **kwargs):
        if self._callback is not None:
            self._callback(**kwargs)
