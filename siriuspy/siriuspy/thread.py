"Definition of thread classes to used across the package."
from threading import Thread as _Thread
from threading import Event as _Event
from queue import Queue as _Queue

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
    """Repeat execution of predefined function for a given number of time."""

    def __init__(self, interval, function, args=tuple(), kwargs=dict(), niter=100):
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
        self.stopped = _Event()

    def run(self):
        """Run method."""
        self.function(*self.args, **self.kwargs)
        while ((not self.stopped.wait(self.interval)) and
               (not self.niters or self.niters > self.cur_iter)):
            self.cur_iter += 1
            self.function(*self.args, **self.kwargs)

    def reset(self):
        """Reset count."""
        self.cur_iter = 0

    def stop(self):
        """Stop execution."""
        self.stopped.set()
