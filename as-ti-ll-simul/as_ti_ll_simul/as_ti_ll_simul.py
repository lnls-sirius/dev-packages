"""IOC Module."""

import os as _os
import uuid as _uuid
import sys as _sys
import time as _time
import logging as _log
import signal as _signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from siriuspy import util as _util
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.timesys.time_simul import TimingSimulation

__version__ = _util.get_last_commit_hash()
INTERVAL = 0.1
RFFREQ = 500000000
stop_event = False


def _stop_now(signum, frame):
    _log.info('SIGINT received')
    global stop_event
    stop_event = True


def _print_pvs_in_file(db, fname):
    with open('pvs/' + fname, 'w') as f:
        for key in sorted(db.keys()):
            f.write(PREFIX+'{0:40s}\n'.format(key))
    _log.info(fname+' file generated with {0:d} pvs.'.format(len(db)))


def _attribute_acces_security_group(db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})


class _Driver(_pcaspy.Driver):

    def __init__(self):
        super().__init__()

    def write(self, reason, value):
        app_ret = self.app.write(reason, value)
        if app_ret:
            self.setParam(reason, value)
            self.updatePVs()
            _log.info('{0:40s}: OK'.format(reason))
        else:
            _log.info('{0:40s}: not OK'.format(reason))
        return app_ret


class App:
    """Main Class of the IOC Logic."""

    @staticmethod
    def get_database():
        """Get the database."""
        return TimingSimulation.get_database()

    def __init__(self, driver=None):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        events : define if this app will manage events;
        clocks_evg : define if this app will manage clocks and evg.
        """
        _log.info('Starting App...')
        self.driver = driver
        self.uuid = _uuid.uuid4()
        self.simul = TimingSimulation(
                        RFFREQ,
                        callbacks={self.uuid: self._update_driver})
        self._database = self.get_database()

    def process(self, interval):
        """Run continuously in the main thread."""
        t0 = _time.time()
        tf = _time.time()
        dt = (tf-t0)
        if dt > 2*interval:
            _log.warning('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt > 0:
            _time.sleep(dt)

    def write(self, reason, value):
        """Write PV in the model."""
        if not self._isValid(reason, value):
            return False
        ret_val = self.simul.set_propty(reason, value)
        if not ret_val:
            _log.warning('Unsuccessful write of PV {0:s}; value = {1:s}.'
                         .format(reason, str(value)))
        return ret_val

    def _update_driver(self, pvname, value,
                       alarm=None, severity=None, **kwargs):
        self.driver.setParam(pvname, value)
        _log.info('{0:40s}: updated'.format(pvname))
        if alarm is not None and severity is not None:
            self.driver.setParamStatus(pvname, alarm=alarm, severity=severity)
            _log.info('{0:40s}: alarm'.format(pvname))
        self.driver.updatePVs()

    def _isValid(self, reason, value):
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            return False
        enums = (self._database[reason].get('enums') or
                 self._database[reason].get('Enums'))
        if enums is not None:
            if isinstance(value, int):
                len_ = len(enums)
                if value >= len_:
                    _log.warning('value {0:d} too large '.format(value) +
                                 'for PV {0:s} of type enum'.format(reason))
                    return False
            elif isinstance(value, str):
                if value not in enums:
                    _log.warning('Value {0:s} not permited'.format(value))
                    return False
        return True


def run(debug=False):
    """Start the IOC."""

    level = _log.DEBUG if debug else _log.INFO
    fmt = ('%(levelname)7s | %(asctime)s | ' +
           '%(module)15s.%(funcName)20s[%(lineno)4d] ::: %(message)s')
    _log.basicConfig(format=fmt, datefmt='%F %T', level=level,
                     stream=_sys.stdout)
    #  filename=LOG_FILENAME, filemode='w')
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    ioc_name = 'AS-TI-LL-SIMUL'
    db = App.get_database()
    db.update({fname+'Version-Cte': {'type': 'string', 'value': __version__}})
    _log.info('Generating database file.')
    _util.save_ioc_pv_list(ioc_name.lower(), PREFIX, db)
    _log.info('File generated with {0:d} pvs.'.format(len(db)))

    _attribute_acces_security_group(db)

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')
    _log.info('Setting Server Database.')
    server.createPV(PREFIX, db)
    _log.info('Creating Driver.')
    pcas_driver = _Driver()
    _log.info('Creating App.')
    app = App(pcas_driver)
    pcas_driver.app = app

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
