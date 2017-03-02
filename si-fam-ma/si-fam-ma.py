import multiprocessing
import signal
from pcaspy import Driver, SimpleServer
from pcaspy.tools import ServerThread
import main

INTERVAL = 0.1
PREFIX   = ''

class MyDriver(Driver):

    stop_event = multiprocessing.Event()

    @staticmethod
    def stop_now(signum, frame):
        return stop_event.set()

    def __init__(self, app):
        super().__init__()
        self.app = main.App(self)

    def read(self, reason):
        self.app.read(reason)
        return super().read(reason)

    def write(self,reason,value):
        status = self.app.write(reason,value)
        if status: return super().write(reason, value)
        return status


if __name__ == '__main__':
    driver = MyDriver()

    signal.signal(signal.SIGINT, driver.stop_now)

    server = SimpleServer()
    server.createPV(PREFIX, driver.app.pv_database)
    server_thread = ServerThread(server)

    server_thread.start()
    while not stop_event.is_set():
        driver.app.process(INTERVAL)
    server_thread.stop()
