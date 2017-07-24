#!/usr/bin/env python3

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import pvs as _pvs
import multiprocessing as _multiprocessing
import signal as _signal
import main as _main


INTERVAL = 0.1
stop_event = False


def stop_now(signum, frame):
    global stop_event
    stop_event = True
    print(' - SIGINT received.')


class PCASDriver(_pcaspy.Driver):

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

def run():

    # define abort function
    _signal.signal(_signal.SIGINT, stop_now)

    # create a new simple pcaspy server and driver to responde client's requests
    server = _pcaspy.SimpleServer()
    # for prefix, database in _main.App.pvs_database.items():
    #     server.createPV(prefix, database)
    server.createPV(_pvs._PREFIX, _main.App.pvs_database)
    pcas_driver = PCASDriver()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()


if __name__ == '__main__':
    run()
