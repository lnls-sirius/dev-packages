
import pcaspy
import pvs
import driver


PREFIX = 'TESTSERVER-'
INTERVAL = 0.1


def run():
    server = pcaspy.SimpleServer()
    server.createPV(PREFIX, pvs.pvdb)
    pcas_driver = driver.PCASDriver()

    while True:
        server.process(INTERVAL)
