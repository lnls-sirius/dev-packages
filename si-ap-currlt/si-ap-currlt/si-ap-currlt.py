#!/usr/bin/env python3.6

#import siriuspy as _siriuspy
#_siriuspy.util.set_ioc_ca_port_number('si-ap-currlt')

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import threading as _threading
import signal as _signal
import main as _main
import pvs as _pvs

INTERVAL = 0.1
stop_event = False

def stop_now(signum, frame):
    global stop_event
    print(' - SIGINT received.')
    stop_event = True


class PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

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
    global stop_event

    # define abort function
    _signal.signal(_signal.SIGINT, stop_now)

    # create application object
    app = _main.App()

    # create a new simple pcaspy server and driver to responde client's requests
    server = _pcaspy.SimpleServer()
    server.createPV(_main.App.PVS_PREFIX, app.pvs_database)
    pcas_driver = PCASDriver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    try:
        while not stop_event:
            app.process(INTERVAL)
    except:
        app.finilize()

    print('exiting...')
    # sends stop signal to server thread
    server_thread.stop()


if __name__ == '__main__':
    run()
