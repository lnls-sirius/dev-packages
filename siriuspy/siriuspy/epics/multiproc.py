"""."""

import multiprocessing as _mp

from epics import ca as _ca


# NOTE: I have to rederive epics.CAProcess here to ensure the process will be
# launched with the spawn method.
class CAProcessSpawn(_mp.get_context('spawn').Process):
    """
    A Channel-Access aware (and safe) subclass of multiprocessing.Process
    Use CAProcess in place of multiprocessing.Process if your Process will
    be doing CA calls!
    """
    def __init__(self, **kws):
        """."""
        super().__init__(**kws)

    def run(self):
        """."""
        _ca.initial_context = None
        _ca.clear_cache()
        super().run()
