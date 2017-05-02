#!/usr/bin/env python3
import siriuspy.util as _util
_util.set_ioc_ca_port_number('as-high-level-timing')

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import pvs as _pvs
import multiprocessing as _multiprocessing
import signal as _signal
import main as _main


INTERVAL = 0.1
stop_event = False # _multiprocessing.Event()


def stop_now(signum, frame):
    print(' - SIGINT received.')
    global stop_event
    stop_event = True


class PCASDriver(_pcaspy.Driver):

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
        app_ret =  self.app.write(reason, value)
        if app_ret:
            self.setParam(reason,value)
            self.updatePVs()
        return app_ret


def run():

    # define abort function
    _signal.signal(_signal.SIGINT, stop_now)

    # create a new simple pcaspy server and driver to responde client's requests
    server = _pcaspy.SimpleServer()
    for prefix, database in _main.App.pvs_database.items():
        server.createPV(prefix, database)
    pcas_driver = PCASDriver()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    #while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    print('exiting...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()


if __name__ == '__main__':
    run()
