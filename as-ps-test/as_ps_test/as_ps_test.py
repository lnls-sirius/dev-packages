"""PS Test IOC."""

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import signal as _signal
import as_ps_test.main as _main
import siriuspy.util as _util
import sys as _sys

INTERVAL = 0.1
stop_event = False  # _multiprocessing.Event()


def _stop_now(signum, frame):
    global stop_event
    signames = _util.get_signal_names()
    print(signames[signum] + ' received at ' + _util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    stop_event = True


class _PCASDriver(_pcaspy.Driver):

    def __init__(self):
        super().__init__()
        self.app = _main.App(self)

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        return self.app.write(reason, value)


def run():
    """Main function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # define IOC and initializes it
    _main.App.init_class()

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    for prefix, database in _main.App.get_pvs_database().items():
        server.createPV(prefix, database)
    pcas_driver = _PCASDriver()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    print('exiting...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
