"""IOC Module."""
import sys as _sys
import time as _time
import logging as _log
import signal as _signal
from copy import deepcopy as _copy
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from siriuspy.util import get_last_commit_hash as _get_version
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.csdevice.bpms import get_bpm_database as _get_bpm_db
from siriuspy.csdevice.bpms import FFTWritableProps as fft_wr
from siriuspy.diagnostics.bpms.bpm_plugins import BPMFake as BPM

__version__ = _get_version()
INTERVAL = 0.1
_TIMEOUT = 0.05
stop_event = False
BPMS_LIST = []
pvDB = _get_bpm_db()


def _stop_now(signum, frame):
    _log.info('SIGINT received')
    global stop_event
    stop_event = True


def _print_pvs_in_file(db, fname):
    with open('pvs/' + fname, 'w') as f:
        for key in sorted(db.keys()):
            f.write(PREFIX+'{0:40s}\n'.format(key))
    _log.info(fname+' file generated with {0:d} pvs.'.format(len(db)))


def get_database(method=None):
    """Get the database."""
    db = dict()
    for bpm in BPMS_LIST:
        for name, pv in pvDB.items():
            db[bpm+':'+name] = _copy(pv)
            if method:
                if name.endswith(('-SP', '-Sel', '-Cmd')) or name in fft_wr:
                    db[bpm+':'+name]['fun_set_pv'] = method(bpm, name)
    return db


class _PCASDriver(_pcaspy.Driver):
    """Main Class of the IOC Logic."""

    def __init__(self):
        """Initialize the instance."""
        _log.info('Starting Driver...')
        super().__init__()
        self.bpms_list = _copy(BPMS_LIST)
        self.bpms = dict()
        self._database = get_database(self._set_pv_func)
        for bpm in self.bpms_list:
            self.bpms[bpm] = BPM(bpm, callback=self._update_driver)

    def _set_pv_func(self, bpm, name):
        def set_pv(value):
            self.bpms[bpm].pvs[name].value = value
            return True
        return set_pv

    def process(self, interval):
        """Run continuously in the main thread."""
        _time.sleep(interval)

    def write(self, reason, value):
        """Write PV in the model."""
        _log.debug('Writing PV {0:s} with value {1:s}'
                   .format(reason, str(value)))
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('Write unsuccessful. PV ' +
                         '{0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.debug('Write complete.')
        else:
            _log.warning('Unsuccessful write of PV {0:s}; value = {1:s}.'
                         .format(reason, str(value)))
        return ret_val

    def _update_driver(self, pvname, value, **kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'
                   .format(pvname, str(value)))
        self.setParam(pvname, value)
        self.updatePVs()

    def _isValid(self, reason, value):
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            _log.debug('PV {0:s} is read only.'.format(reason))
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


def run(bpms_list=[], debug=False):
    """Start the IOC."""

    global BPMS_LIST
    BPMS_LIST.extend(bpms_list)

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

    _log.info('Generating database file.')
    fname = 'as-ap-bpms'
    db = get_database()
    db.update({fname+'Version-Cte': {'type': 'string', 'value': __version__}})
    _print_pvs_in_file(db, fname=fname+'pvs.txt')

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _log.info('Setting Server Database.')
    server.createPV(PREFIX, db)
    _log.info('Creating Driver.')
    pcas_driver = _PCASDriver()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')


if __name__ == '__main__':
    run(['SI-01M1:DI-BPM', 'SI-01M2:DI-BPM', 'SI-01C1-1:DI-BPM'])
