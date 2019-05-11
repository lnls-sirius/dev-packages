"Definition of thread classes to used across the package."
import time as _time
from threading import Thread as _Thread
from threading import Event as _Event
from threading import Lock as _Lock
from queue import Queue as _Queue
from collections import deque as _deque
# NOTE: QueueThread was reported as generating unstable behaviour
# when used intensively in the SOFB IOC.
# TODO: investigate this issue!


class QueueThread(_Thread):
    """Callback queue class.

        Queues threads of this class are used to process callbacks of power
    supplies (magnets) properties among others.
    """

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

    def add_callback(self, func, *args, **kwargs):
        """Add callback."""
        self._queue.put((func, args, kwargs))

    def run(self):
        """Run method."""
        self._running = True
        while self.running:
            func_item = self._queue.get()
            # print(queue_size)
            n = self._queue.qsize()
            if n and n % 500 == 0:
                print("Warning: ComputedPV Queue size is {}!".format(n))
            function, args, kwargs = func_item
            # print(args[0])
            function(*args, **kwargs)  # run the show!

    def stop(self):
        """Stop queue thread."""
        self._running = False


class RepeaterThread(_Thread):
    """Repeat execution of predefined function for a given number of times."""

    def __init__(self, interval, function, args=tuple(),
                 kwargs=dict(), niter=0):
        """Init method.

        Inputs:
        - interval: time to wait between sucessive calls to method.
        - function: method to be executed.
        - args: tuple of positional arguments of method
        - kwargs: dictionary with keyword arguments of method.
        - niter: number of times to execute method. If niter is zero or None
            it will be executed indefinetly until stop is called.
        """
        super().__init__(daemon=True)
        self.interval = interval
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
        self._unpaused.wait()
        self.function(*self.args, **self.kwargs)
        dt = 0.0
        while ((not self._stopped.wait(self.interval - dt)) and
               (not self.niters or self.niters > self.cur_iter)):
            self._unpaused.wait()
            if self._stopped.is_set():
                break
            self.cur_iter += 1
            t0 = _time.time()
            self.function(*self.args, **self.kwargs)
            dt = _time.time() - t0

    def reset(self):
        """Reset count."""
        self.cur_iter = 0

    def pause(self):
        self._unpaused.clear()

    def resume(self):
        self._unpaused.set()

    def unpause(self):
        self.resume()

    def is_paused(self):
        return not self._unpaused.is_set()

    def isPaused(self):
        return self.is_paused()

    def stop(self):
        """Stop execution."""
        self._unpaused.set()
        self._stopped.set()


class DequeThread(_deque):
    """DequeThread.

    This class manages generic operations (actions) using an append-right,
    pop-left queue. Each operation processing is a method invoked as a separate
    thread.
    """
    def __init__(self):
        """Init."""
        super().__init__()
        self._thread = None
        self._ignore = False
        self._enabled = True
        self._lock = _Lock()

    @property
    def last_operation(self):
        """Return last operation."""
        return self._last_operation

    @property
    def enabled(self):
        """Enable process."""
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

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
                return False
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
        donothing = not self._enabled
        donothing |= self._thread is not None and self._thread.is_alive()
        if donothing:
            return False

        # no thread is running, we can process queue
        try:
            operation = self.popleft()
        except IndexError:
            # there is nothing in the queue
            return False
        # process operation taken from queue
        args = tuple()
        kws = dict()
        if len(operation) == 1:
            func = operation[0]
        elif len(operation) == 2:
            func, args = operation
        elif len(operation) >= 3:
            func, args, kws = operation[:3]
        self._thread = _Thread(target=func, args=args, kwargs=kws, daemon=True)
        self._thread.start()
        return True
