"""Definition of thread classes to used across the package."""

import time as _time
from threading import Thread as _Thread, Event as _Event, \
    Lock as _Lock
from queue import Queue as _Queue
from collections import deque as _deque

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


class QueueThread(_Thread):
    """Callback queue class."""

    # NOTE: QueueThread was reported as generating unstable behaviour
    # when used intensively in the SOFB IOC. Currently this class is
    # used in as-ps-diag IOC classes.
    # TODO: investigate this issue!

    def __init__(self, is_cathread=False):
        """Init method."""
        super().__init__(daemon=True)
        self.is_cathread = is_cathread
        self._queue = _Queue()
        self._running = False

    @property
    def running(self):
        """Return whether thread is running."""
        return self._running

    def add_callback(self, func, *args, **kwargs):
        """Add callback."""
        if not hasattr(func, '__call__'):
            raise TypeError('Argument "func" is not callable.')
        self._queue.put((func, args, kwargs))

    def run(self):
        """Run method."""
        if self.is_cathread:
            _use_initial_context()
        self._running = True
        while self.running:
            func_item = self._queue.get()
            nitems = self._queue.qsize()
            if nitems and nitems % 500 == 0:
                print("Warning: Queue size is {}!".format(nitems))
            function, args, kwargs = func_item
            function(*args, **kwargs)  # run the show!

    def stop(self):
        """Stop queue thread."""
        self._running = False


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


class DequeThread(_deque):
    """DequeThread.

    This class manages generic operations (actions) using an append-right,
    pop-left queue. Each operation processing is a method invoked as a separate
    thread. It also has process loop methods to continuously process its
    operation queue.
    """

    DEF_LOOP_INTERVAL = 0.1  # [s]
    SMALL_SLEEP_TIME = 0.1  # [s]

    def __init__(self, loop_interval=None, is_cathread=False):
        """Init."""
        super().__init__()
        loop_interval = loop_interval if loop_interval is not None else \
            self.DEF_LOOP_INTERVAL
        self.is_cathread = is_cathread
        self._last_operation = None
        self._process_thread = None
        self._ignore = False
        self._loop_thread = None
        self._loop_stop_evt = _Event()
        self._loop_interval = loop_interval
        self._loop_is_running = False
        self._lock = _Lock()

    @property
    def last_operation(self):
        """Return last operation."""
        return self._last_operation

    @property
    def running(self):
        """."""
        return self._loop_is_running

    @property
    def interval(self):
        """Return loop process interval."""
        return self._loop_interval

    @interval.setter
    def interval(self, value):
        """Set loop process interval."""
        self._loop_interval = max(0, value)

    def ignore_set(self):
        """Turn ignore state on."""
        self._ignore = True

    def ignore_clear(self):
        """Turn ignore state on."""
        self._ignore = False

    def append(self, operation, unique=False):
        """Append operation to queue."""
        with self._lock:
            if self._ignore or (unique and self.count(operation) > 0):
                return False

            if not hasattr(operation, '__len__'):
                operation = (operation, )
            if not hasattr(operation[0], '__call__'):
                raise TypeError(
                    'First element of "operation" is not callable.')
            super().append(operation)
            self._last_operation = operation
            return True

    def clear(self):
        """Clear deque."""
        with self._lock:
            super().clear()

    def pop(self):
        """Pop operation from queue."""
        with self._lock:
            return super().pop()

    def popleft(self):
        """Pop left operation from queue."""
        with self._lock:
            return super().popleft()

    def process(self):
        """Process operation from queue."""
        # first check if a thread is already running
        with self._lock:
            donothing = \
                self._process_thread is not None and \
                self._process_thread.is_alive()
            if donothing:
                return False

            # no thread is running, we can process queue
            try:
                operation = super().popleft()
            except IndexError:
                # there is nothing in the queue
                return False
            # process operation taken from queue
            args, kws = tuple(), dict()
            if len(operation) == 1:
                func = operation[0]
            elif len(operation) == 2:
                func, args = operation
            elif len(operation) >= 3:
                func, args, kws = operation[:3]

            _thread_class = _Thread
            if self.is_cathread:
                _thread_class = _CAThread

            self._process_thread = _thread_class(
                target=func, args=args, kwargs=kws, daemon=True)
            self._process_thread.start()
            return True

    def run(self, interval=None):
        """Run deque process loop."""
        if interval is not None:
            self.interval = interval

        # check if there is a previously running loop
        self._loop_stop_evt.clear()
        while self._loop_thread is not None and self._loop_thread.is_alive():
            return

        # start new process loop
        _thread_class = _Thread
        if self.is_cathread:
            _thread_class = _CAThread
        self._loop_thread = _thread_class(
            target=self._loop_run_process, daemon=True)
        self._loop_thread.start()

    def stop(self):
        """Stop deque process loop."""
        self._loop_stop_evt.set()

    def _loop_run_process(self):
        while not self._loop_stop_evt.is_set():
            self._loop_is_running = True
            self.process()
            t0 = _time.time()
            while _time.time() - t0 < self._loop_interval:
                sleep_time = \
                    min(DequeThread.SMALL_SLEEP_TIME, self._loop_interval)
                _time.sleep(sleep_time)
        self._loop_is_running = False
        self._loop_stop_evt.clear()
