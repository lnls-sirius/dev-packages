#!/usr/bin/env python3

import time
import threading
import signal
import math
import numpy
import epics
import collections
import pcaspy

WAIT_TIMEOUT = 0.1

class DriverThread(threading.Thread):

    def __init__(self, stop_event, driver):
        self.driver = driver
        self.stop_event = stop_event
        super().__init__(target = self.main)

    def main(self):
        while not self.stop_event.is_set():
            self.driver.process()


class PCASDriver(pcaspy.Driver):

    def  __init__(self, calc_lifetime_thread):
        super().__init__()
        self.calc_lifetime_thread = calc_lifetime_thread
        self.setParam('SIPA-LIFETIME-DT',  self.calc_lifetime_thread.sample_interval)
        self.setParam('SIPA-LIFETIME-PREC', self.calc_lifetime_thread.precision)

    def process(self):
        t0 = time.time()
        lifetime_sec  = self.calc_lifetime_thread.lifetime
        lifetime_min  = lifetime_sec/60.0
        lifetime_hour = lifetime_sec/3600.0
        self.setParam('SIPA-LIFETIME-SEC',  lifetime_sec)
        self.setParam('SIPA-LIFETIME-MIN',  lifetime_min)
        self.setParam('SIPA-LIFETIME-HOUR', lifetime_hour)
        self.setParam('SIPA-LIFETIME-NRPOINTS', self.calc_lifetime_thread.nr_points)
        self.updatePVs()
        t1 = time.time()
        time.sleep(WAIT_TIMEOUT - (t1-t0))

    def write(self, reason, value):
        if '-DT' in reason:
            self.setParam(reason, value)
            self.calc_lifetime_thread.sample_interval = value
            self.updatePVs()
        elif '-PREC' in reason:
            self.setParam(reason, value)
            self.calc_lifetime_thread.precision = value
            self.updatePVs()


class CalcLifetimeThread(threading.Thread):

    def __init__(self, stop_event):
        self.stop_event      = stop_event
        self.sample_interval = 0.1
        self.precision       = 1.0
        self.lifetime        = 0.0
        self.intervals       = [10,11,12,13,14,15,16,17,18,19,20,22,24,26,28,30,34,
                                38,42,48,54,60,68,76,86,98,110,124,140,160,182,200]
        self.count_time      = 0
        self.idx             = 20
        self.len_intervals   = len(self.intervals)
        self.nr_points       = self.intervals[self.idx]
        self.buffer_size     = 2*self.intervals[-1]
        self.measures        = collections.deque(maxlen=self.buffer_size)
        self.timestamp       = collections.deque(maxlen=self.buffer_size)
        self.current_pv       = epics.PV('SIDI-CURRENT')
        self.current_noise_pv = epics.PV('VA-SIDI-CURRENT-NOISELEVEL')
        super().__init__(target=self.main)

    def measure_current(self):
        current, timestamp = 1e-3*self.current_pv.get(), self.current_pv.timestamp
        self.current_noise = 1e-6*self.current_noise_pv.get()
        if self.current_noise == 0: self.current_noise = 10e-6
        if len(self.measures)!=0:
            if math.fabs(current - self.measures[-1]) > 100*self.current_noise:
                self.idx = 20
                self.nr_points = self.intervals[self.idx]
                self.measures.clear()
                self.timestamp.clear()
        self.measures.append(current)
        self.timestamp.append(timestamp)

    def calc_lifetime(self):
        measures = numpy.array(self.measures)
        if len(measures) >= 2*self.nr_points:
            average1 = sum(measures[-self.nr_points:])
            average2 = sum(measures[-2*self.nr_points:-self.nr_points])
            if average1 < 0.0005 and average2 < 0.0005:
                self.lifetime = 0.0
            else:
                average1 = average1/self.nr_points
                average2 = average2/self.nr_points
                current  = (average1 + average2)/2.0
                if math.fabs(average2 - average1) != 0:
                    self.lifetime = current*self.nr_points*self.sample_interval/math.fabs(average2 - average1)
                else:
                    self.lifetime = 0.0
                self.calc_interval(current)

    def calc_interval(self, current):
        dtmin = ((self.lifetime*(self.current_noise/current)*math.sqrt(2*self.sample_interval))/(1e-2*self.precision + 0.005))**(2/3)
        dtmax = ((self.lifetime*(self.current_noise/current)*math.sqrt(2*self.sample_interval))/(1e-2*self.precision - 0.005))**(2/3)
        if dtmin > (2*self.nr_points*self.sample_interval):
            self.count_time += 1
            if self.idx < (self.len_intervals-1) and (2*self.nr_points)<=self.count_time and len(self.measures)>(2*self.intervals[self.idx+1]):
                self.idx += 1
        else:
            if dtmax < (2*self.nr_points*self.sample_interval):
                if self.idx < (self.len_intervals) and self.idx > 0 :
                    self.idx -= 1
                self.count_time = 0
        if self.idx > self.len_intervals: self.idx = self.len_intervals
        self.nr_points = self.intervals[self.idx]

    def main(self):
        while not self.stop_event.is_set():
            try:
                if not all([self.current_pv.connected, self.current_noise_pv.connected]):
                    time.sleep(self.sample_interval)
                else:
                    t0 = time.time()
                    self.measure_current()
                    self.calc_lifetime()
                    t1 = time.time()
                    if (t1-t0) < self.sample_interval:
                        time.sleep(self.sample_interval - (t1-t0))
            except:
                time.sleep(self.sample_interval)

def handle_signal(signum, frame):
    global stop_event
    stop_event.set()


def run(prefix):
    global stop_event
    stop_event = threading.Event()
    signal.signal(signal.SIGINT, handle_signal)

    pv_database = {'SIPA-LIFETIME-SEC'      : {'type' : 'float', 'count': 1, 'value': 0.0, 'unit': 's'},
                   'SIPA-LIFETIME-MIN'      : {'type' : 'float', 'count': 1, 'value': 0.0, 'unit': 'min'},
                   'SIPA-LIFETIME-HOUR'     : {'type' : 'float', 'count': 1, 'value': 0.0, 'unit': 'h'},
                   'SIPA-LIFETIME-DT'       : {'type' : 'float', 'count': 1, 'value': 0.0, 'unit': 's'},
                   'SIPA-LIFETIME-PREC'     : {'type' : 'float', 'count': 1, 'value': 0.0, 'unit': '%'},
                   'SIPA-LIFETIME-NRPOINTS' : {'type' : 'int',   'count': 1, 'value': 0},}

    pvs = [key for key in pv_database.keys()]
    server = pcaspy.SimpleServer()
    server.createPV(prefix, pv_database)

    calc_lifetime_thread = CalcLifetimeThread(stop_event)
    calc_lifetime_thread.start()
    driver = PCASDriver(calc_lifetime_thread)
    driver_thread = DriverThread(stop_event, driver)
    driver_thread.start()

    while not stop_event.is_set():
        server.process(WAIT_TIMEOUT)

    calc_lifetime_thread.join()
    driver_thread.join()

prefix = ""
run(prefix)
