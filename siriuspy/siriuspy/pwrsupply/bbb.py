#!/usr/bin/env python-sirius

"""BeagleBone Controller.

This module implements classes that are used to do low level BeagleBone
communications, be it with PRU or BSMP requests to power supply controllers
at the other end of the serial line.
"""

import time as _time
import math as _math
from collections import deque as _deque
from collections import namedtuple as _namedtuple
from threading import Thread as _Thread
from threading import Lock as _Lock
from copy import deepcopy as _dcopy


from siriuspy.bsmp import BSMP
from siriuspy.bsmp import Response
from siriuspy.bsmp import SerialError as _SerialError
from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.pru import PRUInterface as _PRUInterface
from siriuspy.pwrsupply.pru import PRU
from siriuspy.pwrsupply.bsmp import Const as _c


BBB1_device_ids = (1, 2)
BBB2_device_ids = (5, 6)


class BSMPOpQueue(_deque):
    """BSMPOpQueue.

    This class takes manages operations which invoque BSMP communications using
    an append-right, pop-left queue. It also processes the next operation in a
    way as to circumvent the blocking character of UART writes when PRU sync
    mode is on.
    """

    _lock = _Lock()

    def __init__(self):
        """Init."""
        self._thread = None
        self._ignore = False

    @property
    def last_operation(self):
        """Return last operation."""
        return self._last_operation

    def ignore_set(self):
        """Turn ignore state on."""
        self._ignore = True

    def ignore_clear(self):
        """Turn ignore state on."""
        self._ignore = False

    def append(self, operation, unique=False):
        """Append operation to queue."""
        BSMPOpQueue._lock.acquire(blocking=True)
        if not self._ignore:
            if not unique:
                super().append(operation)
                self._last_operation = operation
            else:
                # super().append(operation)
                # self._last_operation = operation
                n = self.count(operation)
                if n == 0:
                    super().append(operation)
                    self._last_operation = operation
        BSMPOpQueue._lock.release()

    def clear(self):
        """Clear deque."""
        self._lock.acquire()
        super().clear()
        self._lock.release()

    def popleft(self):
        """Pop left operation from queue."""
        BSMPOpQueue._lock.acquire(blocking=True)
        if super().__len__() > 0:
            value = super().popleft()
        else:
            value = None
        BSMPOpQueue._lock.release()
        return value

    def process(self):
        """Process operation from queue."""
        # first check if a thread is already running
        if self._thread is None or not self._thread.is_alive():
            # no thread is running, we can process queue
            operation = self.popleft()
            if operation is None:
                # nothing in queue
                return False
            else:
                # process operation take from queue
                func, args = operation
                self._thread = _Thread(target=func, args=args, daemon=True)
                self._thread.start()
                return True
        else:
            return False


class BBBController:
    """BeagleBone controller.

    This class implements all basic PRU configuration and BSMP communications
    of the BeagleBone computer connected through a serial line to power supply
    controllers.
    """

    # TODO: make class robust to BSMP errors!!!
    # TODO: test class in sync on mode and trigger from timing
    # TODO: implement BSMP function executions

    # TODO: Improve update frequency in WfmRamp/MigRamp
    #
    # Gabriel from ELP proposed the idea of a privilegded slave that
    # could define BSMP variables that corresponded to other slaves variables
    # By defining a BSMP variable group with selected variables from all
    # devices we could update all device states with a single BSMP request
    # thus providing higher refresh rates.

    # TODO: check if these measured times are not artifact of python!

    # frequency constants
    # _FREQ_RAMP = 2.0  # [Hz]
    # _FREQ_SCAN = 10.0  # [Hz]
    FREQ = _namedtuple('FREQ', '')
    FREQ.RAMP = 2.0  # [Hz]
    FREQ.SCAN = 10.0  # [Hz]

    # define PRU constants
    # SYNC_OFF = _PRUInterface._SYNC_OFF
    # SYNC_ON = _PRUInterface._SYNC_ON
    # SYNC_MIGINT = _PRUInterface.SYNC_MIGINT
    # SYNC_MIGEND = _PRUInterface.SYNC_MIGEND
    # SYNC_RMPINT = _PRUInterface.SYNC_RMPINT
    # SYNC_RMPEND = _PRUInterface.SYNC_RMPEND
    # SYNC_CYCLE = _PRUInterface.SYNC_CYCLE
    SYNC = _namedtuple('SYNC', '')
    SYNC.OFF = _PRUInterface._SYNC_OFF
    SYNC.ON = _PRUInterface._SYNC_ON
    SYNC.MIGINT = _PRUInterface.SYNC_MIGINT
    SYNC.MIGEND = _PRUInterface.SYNC_MIGEND
    SYNC.RMPINT = _PRUInterface.SYNC_RMPINT
    SYNC.RMPEND = _PRUInterface.SYNC_RMPEND
    SYNC.CYCLE = _PRUInterface.SYNC_CYCLE

    _groups = dict()

    # predefined variable groups
    _groups[0] = (
        _c.V_PS_STATUS,
        _c.V_PS_SETPOINT,
        _c.V_PS_REFERENCE,
        _c.V_FIRMWARE_VERSION,
        _c.V_COUNTER_SET_SLOWREF,
        _c.V_COUNTER_SYNC_PULSE,
        _c.V_SIGGEN_ENABLE,
        _c.V_SIGGEN_TYPE,
        _c.V_SIGGEN_NUM_CYCLES,
        _c.V_SIGGEN_N,
        _c.V_SIGGEN_FREQ,
        _c.V_SIGGEN_AMPLITUDE,
        _c.V_SIGGEN_OFFSET,
        _c.V_SIGGEN_AUX_PARAM,
        _c.V_UNDEF14,
        _c.V_UNDEF15,
        _c.V_UNDEF16,
        _c.V_UNDEF17,
        _c.V_UNDEF18,
        _c.V_UNDEF19,
        _c.V_UNDEF20,
        _c.V_UNDEF21,
        _c.V_UNDEF22,
        _c.V_UNDEF23,
        _c.V_UNDEF24,
        _c.V_PS_SOFT_INTERLOCKS,
        _c.V_PS_HARD_INTERLOCKS,
        _c.V_I_LOAD,
        _c.V_V_LOAD,
        _c.V_V_DCLINK,
        _c.V_TEMP_SWITCHES,)
    _groups[1] = _groups[0]
    _groups[2] = tuple()

    # new groups (must be continous!)
    _groups[3] = (
        # =======================================================
        # SyncMode: SlowRef and Cycle
        #   17.2 ± 0.3 ms @ BBB1, 4 ps/cycle [2.0 hz update]
        # SyncMode: RmpWfm and MigWfm
        #    4.5 ± 0.1 ms @ BBB1, 1 ps/cycle [0.5 Hz update]
        # =======================================================
        _c.V_PS_STATUS,
        _c.V_PS_SETPOINT,
        _c.V_PS_REFERENCE,
        # _c.V_FIRMWARE_VERSION,
        _c.V_COUNTER_SET_SLOWREF,
        _c.V_COUNTER_SYNC_PULSE,
        _c.V_SIGGEN_ENABLE,
        _c.V_SIGGEN_TYPE,
        _c.V_SIGGEN_NUM_CYCLES,
        _c.V_SIGGEN_N,
        _c.V_SIGGEN_FREQ,
        _c.V_SIGGEN_AMPLITUDE,
        _c.V_SIGGEN_OFFSET,
        _c.V_SIGGEN_AUX_PARAM,
        _c.V_PS_SOFT_INTERLOCKS,
        _c.V_PS_HARD_INTERLOCKS,
        _c.V_I_LOAD,
        _c.V_V_LOAD,
        _c.V_V_DCLINK,
        _c.V_TEMP_SWITCHES,)
    _groups[4] = (
        # =======================================================
        # SyncMode: RmpWfm and MigWfm
        #   2.0 ± 0.1 ms @ BBB1, 1 ps/cycle [0.5 Hz update]
        # =======================================================
        _c.V_PS_STATUS,
        _c.V_PS_SETPOINT,
        _c.V_PS_REFERENCE,
        # _c.V_FIRMWARE_VERSION,
        # _c.V_COUNTER_SET_SLOWREF,
        # _c.V_COUNTER_SYNC_PULSE,
        _c.V_SIGGEN_ENABLE,
        # _c.V_SIGGEN_TYPE,
        # _c.V_SIGGEN_NUM_CYCLES,
        # _c.V_SIGGEN_N,
        # _c.V_SIGGEN_FREQ,
        # _c.V_SIGGEN_AMPLITUDE,
        # _c.V_SIGGEN_OFFSET,
        # _c.V_SIGGEN_AUX_PARAM,
        _c.V_PS_SOFT_INTERLOCKS,
        _c.V_PS_HARD_INTERLOCKS,
        _c.V_I_LOAD,
        # _c.V_V_LOAD,
        # _c.V_V_DCLINK,
        # _c.V_TEMP_SWITCHES,
    )

    _sleep_delay = 0.010  # [s]

    # --- public interface ---

    def __init__(self, bsmp_entities, device_ids=BBB1_device_ids):
        """Init."""
        self._device_ids = sorted(device_ids)
        # self._device_ids = sorted(device_ids + device_ids)  # test with 4 PS

        # create PRU with sync mode off.
        self._pru = PRU()
        self._time_interval = self._get_time_interval()

        # initialize BSMP
        self._initialize_bsmp(bsmp_entities)

        # operation queue
        self._queue = BSMPOpQueue()

        self._connections = list()
        for id in device_ids:
            self._connections.append(False)

        # scan thread
        self._last_device_scanned = len(self._device_ids)  # next is the first
        self._update_exec_time = None  # registers last update exec time
        self._thread_scan = _Thread(target=self._loop_scan, daemon=True)
        self._scanning = True
        self._thread_scan.start()

        # process thread
        self._thread_process = _Thread(target=self._loop_process, daemon=True)
        self._processing = True
        self._thread_process.start()

    @property
    def scan(self):
        """Return scanning state."""
        return self._scanning

    @scan.setter
    def scan(self, value):
        """Set scanning state."""
        self._scanning = value

    @property
    def process(self):
        """Return processing state."""
        return self._processing

    @process.setter
    def process(self, value):
        """Set scan state."""
        self._processing = value

    @property
    def queue_length(self):
        """Number of operations currently in the queue."""
        return len(self._queue)

    @property
    def connections(self):
        return self._connections
    # ---- main methods ----

    def read_variable(self, device_id, variable_id=None):
        """Return current mirror of variable values of the BSMP device."""
        dev_values = self._variables_values[device_id]
        if variable_id is None:
            values = dev_values
        else:
            values = dev_values[variable_id]
        return _dcopy(values)  # return a deep copy

    def exec_function(self, device_id, function_id, args=None):
        """Append a BSMP function execution to operations queue."""
        if self._pru.sync_status == self.SYNC.OFF:
            # in PRU sync off mode, append BSM function exec operation to queue
            if not args:
                args = (device_id, function_id)
            else:
                args = (device_id, function_id, args)
            operation = (self._bsmp_exec_function, args)
            self._queue.append(operation)
        else:
            # does nothing if PRU sync is on, regardless of sync mode.
            return False

    # ---- PRU and BSMP methods ----

    def pru_get_sync_status(self):
        """Return PRU sync status."""
        return self._pru.sync_status

    def pru_sync_stop(self):
        """Stop PRU sync mode."""
        # TODO: should we do more than what is implemented?
        self._pru.sync_stop()
        self._time_interval = self._get_time_interval()

    def pru_sync_start(self, sync_mode):
        """Start PRU sync mode."""
        # try to abandon previous sync mode gracefully
        if self._pru.sync_status != self.SYNC.OFF:
            # --- already with sync mode on.
            if sync_mode != self._pru.sync_mode:
                # --- different sync mode
                # PRU sync is on but it needs sync_mode change
                # first turn off PRY sync mode
                self.pru_sync_stop()
            else:
                # --- already in selected sync mode
                # TODO: to do nothing is what we want? what about WfmIndex?
                return
        else:
            # --- current sync mode is off
            pass

        # wait for all queued operations to be processed
        self._queue.ignore_set()  # ignore eventual new operation requests
        while len(self._queue) > 0:
            _time.sleep(5*self._sleep_delay)  # sleep a little

        # update time interval according to new sync mode selected
        self._time_interval = self._get_time_interval()

        # set selected sync mode
        self._pru.sync_start(
            sync_mode=sync_mode,
            sync_address=self._device_ids[0], delay=100)

        # accept back new operation requests
        self._queue.ignore_clear()

    def bsmp_scan(self):
        """Run scan one."""
        # select devices and variable group, defining the read group
        # opertation to be performed
        device_ids, group_id = self._select_device_group_ids()
        operation = (self._bsmp_update_variables,
                     (device_ids, group_id, ))
        if len(self._queue) == 0 or \
           operation != self._queue.last_operation:
            if self._pru.sync_status == self.SYNC.OFF:
                # with sync off, function executions are allowed and
                # therefore operations must be queued in order
                self._queue.append(operation)
            else:
                # for sync on, no function execution is accepted and
                # we can therefore append only unique operations since
                # processing order is not relevant.
                self._queue.append(operation, unique=True)
        else:
            # does not append if last operation is the same as last one
            # operation appended to queue
            pass

    def bsmp_process(self):
        """Run process once."""
        # process first operation in queue, if any
        self._queue.process()
        # print info
        n = len(self._queue)
        if n > 50:
            print('BBB queue size: {} !!!'.format(len(self._queue)))

    # ---- methods to access and measure communication times ----

    def meas_exec_time(self):
        """Return last update execution time [s]."""
        return self._update_exec_time

    def meas_sample_exec_time(self, device_ids, group_id, nrpoints=20):
        """Measure execution times and return stats and sample."""
        sample = []
        self.pru_sync_stop()

        # turn scanning off
        self._scanning = False

        # wait until queue empties
        while len(self._queue) > 0:
            _time.sleep(5*self._sleep_delay)  # sleep a little
        _time.sleep(self._time_interval)

        # loop and collect sample
        while len(sample) < nrpoints:
            self._bsmp_update_variables(device_ids, group_id)
            value = self.meas_exec_time()
            sample.append(value)
            print('{:03d}: {:.4f} ms'.format(len(sample), 1000*value))
            _time.sleep(self._time_interval)

        # turn scanning back on
        self._scanning = True

        # calc stats and return
        n = len(sample)
        avg = sum(sample)/n
        dev = _math.sqrt(sum([(v - avg)**2 for v in sample])/(n-1.0))
        return avg, dev, sample

    # --- private methods ---

    def _initialize_bsmp(self, bsmp_entities):

        # TODO: deal with BSMP comm errors at init!!

        # create BSMP devices
        self._bsmp = self._create_bsmp(bsmp_entities)

        # initialize variable groups
        self._initialize_groups()

        # initialize variables_values, a mirror state of BSMP devices
        self._initialize_variable_values(bsmp_entities)

    def _create_bsmp(self, bsmp_entities):
        bsmp = dict()
        for id in self._device_ids:
            # TODO: catch BSMP comm errors
            bsmp[id] = BSMP(self._pru, id, bsmp_entities)
        return bsmp

    def _initialize_variable_values(self, bsmp_entities):

        # create _variables_values
        dev_variables = \
            [None, ] * (1+max([v.eid for v in bsmp_entities.variables]))
        self._variables_values = \
            {id: dev_variables[:] for id in self._device_ids}
        # TODO: should we initialize this reading the ps controllers?

        # read all variable from BSMP devices
        # TODO: for some reason cannot use group_id = 0 !!!
        # it seems
        self._bsmp_update_variables(device_ids=self._device_ids, group_id=0)

    def _initialize_groups(self):

        # TODO: catch BSMP comm errors

        # check if groups have consecutive ids
        groups_ids = sorted(self._groups.keys())
        if len(groups_ids) < 3:
            raise ValueError('Invalid variable group definition!')
        for i in range(len(groups_ids)):
            if i not in groups_ids:
                raise ValueError('Invalid variable group definition!')

        # loop over bsmp devices
        for id in self._device_ids:
            # remove previous variables groups and fresh ones
            self._bsmp[id].remove_all_groups()
            for group_id in groups_ids[3:]:
                var_ids = self._groups[group_id]
                self._bsmp[id].create_group(var_ids)

    def _loop_scan(self):
        while True:
            if self._scanning:
                self.bsmp_scan()
            # wait for time_interval
            _time.sleep(self._time_interval)

    def _loop_process(self):
        while True:
            if self._processing:
                self.bsmp_process()
            # sleep a little
            _time.sleep(self._sleep_delay)

    def _select_device_group_ids(self):
        """Return variable group id and device ids for the loop scan."""
        if self._pru.sync_status == self.SYNC.OFF:
            return self._device_ids, 3
        else:
            if self._pru.sync_mode == self.SYNC.CYCLE:
                # return all devices
                return self._device_ids, 3
            else:
                dev_id = self._select_next_device_id()
                return (dev_id,), 3

    def _select_next_device_id(self):
        # calc index of next single device to be scanned
        nr_devs = len(self._device_ids)
        dev_idx = (self._last_device_scanned + 1) % nr_devs
        dev_id = self._device_ids[dev_idx]
        self._last_device_scanned = dev_idx
        return dev_id

    def _get_time_interval(self):
        if self._pru.sync_status == self.SYNC.OFF or \
           self._pru.sync_mode == self.SYNC.CYCLE:
            return 1.0/self.FREQ.SCAN  # [s]
        else:
            return 1.0/self.FREQ.RAMP  # [s]

    # --- methods that generate BSMP UART communications ---

    def _bsmp_update_variables(self, device_ids, group_id):

        ack, data = dict(), dict()

        # --- send requests to serial line
        t0 = _time.time()
        for id in device_ids:
            try:
                ack[id], data[id] = \
                    self._bsmp[id].read_group_variables(group_id=group_id)
                self._connections[id] = True
            except _SerialError:
                ack[id], data[id] = (None, None)
                self._connections[id] = False
        self._update_exec_time = _time.time() - t0

        # print('ack: ', ack)
        # print('data: ', data)

        # --- update variables, if ack is ok
        var_ids = self._groups[group_id]

        # print('var_ids: ', var_ids)

        for id in device_ids:
            if ack[id] == Response.ok:
                values = data[id]
                # print('values: ', values)
                for i in range(len(values)):
                    var_id = var_ids[i]
                    # print('variables_values: ', self._variables_values[id])
                    # print('id: ', id)
                    # print('id: ', values[i])
                    self._variables_values[id][var_id] = values[i]
            else:
                # TODO: update 'connect' state for that device
                pass

    def _bsmp_exec_function(self, device_id, function_id, args=None):
        ack, values = self._bsmp[device_id].execute_function(function_id, args)
        if ack == Response.ok:
            return values
        else:
            # TODO: update 'connect' state for that device
            return None


def create_BBBController():
    """Return a BBB."""
    bbb = BBBController(bsmp_entities=FBPEntities(),
                        device_ids=BBB1_device_ids)
    return bbb


def init_bbb():

    bbb = create_BBBController()

    # turn power supply on
    bbb.exec_function(1, 0, args=())
    _time.sleep(0.3)
    # print('turn on')

    # close loop
    bbb.exec_function(1, 3, args=())
    _time.sleep(0.3)
    # print('close loop')

    # set slowref
    bbb.exec_function(1, 4, args=(3,))

    # setpoint
    bbb.exec_function(1, 16, args=(2.5))
    # print('setpoint')

    return bbb


def init_siggen(bbb):

    # configure siggen
    args = (
        0,
        10,
        0.5,
        2.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )
    bbb.exec_function(1, 23, args)

    # disable siggen
    bbb.exec_function(1, 26)

    # set ps to cycle mode
    bbb.exec_function(1, 4, args=(5,))




# def run_cycle(bbb, print_flag=True):
#
#     t = _Thread(target=_run_cycle, args=(bbb, print_flag))
#     t.start()


def run_cycle(bbb, print_flag=True):

    # set sync on
    bbb.pru_sync_start(0x5c)

    if bbb.pru_get_sync_status() == 0:
        print('problem!')
        return

    rcvd_trig = False
    t0 = None
    while True:
        if bbb.pru_get_sync_status() == 0 and not rcvd_trig:
            rcvd_trig = True
            t0 = _time.time()
            print('sync trigger!')
            # bbb.exec_function(1, 25)

        siggen_enable = bbb.read_variable(1, 6)
        iLoad = bbb.read_variable(1, 27)
        if print_flag:
            print('enable: {}, iload: {:.4f}'.format(siggen_enable, iLoad))
        _time.sleep(0.1)
        if t0 and _time.time()-t0 > 22:
            break


def main():
    """Run."""
    bbb = create_BBBController()
    print('pru_sync_status: {}'.format(bbb.pru.sync_status))
    # bbb.pru.sync_start()


if __name__ == "__main__":
    main()
