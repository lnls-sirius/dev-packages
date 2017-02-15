#!/usr/bin/env python3

import sys
import os
import threading
import signal
import numpy
import pcaspy

WAIT_TIMEOUT = 0.1

class PCASDriver(pcaspy.Driver):
    def  __init__(self):
        super().__init__()

    def write(self, reason, value):
        prev_value = self.getParam(reason)
        if isinstance(value, (list, tuple, numpy.ndarray)) and len(value) == len(prev_value):
            self.setParam(reason, value)
            self.updatePVs()

def handle_signal(signum, frame):
    global stop_event
    stop_event.set()

def run(prefix):
    global stop_event
    stop_event = threading.Event()
    signal.signal(signal.SIGINT, handle_signal)

    try:
        sep = os.sep
        facroot = os.environ["FACROOT"]
        default_file = facroot + sep + "siriusdb" + sep + "reference_orbit" + sep + "reference_orbit.txt"
        orbit = numpy.genfromtxt(default_file)
        orbit_x = orbit[:,0]
        orbit_y = orbit[:,1]
    except:
        orbit_x = [0]*160
        orbit_y = [0]*160

    pv_database = {'SIPA-REFERENCE-ORBIT-X' : {'type' : 'float', 'count': len(orbit_x), 'value': orbit_x},
                   'SIPA-REFERENCE-ORBIT-Y' : {'type' : 'float', 'count': len(orbit_y), 'value': orbit_y},}

    pvs = [key for key in pv_database.keys()]
    server = pcaspy.SimpleServer()
    server.createPV(prefix, pv_database)
    driver = PCASDriver()

    while not stop_event.is_set():
        server.process(WAIT_TIMEOUT)

prefix = ""
run(prefix)
