
import time
import datetime
from termcolor import colored
import pyaccel
import mathphys


UNDEF_VALUE = 0.0
PREFIX_LEN = 2

# Interprocess communication commands - move here


def log(message1='', message2='', c='white', a=None):
    t0 = time.time()
    st = datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d %H:%M:%S')
    st = st + '.{0:03d}'.format(int(1000*(t0-int(t0))))
    if a is None: a = []
    strt = colored(st, 'white', attrs=[])
    str1 = colored('{0:<6.6s}'.format(message1), c, attrs=a)
    str2 = colored('{0}'.format(message2), c, attrs=a)
    strt = strt + ': ' + str1 + ' ' + str2
    print(strt)


def process_and_wait_interval(processing_function, interval):
    start_time = time.time()
    processing_function()
    _wait_interval(start_time, interval)


def _wait_interval(start_time, interval):
    delta_t = time.time() - start_time
    if 0 < delta_t < interval:
        time.sleep(interval - delta_t)
