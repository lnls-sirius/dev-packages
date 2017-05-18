#!/usr/bin/env python3

import logging as _log
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import pvs as _pvs
import multiprocessing as _multiprocessing
import signal as _signal
import main as _main


INTERVAL = 0.1
stop_event = False # _multiprocessing.Event()
PREFIX = ''
DB_FILENAME = 'my_pvs.txt'
LOG_FILENAME = 'as-hl-timing.log'

def stop_now(signum, frame):
    _log.info('SIGINT received')
    global stop_event
    stop_event = True

def print_pvs_in_file(db):
    with open(DB_FILENAME,'w') as f:
        for key in sorted(db.keys()):
            f.write('{0:20s}\n'.format(key))
    _log.info(DB_FILENAME+' file generated with {0:d} pvs.'.format(len(db)))

class PCASDriver(_pcaspy.Driver):

    def __init__(self,app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        _log.debug("Sending read of {0:s} to App.".format(reason))
        value = self.app.read(reason)
        if value is None:
            _log.debug("PV {0:s} read by App. Trying drivers database.".format(reason))
            return super().read(reason)
        else:
            _log.debug("App returned {0:s} for PV {1:s}.".format(str(value),reason))
            return value

    def write(self, reason, value):
        app_ret =  self.app.write(reason, value)
        if app_ret:
            self.setParam(reason,value)
            self.updatePVs()
        return app_ret


def run():

    fmt = '%(levelname)7s | %(asctime)s: %(message)s'
    _log.basicConfig(format=fmt,datefmt='%F %T',filename=LOG_FILENAME, level=_log.DEBUG)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, stop_now)

    # Creates App object
    _log.info('Creating App.')
    app = _main.App()
    _log.info('Generating database file.')
    db = app.get_database()
    print_pvs_in_file(db)


    # create a new simple pcaspy server and driver to responde client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _log.info('Setting Server Database.')
    server.createPV(PREFIX, db)
    _log.info('Creating Driver.')
    pcas_driver = PCASDriver(app)

    # Connects to low level PVs
    _log.info('Openning connections with Low Level IOCs.')
    app.connect()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    #while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')


if __name__ == '__main__':
    run()
