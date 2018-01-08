"""PS Test IOC."""

import sys as _sys
import signal as _signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import siriuspy.util as _util
import as_ps_test.main as _main
import as_ps_test.pvs as _pvs

INTERVAL = 0.1
stop_event = False  # _multiprocessing.Event()


def _stop_now(signum, frame):
    global stop_event
    print(_signal.Signals(signum).name + ' received at ' +
          _util.get_timestamp())
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

    # check if IOC is already running
    p = next(iter(_main.App.pvs_database.keys()))
    pvname = _pvs._PREFIX + next(iter(_main.App.pvs_database[p].keys()))
    running = _util.check_pv_online(
        pvname=pvname, use_prefix=False, timeout=0.5)
    if running:
        print('Another PS IOC is already running!')
        return

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
