"""Definition of thread classes to used across the package."""

import time as _time
from threading import Thread as _Thread, Event as _Event, \
    Lock as _Lock
from queue import Queue as _Queue, Empty as _Empty, Full as _Full

from epics.ca import use_initial_context as _use_initial_context

from .epics import CAThread as _CAThread


class AsyncWorker(_Thread):
    """Asynchronous Worker Thread.

    Performs asynchronous jobs indefinitely.
    """

    def __init__(self, name=None, is_cathread=False):
        """."""
        super().__init__(name=name, daemon=True)
        self.is_cathread = is_cathread
        self._evt_received = _Event()
        self._evt_ready = _Event()
        self._evt_ready.set()
        self._evt_stop = _Event()
        self.target = None
        self.args = tuple()

    def configure_new_run(self, target, args=None):
        """Configure a new run of the thread."""
        if not self._evt_ready.is_set():
            return False
        self.target = target
        self.args = args or tuple()
        self._evt_ready.clear()
        # NOTE: _evt_received setting must be last operation of this method.
        self._evt_received.set()
        return True

    def wait_ready(self, timeout=None):
        """Wait until last run is finished."""
        self._evt_ready.wait(timeout=timeout)

    def is_ready(self):
        """Check if last run has finished."""
        return self._evt_ready.is_set()

    def stop(self):
        """Stop thread."""
        self._evt_stop.set()

    def run(self):
        """."""
        if self.is_cathread:
            _use_initial_context()
        while not self._evt_stop.is_set():
            if self._evt_received.wait(0.5):
                self._evt_received.clear()
                self.target(*self.args)
                self._evt_ready.set()


class RepeaterThread(_Thread):
    """Repeat execution of predefined function for a given number of times."""

    def __init__(
            self, interval, function, args=None, kwargs=None, niter=0,
            is_cathread=False):
        """Init method.

        Inputs:
        - interval: time to wait between sucessive calls to method.
        - function: method to be executed.
        - args: tuple of positional arguments of method
        - kwargs: dictionary with keyword arguments of method.
        - niter: number of times to execute method. If niter is zero or None
            it will be executed indefinetly until stop is called.
        - whether to use CAThread logic .
        """
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()
        super().__init__(daemon=True)
        self.is_cathread = is_cathread
        self.interval = interval
        if not hasattr(function, '__call__'):
            raise TypeError('Argument "function" is not callable.')
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.niters = niter
        self.cur_iter = 0
        self._stopped = _Event()
        self._unpaused = _Event()
        self._unpaused.set()

    def run(self):
        """Run method."""
        if self.is_cathread:
            _use_initial_context()

        self._unpaused.wait()
        self.function(*self.args, **self.kwargs)
        dtime = 0.0
        while ((not self._stopped.wait(self.interval - dtime)) and
               (not self.niters or self.niters > self.cur_iter)):
            self._unpaused.wait()
            if self._stopped.is_set():
                break
            self.cur_iter += 1
            _t0 = _time.time()
            self.function(*self.args, **self.kwargs)
            dtime = _time.time() - _t0

    def reset(self):
        """Reset count."""
        self.cur_iter = 0

    def pause(self):
        """."""
        self._unpaused.clear()

    def resume(self):
        """."""
        self._unpaused.set()

    def unpause(self):
        """."""
        self.resume()

    def is_paused(self):
        """."""
        return not self._unpaused.is_set()

    def isPaused(self):
        """."""
        return self.is_paused()

    def stop(self):
        """Stop execution."""
        self._unpaused.set()
        self._stopped.set()


class QueueThread(_Queue):
    """QueueThread.

    This class manages generic operations (actions) using a FIFO queue. Each
    operation processing is a method invoked as a separate thread. It also has
    process loop methods to continuously process its operation queue in a
    single thread.
    """

    def __init__(self, is_cathread=False):
        """Init."""
        super().__init__()
        self.is_cathread = is_cathread
        self._last_operation = None
        self._pth = None
        self._lth = None
        self._loop_stop_evt = _Event()
        self._changing_queue = _Lock()

    @property
    def last_operation(self):
        """Return last operation."""
        return self._last_operation

    @property
    def loop_running(self):
        """."""
        return self._lth is not None and self._lth.is_alive()

    @property
    def process_running(self):
        """."""
        return self._pth is not None and self._pth.is_alive()

    def put(self, operation, block=True, timeout=None, unique=False):
        """Put operation to queue."""
        if not hasattr(operation, '__len__'):
            operation = (operation, )
        if not hasattr(operation[0], '__call__'):
            raise TypeError(
                'First element of "operation" is not callable.')

        with self._changing_queue:
            # NOTE: the self.queue attribute is not in the documentation of
            # the class Queue. I am not sure if they will keep this reference
            # in the future, or maybe make it a hidden attribute.
            if unique and self.queue.count(operation) > 0:
                return False
            try:
                super().put(operation, block=block, timeout=timeout)
            except _Full:
                return False
            self._last_operation = operation
        return True

    def get(self, block=True, timeout=None):
        """Get operation from queue."""
        with self._changing_queue:
            try:
                return super().get(block=block, timeout=timeout)
            except _Empty:
                return None

    def process(self, block=True, timeout=None):
        """Process operation from queue."""
        with self._changing_queue:
            # first check if a thread is already running
            if self.process_running:
                return False
            # no thread is running, we can process queue
            try:
                func, args, kws = self._get_operation(block, timeout)
            except _Empty:
                return False
            th_cls = _CAThread if self.is_cathread else _Thread
            self._pth = th_cls(target=func, args=args, kwargs=kws, daemon=True)
            self._pth.start()
            return True

    def loop_run(self):
        """Run deque process loop."""
        # check if there is a previously running loop
        self._loop_stop_evt.clear()
        if self.loop_running:
            return
        # start new process loop
        th_cls = _CAThread if self.is_cathread else _Thread
        self._lth = th_cls(target=self._loop_run_process, daemon=True)
        self._lth.start()

    def loop_stop(self):
        """Stop deque process loop."""
        self._loop_stop_evt.set()

    def _loop_run_process(self):
        while not self._loop_stop_evt.is_set():
            try:
                func, args, kws = self._get_operation(True, timeout=1)
                func(*args, **kws)
            except _Empty:
                continue
        self._loop_stop_evt.clear()

    def _get_operation(self, block=True, timeout=None):
        """Raise queue.Empty exception in case of timeout or empty Queue."""
        operation = super().get(block=block, timeout=timeout)
        # process operation taken from queue
        args, kws = tuple(), dict()
        if len(operation) == 1:
            func = operation[0]
        elif len(operation) == 2:
            func, args = operation
        elif len(operation) >= 3:
            func, args, kws = operation[:3]
        return func, args, kws
