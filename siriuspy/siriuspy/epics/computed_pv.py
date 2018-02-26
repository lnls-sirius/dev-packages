"""Definition of ComputedPV class that simulates a PV composed of epics PVs."""
from threading import Thread as _Thread
from queue import Queue as _Queue
from epics import get_pv as _get_pv
from siriuspy.epics import connection_timeout as _connection_timeout


class QueueThread(_Thread):
    """Callback queue class."""

    def __init__(self):
        """Init method."""
        super().__init__(daemon=True)
        # self._queue = []
        self._queue = _Queue()
        self._running = False

    @property
    def running(self):
        """Return whether thread is running."""
        return self._running

    def add_callback(self, func, pvname, value):
        """Add callback."""
        self._queue.put((func, [pvname, value]))

    def run(self):
        """Run method."""
        self._running = True
        while self.running:
            func_item = self._queue.get()
            # print(queue_size)
            n = self._queue.qsize()
            if n and n % 500 == 0:
                print("Warning: ComputedPV Queue size is {}!".format(n))
            function, args = func_item
            # print(args[0])
            function(*args)  # run the show!

    def stop(self):
        """Stop queue thread."""
        self._running = False


class ComputedPV:
    """Simulates an epics PV object."""

    def __init__(self, pvname, computer, queue, *pvs):
        """Initialize PVs."""
        # computedPV properties
        self._queue = queue
        if not self._queue.running:
            self._queue.start()
        self.value = None
        self.upper_alarm_limit = None
        self.upper_warning_limit = None
        self.upper_disp_limit = None
        self.lower_disp_limit = None
        self.lower_warning_limit = None
        self.lower_alarm_limit = None

        self.pvname = pvname
        # object that know how to compute the PV props based on the PV list
        self.computer = computer
        # thread used to update values, thus letting the callback return
        self._callbacks = []
        # get pvs
        self.pvs = list()  # List with PVs used by the computed PV
        for pv in pvs:
            if isinstance(pv, str):  # give up string option.
                tpv = _get_pv(pv, connection_timeout=_connection_timeout)
                self.pvs.append(tpv)
            else:
                self.pvs.append(pv)
        # add callback
        for pv in self.pvs:
            pv.add_callback(self._value_update_callback)

        # init limits
        if self.connected:
            # print('connected')
            lims = self.computer.compute_limits(self)
            self.upper_alarm_limit = lims[0]
            self.upper_warning_limit = lims[1]
            self.upper_disp_limit = lims[2]
            self.lower_disp_limit = lims[3]
            self.lower_warning_limit = lims[4]
            self.lower_alarm_limit = lims[5]

        for pv in self.pvs:
            pv.run_callbacks()

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

    def run_callbacks(self):
        """Run all callbacks."""
        self._issue_callback(**{
            'pvname': self.pvname,
            'value': self.value,
            'high': self.upper_warning_limit,
            'low': self.lower_warning_limit,
            'hihi': self.upper_alarm_limit,
            'lolo': self.lower_alarm_limit,
            'hilim': self.upper_disp_limit,
            'lolim': self.lower_disp_limit})

    def wait_for_connection(self, timeout):
        """Wait util computed PV is connected or until timeout."""
        pass

    # Private methods
    def _update_value(self, pvname, value):
        # Get dict with pv props that changed
        # print('update_value')
        kwargs = self.computer.compute_update(self, pvname, value)

        if kwargs is not None:
            self.value = kwargs["value"]
            # Check if limits are in the return dict and update them
            if "high" in kwargs:
                # print('set_limits')
                self.upper_alarm_limit = kwargs["hihi"]
                self.upper_warning_limit = kwargs["high"]
                self.upper_disp_limit = kwargs["hilim"]
                self.lower_disp_limit = kwargs["lolim"]
                self.lower_warning_limit = kwargs["low"]
                self.lower_alarm_limit = kwargs["lolo"]
                # print('upper_alarm_limit:', self.upper_alarm_limit)
                # print()

            self._issue_callback(pvname=self.pvname, **kwargs)

    def _value_update_callback(self, pvname, value, **kwargs):
        if self.connected:
            if pvname == self.pvs[0].pvname:
                # add update_callback to queuethread only if updated_pv_name
                # corresponds to the main magnet current, which is always the
                # first PV in the list.
                self._queue.add_callback(self._update_value,
                                         pvname, value)

    def _issue_callback(self, **kwargs):
        if self._callbacks:
            for cb in self._callbacks:
                cb(**kwargs)
