#!/usr/bin/env python-sirius

"""Tests."""

import time as _time
from collections import deque as _deque
from threading import Thread as _Thread
from threading import Lock as _Lock

from siriuspy.bsmp import BSMP
from siriuspy.bsmp import Response
from siriuspy.pwrsupply.bsmp import FBPEntities
from siriuspy.pwrsupply.pru import PRU
from siriuspy.pwrsupply.bsmp import Const as _c


BBB1_device_ids = (1, 2)
BBB2_device_ids = (3, 4)


class BSMPOpQueue(_deque):
    """BBBQueue."""

    def __init__(self):
        """Init."""
        self._lock = _Lock()
        self._thread = None

    @property
    def last_operation(self):
        """Return last operation."""
        return self._last_operation

    def append(self, operation):
        """Append operation to queue."""
        self._lock.acquire()
        super().append(operation)
        self._last_operation = operation
        self._lock.release()

    def clear(self):
        """Clear deque."""
        self._lock.acquire()
        super().clear()
        self._lock.release()

    def popleft(self):
        """Pop left operation from queue."""
        self._lock.acquire()
        if super().__len__() > 0:
            value = super().popleft()
        else:
            value = None
        self._lock.release()
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

    _FREQ_RAMP = 2.0  # [Hz]
    _FREQ_SCAN = 10.0  # [Hz]

    _group0 = (
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
        _c.V_PS_SOFT_INTERLOCKS,
        _c.V_PS_HARD_INTERLOCKS,
        _c.V_I_LOAD,
        _c.V_V_LOAD,
        _c.V_V_DCLINK,
        _c.V_TEMP_SWITCHES,
    )

    # TODO: check if these times are not artifact of python!

    _group3 = (
        # ================================================
        # SyncMode: SlowRef and Cycle
        # It is taking 17 ms @ BBB1 for 4 power supplies.
        # ================================================
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
        _c.V_TEMP_SWITCHES,
    )

    _group4 = (
        # ================================================
        # SyncMode: RmpWfm and MigWfm
        # It is taking 8 ms @ BBB1 for 4 power supplies.
        # ================================================

        _c.V_PS_STATUS,
        # _c.V_PS_SETPOINT,
        _c.V_PS_REFERENCE,
        # _c.V_FIRMWARE_VERSION,
        # _c.V_COUNTER_SET_SLOWREF,
        # _c.V_COUNTER_SYNC_PULSE,
        # _c.V_SIGGEN_ENABLE,
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

    _groups = {
        3: _group3,
        4: _group4,
    }

    # --- public interface ---

    def __init__(self, bsmp_entities, device_ids=BBB1_device_ids):
        """Init."""
        self._device_ids = sorted(device_ids)
        # self._device_ids = sorted(device_ids + device_ids)  # test with 4 PS

        # create PRU with sync mode off.
        self._pru = PRU()
        self._time_interval = self._get_time_interval()

        # create BSMP devices
        self._bsmp = dict()
        for id in self._device_ids:
            # TODO: catch BSMP comm errors
            self._bsmp[id] = BSMP(self._pru, id, bsmp_entities)

        # remove previous variables groups and fresh ones
        groups_ids = sorted(self._groups.keys())
        for id in self._device_ids:
            # TODO: catch BSMP comm errors
            self._bsmp[id].remove_all_groups()
            for group_id in groups_ids:
                var_ids = self._groups[group_id]
                self._bsmp[id].create_group(var_ids)

        # copy of ps controller variables
        dev_variables = [None, ] * len(bsmp_entities.variables)
        self._variables_values = \
            {id: dev_variables[:] for id in self._device_ids}
        # TODO: should be initialize this reading the ps controllers?
        # at this points the PRU is in sync off mode.

        # operation queue
        self._queue = BSMPOpQueue()

        # scan thread
        self._thread_scan = _Thread(target=self._loop_scan, daemon=True)
        self._thread_scan.start()

        # process thread
        self._thread_process = _Thread(target=self._loop_process,
                                       daemon=True)
        self._thread_process.start()

    @property
    def variables_values(self):
        """Variable values."""
        # make copy of variable values
        value = {k: [d for d in v] for k, v in self._variables_values.items()}
        return value

    def pru_sync_status(self):
        """Return PRU sync status."""
        return self._pru.sync_status

    def pru_sync_stop(self):
        """Stop PRU sync mode."""
        self._pru.sync_stop()

    def pru_sync_start(self, sync_mode):
        """Start PRU sync mode."""
        self._pru.sync_start(sync_mode=sync_mode,
                             sync_address=self._device_ids[0], delay=100)

    # --- private methods ---

    def _loop_scan(self):
        while True:

            # update time_interval
            self._time_interval = self._get_time_interval()

            # append update variables group to queue
            group_id = self._select_scan_group_id()
            operation = (self._bsmp_update_variables_group, (group_id, ))
            if len(self._queue) == 0 or \
               operation != self._queue.last_operation:
                # append only if queue is empty or if last operation was
                # not a update variables group operation
                operation = (self._bsmp_update_variables_group, (group_id, ))
                self._queue.append(operation)

            # wait for time_interval
            _time.sleep(self._time_interval)

    def _loop_process(self):
        while True:
            self._queue.process()  # Return True of operation was processed.
            n = len(self._queue)
            if n > 0:
                print('queue size: {}'.format(len(self._queue)))
            _time.sleep(0.010)  # sleep a little

    def _select_scan_group_id(self):
        if self._pru.sync_status == self._pru._SYNC_OFF or \
           self._pru.sync_mode == self._pru.SYNC_CYCLE:
            return 3
        else:
            return 4

    def _get_time_interval(self):
        if self._pru.sync_status == self._pru._SYNC_OFF or \
           self._pru.sync_mode == self._pru.SYNC_CYCLE:
            return 1.0/self._FREQ_SCAN  # [s]
        else:
            return 1.0/self._FREQ_RAMP  # [s]

    # --- BSMP communication methods ---

    def _bsmp_update_variables_group(self, group_id):

        ack, data = dict(), dict()

        # --- send request to serial line
        # t0 = _time.time()
        for id in self._device_ids:
            ack[id], data[id] = \
                self._bsmp[id].read_group_variables(group_id=group_id)
        # dt = _time.time() - t0
        # print('bsmp comm time in update: {:.4f} ms'.format(1000*dt))

        # --- process ack
        for v in ack.values():
            if v != Response.ok:
                return False

        # --- if ack is ok, update variables
        var_ids = self._groups[group_id]
        for id in self._device_ids:
            values = data[id]
            for i in range(len(values)):
                var_id = var_ids[i]
                self._variables_values[id][var_id] = values[i]


def create_BBBController():
    """Return a BBB."""
    bbb = BBBController(bsmp_entities=FBPEntities(),
                        device_ids=BBB1_device_ids)
    return bbb


def main():
    """Run."""
    bbb = create_BBBController()
    print('pru_sync_status: {}'.format(bbb.pru.sync_status))
    # bbb.pru.sync_start()


if __name__ == "__main__":
    main()
