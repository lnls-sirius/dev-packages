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


