
import pcaspy
import driver
import pvs
import utils

INTERVAL = 0.1

def run(app):
    server = pcaspy.SimpleServer()
    server.createPV(utils.PREFIX, pvs.pvdb)
    pcas_driver = driver.PCASDriver(app)
    while True:
        server.process(INTERVAL)
