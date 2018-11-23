"""AS-MA IOC Module."""

import os as _os
import sys as _sys
import signal as _signal
import logging as _log

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
import as_ma.pvs as _pvs
import as_ma.main as _main


INTERVAL = 0.1
stop_event = False


def _stop_now(signum, frame):
    global stop_event
    _log.warning(_signal.Signals(signum).name +
                 ' received at ' + _util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self):
        super().__init__()
        self.app = _main.App(self)

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            val = super().read(reason)
            return val
        else:
            return value

    def write(self, reason, value):
        self.app.write(reason, value)


def run(manames):
    """Implement main module function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file()

    # define IOC and initializes it
    # _pvs.select_ioc(manames)
    _main.App.init_class(manames)

    # check if IOC is already running
    pvname = _pvs._PREFIX_VACA + next(iter(_main.App.pvs_database.keys()))
    running = _util.check_pv_online(
        pvname=pvname, use_prefix=False, timeout=0.5)
    if running:
        _log.warning(
            'Another IOC providing "' + pvname + '"is already running!')
        return

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    # for prefix, database in _main.App.pvs_database.items():
    #     server.createPV(prefix, database)
    db = _main.App.pvs_database
    _attribute_access_security_group(server, db)
    server.createPV(_pvs._PREFIX_VACA, db)
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
