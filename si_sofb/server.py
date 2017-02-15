
import time
import signal
import multiprocessing
import threading
import pcaspy
import pvs
import driver
import utils
import thread_classes
import epics


WAIT_TIMEOUT = 0.1
JOIN_TIMEOUT = 10.0
INIT_TIMEOUT = 2.0


def run(prefix):
    """Start orbit correction IOC

    Keyword arguments:
    prefix -- prefix to be added to PVs
    """
    global start_event
    global stop_event
    start_event = multiprocessing.Event()
    stop_event = multiprocessing.Event() # signals a stop request
    set_sigint_handler(set_global_stop_event)

    server = pcaspy.SimpleServer()
    server.createPV(prefix, pvs.pvdb)

    thread_names = ('orbit_correction', 'orbit_measurement', 'respm_measurement', 'var_update')
    threads = create_threads(thread_names)
    pcas_driver = driver.PCASDriver(threads, start_event, stop_event, WAIT_TIMEOUT)
    start_threads(threads)

    print_start_ioc_message()
    while not stop_event.is_set():
        server.process(WAIT_TIMEOUT)

    print_stop_event_message()
    join_threads(threads)


def set_sigint_handler(handler):
    signal.signal(signal.SIGINT, handler)


def set_global_stop_event(signum, frame):
    global stop_event
    stop_event.set()


def create_threads(thread_names):
    threads = {}
    for tn in thread_names:
        if tn == 'orbit_correction':
            thread = thread_classes.CODCorrectionThread(tn, stop_event, WAIT_TIMEOUT)
        elif tn == 'orbit_measurement':
            thread = thread_classes.MEASOrbitThread(tn, stop_event, WAIT_TIMEOUT, 1)
        elif tn == 'respm_measurement':
            thread = thread_classes.MEASRespmThread(tn, stop_event, WAIT_TIMEOUT)
        elif tn == 'var_update':
            thread = thread_classes.UPDATEVariablesThread(tn, stop_event, WAIT_TIMEOUT)
        threads[tn] = thread
    return threads


def start_threads(threads):
    for t in threads:
        threads[t].start()


def print_start_ioc_message():
    utils.log('start', 'starting SOFB IOC', 'green')


def print_stop_event_message():
    utils.log('exit', 'stop_event was set', 'red')


def join_threads(threads):
    utils.log('join', 'joining threads...')
    for t in threads:
        threads[t].join(JOIN_TIMEOUT)
    utils.log('join', 'done')
