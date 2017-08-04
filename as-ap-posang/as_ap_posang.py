"""AS-AP-PosAng IOC."""

import sys as _sys
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import pvs as _pvs
import signal as _signal
import main as _main
from siriuspy import util as _util


INTERVAL = 0.1
stop_event = False


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
        if self.app.write(reason, value):
            super().write(reason, value)
        else:
            return False


def run():
    """Main module function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    # for prefix, database in _main.App.pvs_database.items():
    #     server.createPV(prefix, database)
    server.createPV(_pvs._PREFIX, _main.App.pvs_database)
    pcas_driver = _PCASDriver()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
