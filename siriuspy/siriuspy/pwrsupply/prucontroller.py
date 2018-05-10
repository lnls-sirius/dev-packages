"""BeagleBone Controller.

This module implements classes that are used to do low level BeagleBone
communications, be it with PRU or BSMP requests to power supply controllers
at the other end of the serial line.
"""

import time as _time
import random as _random
# import traceback as _traceback
from collections import deque as _deque
# from collections import namedtuple as _namedtuple
from threading import Thread as _Thread
from threading import Lock as _Lock
from copy import deepcopy as _dcopy

from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Response as _Response
from siriuspy.bsmp.exceptions import SerialError as _SerialError
from siriuspy.csdevice.pwrsupply import DEFAULT_WFMDATA as _DEFAULT_WFMDATA
from siriuspy.pwrsupply.pru import Const as _PRUConst
# from siriuspy.pwrsupply.pru import PRUInterface as _PRUInterface
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.bsmp import __version__ as _ps_bsmp_version
from siriuspy.pwrsupply.bsmp import Const as _c
from siriuspy.pwrsupply.bsmp import MAP_MIRROR_2_ORIG as _mirror_map
from siriuspy.pwrsupply.bsmp import Parameters as _Parameters
from siriuspy.pwrsupply.bsmp import FBPEntities as _FBPEntities
from siriuspy.pwrsupply.status import PSCStatus as _PSCStatus
from siriuspy.pwrsupply.controller import FBP_BSMPSim as _FBP_BSMPSim


# NOTE: On current behaviour of PRU and Power Supplies:
#
# 01. Currently curve block changes are implemented only upon the arrival of
#     timing trigger that corresponds to the last curve point.
#     This better preserves magnetic history of the magnet while being
#     able to change the curve on the fly.
#
# 02. PRU 'sync_stop' aborts the sync mode right away. Maybe it should be
#     renamed to 'sync_abort' and a new command named 'sync_stop' should be
#     provided that implements abort only at the end of the ramp, thus
#     preserving the magnetic history of the magnets sourced my the power
#     supplies. Without this abort at the end of the ramp, the high level
#     has to be responsible for first turning the 2Hz timing trigger off
#     before switching the power supply off the ramp mode.
#     This is prone to operation errors!
#
# 03. In order to avoid having many concurrent processes|threads accessing
#     the UART through the PRU library by mistake it is desirable to have a
#     semaphore the PRU memory to guarantee that only one process access it.
#     Think about how this could be implemented in a safe but simple way...
#
# 04. Change of curves on the fly. In order to allow this blocks 0 and 1 of
#     curves will be used in a cyclic way. This should be transparent for
#     users of the PRUController. At this points only one high level curve
#     for each power supply is implemented. Also we have not implemented yet
#     the possibility of changing the curve length.
#
# 05. Discretization of the current-mon can mascarade measurements of update
#     rates. For testing we should add a small random fluctuation.
#
# 06. In Cycle mode, the high level OpMode-Sts (maybe OpMode-Sel too?) is
#     expected to return to SlowRef automatically without changing CurrentRef.
#     In the current firmware version when the controller executes a
#     SELECT_OP_MODE with SlowRef as argument it automatically sets CurrentRef
#     (V_PS_REFERENCE) to the Current-RB (V_PS_SETPOINT). This is a problem
#     after cycling since we want the IOC to move back to SlowRef automatically
#     So the IOC has to set Current-SP to the same value as SigGen's offset
#     before moving the power supply to Cycle mode. This is being done with the
#     current version of the IOC.


# TODO: discuss with patricia:
#
# 01. What does the 'delay' param in 'PRUserial485.UART_write' mean exactly?
# 02. Request a 'sync_abort' function in the PRUserial485 library.
# 03. Requested new function that reads curves at PRU memory.
#     patricia will work on this.


def parse_firmware_version(version):
    """Process firmware version from BSMP device."""
    # TODO: find an appropriate module/class for this function.
    version = version[:version.index(b'\x00')]
    version = ''.join([chr(ord(v)) for v in version])
    return version


class _BSMPOpQueue(_deque):
    """BSMPOpQueue.

    This class manages operations which invoke BSMP communications using
    an append-right, pop-left queue. It also processes the next operation in a
    way as to circumvent the blocking character of UART writes when PRU sync
    mode is on.

    Each operation processing is a method invoked as a separate thread since
    it run write PRU functions that might block code execution, depending
    on the PRU sync mode. The serial read called and the preceeding write
    function are supposed to be in a locked scope in orde to avoid other
    write executations to read the respond of previous write executions.
    """

    # TODO: maybe methods 'ignore_set' and 'ignore_clear' are not needed!
    # PRUController's scan setter could be set to False instead.

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
        _BSMPOpQueue._lock.acquire(blocking=True)
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
        _BSMPOpQueue._lock.release()

    def clear(self):
        """Clear deque."""
        self._lock.acquire()
        super().clear()
        self._lock.release()

    def popleft(self):
        """Pop left operation from queue."""
        _BSMPOpQueue._lock.acquire(blocking=True)
        if super().__len__() > 0:
            value = super().popleft()
        else:
            value = None
        _BSMPOpQueue._lock.release()
        return value

    def process(self):
        """Process operation from queue."""
        # first check if a thread is already running
        if self._thread is None or not self._thread.is_alive():
            # no thread is running, we can process queue
            operation = self.popleft()
            if operation is None:
                # but therse is nothing in queue
                return False
            else:
                # process operation taken from queue
                func, args = operation
                self._thread = _Thread(target=func, args=args, daemon=True)
                self._thread.start()
                return True
        else:
            # there an operation being processed:do nothing for now.
            return False


class _BSMPVarGroups:
    """Beaglebone Variagle groups.

    Namespace to group usefull BSMP variable groups used by PRUController.
    """

    # group ids
    ALL = 0
    READONLY = 1
    WRITEABLE = 2
    ALLRELEVANT = 3
    SYNCOFF = 4
    MIRROR = 5

    SLOWREF = SYNCOFF
    MIGWFM = MIRROR
    CYCLE = SYNCOFF
    RMPWFM = MIRROR

    groups = dict()

    # reserved variable groups (not to be used)
    groups[ALL] = (
        # --- common variables
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
        # --- undefined variables
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
        # --- FSB variables ---
        _c.V_PS_SOFT_INTERLOCKS,
        _c.V_PS_HARD_INTERLOCKS,
        _c.V_I_LOAD,
        _c.V_V_LOAD,
        _c.V_V_DCLINK,
        _c.V_TEMP_SWITCHES,
        _c.V_DUTY_CYCLE,
        # --- undefined variables
        _c.V_UNDEF32,
        _c.V_UNDEF33,
        _c.V_UNDEF34,
        _c.V_UNDEF35,
        _c.V_UNDEF36,
        _c.V_UNDEF37,
        _c.V_UNDEF38,
        _c.V_UNDEF39,
        # --- mirror variables ---
        _c.V_PS_STATUS_1,
        _c.V_PS_STATUS_2,
        _c.V_PS_STATUS_3,
        _c.V_PS_STATUS_4,
        _c.V_PS_SETPOINT_1,
        _c.V_PS_SETPOINT_2,
        _c.V_PS_SETPOINT_3,
        _c.V_PS_SETPOINT_4,
        _c.V_PS_REFERENCE_1,
        _c.V_PS_REFERENCE_2,
        _c.V_PS_REFERENCE_3,
        _c.V_PS_REFERENCE_4,
        _c.V_PS_SOFT_INTERLOCKS_1,
        _c.V_PS_SOFT_INTERLOCKS_2,
        _c.V_PS_SOFT_INTERLOCKS_3,
        _c.V_PS_SOFT_INTERLOCKS_4,
        _c.V_PS_HARD_INTERLOCKS_1,
        _c.V_PS_HARD_INTERLOCKS_2,
        _c.V_PS_HARD_INTERLOCKS_3,
        _c.V_PS_HARD_INTERLOCKS_4,
        _c.V_I_LOAD_1,
        _c.V_I_LOAD_2,
        _c.V_I_LOAD_3,
        _c.V_I_LOAD_4,)
    groups[READONLY] = groups[ALL]
    groups[WRITEABLE] = tuple()

    # new variable groups usefull for PRUController.
    groups[ALLRELEVANT] = (
        # --- common variables
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
        # --- FSB variables ---
        _c.V_PS_SOFT_INTERLOCKS,
        _c.V_PS_HARD_INTERLOCKS,
        _c.V_I_LOAD,
        _c.V_V_LOAD,
        _c.V_V_DCLINK,
        _c.V_TEMP_SWITCHES,
        _c.V_DUTY_CYCLE,)
    groups[SYNCOFF] = (
        # =======================================================
        # cmd exec_funcion read_group:
        #   17.2 ± 0.3 ms @ BBB1, 4 ps as measured from Python
        #   180us @ BBB1, 1 ps as measured in the oscilloscope
        # =======================================================
        # --- common variables
        _c.V_PS_STATUS,
        _c.V_PS_SETPOINT,
        _c.V_PS_REFERENCE,
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
        # --- FSB variables ---
        _c.V_PS_SOFT_INTERLOCKS,
        _c.V_PS_HARD_INTERLOCKS,
        _c.V_I_LOAD,
        _c.V_V_LOAD,
        _c.V_V_DCLINK,
        _c.V_TEMP_SWITCHES,)
    groups[MIRROR] = (
        # --- mirror variables ---
        _c.V_PS_STATUS_1,
        _c.V_PS_STATUS_2,
        _c.V_PS_STATUS_3,
        _c.V_PS_STATUS_4,
        _c.V_PS_SETPOINT_1,
        _c.V_PS_SETPOINT_2,
        _c.V_PS_SETPOINT_3,
        _c.V_PS_SETPOINT_4,
        _c.V_PS_REFERENCE_1,
        _c.V_PS_REFERENCE_2,
        _c.V_PS_REFERENCE_3,
        _c.V_PS_REFERENCE_4,
        _c.V_PS_SOFT_INTERLOCKS_1,
        _c.V_PS_SOFT_INTERLOCKS_2,
        _c.V_PS_SOFT_INTERLOCKS_3,
        _c.V_PS_SOFT_INTERLOCKS_4,
        _c.V_PS_HARD_INTERLOCKS_1,
        _c.V_PS_HARD_INTERLOCKS_2,
        _c.V_PS_HARD_INTERLOCKS_3,
        _c.V_PS_HARD_INTERLOCKS_4,
        _c.V_I_LOAD_1,
        _c.V_I_LOAD_2,
        _c.V_I_LOAD_3,
        _c.V_I_LOAD_4,)


class PRUController:
    """Beaglebone controller.

    This class implements all basic PRU configuration and BSMP communications
    of the Beaglebone computer connected through a serial line to power supply
    controllers.
    """

    # TODO: allow variable-size curves
    # TODO: delete random fluctuation added to measurements
    # TODO: it might be possible and usefull to use simulated BSMP but real PRU
    # TODO: test not dcopying self._variables_values in _bsmp_update_variables.
    #       we need lock whole up section in that function that does
    #       updating of _variables_values, though. Also lock other class
    #       properties and methods that access _variables_values or _psc_status

    # NOTES:
    # =====
    #
    # 01. All private methods starting with '_bsmp' string make a direct
    #     write to the serial line.

    # frequency constants
    class FREQ:
        """Namespace for frequency values."""

        RAMP = 2.0  # [Hz]
        SCAN = 10.0  # [Hz]

    # PRU constants
    PRU = _PRUConst

    # BSMP variable constants
    BSMP = _c

    # BSMP variable group constants
    VGROUPS = _BSMPVarGroups

    # shortcuts, local variables and constants

    _default_slowrefsync_sp = _DEFAULT_WFMDATA[0]

    # TODO: check with ELP group how short these delays can be
    _delay_turn_on_off = 0.3  # [s]
    _delay_loop_open_close = 0.3  # [s]
    _delay_remove_groups = 100  # [us]
    _delay_create_group = 100  # [us]
    _delay_read_group_variables = 100  # [us]
    # increasing _delay_sleep from 10 ms to 90 ms decreases CPU usage from
    # 20% to 19.2% at BBB1.
    _delay_sleep = 0.020  # [s]

    _groups = _BSMPVarGroups.groups

    # TODO: solution works only within the name process space
    #       look at linux flock facility for a system-wide solution.
    _instance_running = False  # to check if another instance exists

    # default delays for sync modes

    # This this is delay PRU observes right after finishing writting to UART
    # the BSMP broadcast command 0x0F 'sync_pulse' before processing the UART
    # buffer again. This delay has to be longer than the duration of the
    # controller's response to 'sync_pulse'.

    # TODO: confirm with CON if these delays are appropriate
    _delay_func_sync_pulse = 100  # [us]
    _delay_func_set_slowref_fbp = 100  # [us]
    _pru_delays = dict()
    _pru_delays[PRU.SYNC_MODE.MIGINT] = None  # This mode is not implemented
    _pru_delays[PRU.SYNC_MODE.MIGEND] = _delay_func_set_slowref_fbp
    _pru_delays[PRU.SYNC_MODE.RMPINT] = None  # This mode is not implemented
    _pru_delays[PRU.SYNC_MODE.RMPEND] = _delay_func_set_slowref_fbp
    _pru_delays[PRU.SYNC_MODE.CYCLE] = _delay_func_sync_pulse

    # lock used when accessing _variables_values
    _lock = _Lock()

    # --- public interface ---

    def __init__(self, psmodel, device_ids,
                 simulate=False,
                 processing=True,
                 scanning=True,
                 reset=True):
        """Init."""
        # check if another instance is running
        PRUController._check_instance()

        # store simulation mode
        self._simulate = simulate

        # store psmodel
        self._psmodel = psmodel

        # sorted list of device ids
        if len(device_ids) > 4:
            raise ValueError('Number of device ids exceeds maximum!')
        self._device_ids = sorted(device_ids)

        # conversion of ps status to high level properties
        self._psc_state = {}
        for id in self.device_ids:
            self._psc_state[id] = _PSCStatus()

        # create PRU (sync mode off).
        self._initialize_pru()

        # initialize BSMP
        self._initialize_bsmp()

        # reset power supply controllers
        # TODO: this should be invoked in the case of IOC setting state of HW
        if reset is True:
            self._bsmp_reset_ps_controllers()  # (contains first BSMP comm)

        # update state of PRUController from ps controller
        self._bsmp_init_update()

        # initialize BSMP devices (might contain BSMP comm)
        self._initialize_devices()

        # operation queue
        self._queue = _BSMPOpQueue()

        # define scan thread
        self._last_device_scanned = len(self._device_ids)  # next is the first
        self._last_operation = None  # registers last operation
        self._thread_scan = _Thread(target=self._loop_scan, daemon=True)
        self._scanning = scanning

        # define process thread
        self._thread_process = _Thread(target=self._loop_process, daemon=True)
        self._processing = processing

        # after all initializations, threads are started
        self._running = True
        self._thread_scan.start()
        self._thread_process.start()

    # --- properties to read and set controller state and access functions ---

    @property
    def device_ids(self):
        """Device ids."""
        return self._device_ids[:]

    @property
    def scan_interval(self):
        """Scan interval."""
        return self._scan_interval

    @property
    def scanning(self):
        """Return scanning state."""
        return self._scanning

    @scanning.setter
    def scanning(self, value):
        """Set scanning state."""
        self._scanning = value

    @property
    def processing(self):
        """Return processing state."""
        return self._processing

    @processing.setter
    def processing(self, value):
        """Set processing state."""
        self._processing = value

    @property
    def queue_length(self):
        """Number of operations currently in the queue."""
        return len(self._queue)

    @property
    def last_operation(self):
        """Return last operation information."""
        return self._last_operation

    @property
    def connected(self):
        """Connection state."""
        return all((self.check_connected(id) for id in self.device_ids))

    def check_connected(self, device_id):
        """Return connection state of a device."""
        # TODO: may not be the true current connection state
        return self._connected[device_id]

    # --- public methods: bbb controller ---

    def disconnect(self):
        """Disconnect to BSMP devices and stop threads."""
        # move PRU sync to off
        self.pru_sync_abort()

        # wait for empty queue
        self._scanning_false_wait_empty_queue()

        # stop processing
        self.processing = False

        # signal threads to finish
        self._running = False

        # instance not running
        PRUController._instance_running = False

    def get_state(self, device_id):
        """Return updated PSCState for a device."""
        PRUController._lock.acquire()
        state = _dcopy(self._psc_state[device_id])
        PRUController._lock.release()
        return state

    # --- public methods: bsmp variable read and func exec ---

    def read_variables(self, device_ids, variable_id=None):
        """
        Return device variables.

        Parameters
        ----------
        device_ids : int, tuple or list
            The BSMP device ids.
        variable_id : int or None, optional.
            The BSMP variable id selected. If not passed all device variables
            will be returned.

        Returns
        -------
        Selected BSMP device variable values.
        """
        # process device_ids
        if isinstance(device_ids, int):
            dev_ids = (device_ids, )
        else:
            dev_ids = device_ids

        # gather selected data
        values = dict()
        for id in dev_ids:
            dev_values = self._variables_values[id]
            if variable_id is None:
                values[id] = dev_values
            else:
                values[id] = dev_values[variable_id]

        # get rid of dict, if a single device_id was passed.
        if isinstance(device_ids, int):
            values = values[device_ids]

        # lock and make copy of value
        # TODO: test if locking is really necessary.
        PRUController._lock.acquire()
        values = _dcopy(values)
        PRUController._lock.release()

        return values

    def exec_functions(self, device_ids, function_id, args=None):
        """
        Append BSMP function executions to opertations queue.

        Parameters
        ----------
        device_ids : int, tuple or list
            The BSMP device ids. It can be a list of ids or a singe id.
        function_id : int
            The BSMP function id to be executed for the devices.
        args : tuple, optional
            The list of BSMP function argument values

        Returns
        -------
        status : bool
            True is operation was queued or False, if operation was rejected
            because of the PRU sync state.
        """
        if self.pru_sync_status == self.PRU.SYNC_STATE.OFF:
            # in PRU sync off mode, append BSM function exec operation to queue
            if isinstance(device_ids, int):
                device_ids = (device_ids, )
            if args is None:
                args = (device_ids, function_id)
            else:
                args = (device_ids, function_id, args)
            operation = (self._bsmp_exec_function, args)
            self._queue.append(operation)
            return True
        else:
            # does nothing if PRU sync is on, regardless of sync mode.
            return False

    # --- public methods: access to PRU properties ---

    @property
    def pru_sync_mode(self):
        """PRU sync mode."""
        return self._pru.sync_mode

    @property
    def pru_sync_status(self):
        """PRU sync status."""
        return self._pru.sync_status

    def pru_sync_start(self, sync_mode):
        """Start PRU sync mode.

        Before starting a sync_mode this method does a number of actions:

        01. Checks if requested mode exists. If not, raises NotImplementedError
        02. Moves sync state to off.
        03. Stops scanning device variables
        04. Waits untill all operations in queue are processed.
        05. Start sync in requested mode
        06. Turn scanning back on again.

        obs: Since operation in queue are processed before changing starting
        the new sync mode, this method can safely be invoked right away after
        any other PRUController method, withou any inserted delay.
        """
        # test if sync_mode is valid
        if sync_mode not in self.PRU.SYNC_MODE.ALL:
            self.disconnect()
            raise NotImplementedError('Invalid sync mode {}'.format(
                hex(sync_mode)))

        # try to abandon previous sync mode gracefully
        if self.pru_sync_status != self.PRU.SYNC_STATE.OFF:
            # --- already with sync mode on.
            if sync_mode != self._pru.sync_mode:
                # --- different sync mode
                # PRU sync is on but it needs sync_mode change
                # first turn off PRY sync mode abruptally
                self.pru_sync_abort()
            else:
                # --- already in selected sync mode
                # TODO: to do nothing is what we want? what about WfmIndex?
                return
        else:
            # --- current sync mode is off
            pass

        # wait for all queued operations to be processed
        self.bsmp_scan()
        self._scanning_false_wait_empty_queue()

        # execute a BSMP read group so that mirror is updated.
        # This is supposedly needed in cases where the last operation
        # in the queue was a function execution.
        # TODO: test this! but is it really necessary?
        self._bsmp_update_variables(self.device_ids,
                                    PRUController.VGROUPS.SYNCOFF)
        self._scanning_false_wait_empty_queue()

        # reset curve index
        self._pru.set_curve_pointer(0)

        # set selected sync mode
        self._pru.sync_start(
            sync_mode=sync_mode,
            sync_address=self._device_ids[0],
            delay=PRUController._pru_delays[sync_mode])

        # update time interval according to new sync mode selected
        self._scan_interval = self._get_scan_interval()

        # accept back new operation requests
        self.scanning = True
        self._queue.ignore_clear()

    def pru_sync_stop(self):
        """Stop PRU sync mode."""
        # TODO: should we do more than what is implemented?
        self._pru.sync_stop()  # TODO: implemented as a sync_abort!!!
        self._scan_interval = self._get_scan_interval()

    def pru_sync_abort(self):
        """Force stop PRU sync mode."""
        # TODO: should we do more than what is implemented?
        self._pru.sync_abort()
        self._scan_interval = self._get_scan_interval()

    @property
    def pru_sync_pulse_count(self):
        """PRU sync pulse count."""
        return self._pru.sync_pulse_count

    @property
    def pru_curve_block(self):
        """PRU curves block index."""
        return self._pru.read_curve_block()

    def pru_curve_read(self, device_id):
        """Read curve of a device from PRU memory."""
        # pass reference to curve, not a copy! this is necessary otherwise
        # it is hard to achieve update rate of 10 Hz of the IOC.
        idx = self.device_ids.index(device_id)
        # curve = _dcopy(self._curves[idx])
        curve = self._curves[idx]
        return curve

    def pru_curve_write(self, device_id, curve):
        """Write curve for a device to the correponding PRU memory."""
        # get index of curve for the given device id
        idx = self.device_ids.index(device_id)

        # if the case, trim or padd existing curves
        n, n0 = len(curve), len(self._curves[idx])
        if n == 0:
            raise ValueError('Invalid empty curve!')
        elif n > n0:
            for i in self.device_ids:
                # padd wfmdata with current last value
                self._curves[i] += [self._curves[i][-1], ] * (n - n0)
        elif n < n0:
            for i in self.device_ids:
                # trim wfmdata
                self._curves[i] += self._curves[i][:n]

        # # for now do not accept changing curve lengths
        # if len(curve) != len(self._curves[idx]):
        #     self.disconnect()
        #     raise NotImplementedError('Change of curve size not implemented')

        # store curve in PRUController attribute
        self._curves[idx] = list(curve)

        # write curve to PRU memory
        self.pru_curve_send()

    def pru_curve_write_slowref_sync(self, setpoints):
        """Write curves for all devices."""
        # TODO: test method!!!
        # create 1-point curves for all power supplies.
        curves = [[setpoint, ] for setpoint in setpoints]
        curves += [[PRUController._default_slowrefsync_sp, ]] * (4-len(curves))

        # select in which block the new curve will be stored
        block_curr = self._pru.read_curve_block()
        block_next = 1 if block_curr == 0 else 0

        self._pru.curve(curves[0],
                        curves[1],
                        curves[2],
                        curves[3],
                        block_next)
        # TODO: do we need a sleep here?

        # select block to be used at next start of ramp
        self._pru.set_curve_block(block_next)

    def pru_curve_send(self):
        """Send PRUController curves to PRU."""
        # select in which block the new curve will be stored
        block_curr = self._pru.read_curve_block()
        block_next = 1 if block_curr == 0 else 0

        self._pru.curve(self._curves[0],
                        self._curves[1],
                        self._curves[2],
                        self._curves[3],
                        block_next)
        # TODO: do we need a sleep here?

        # select block to be used at next start of ramp
        self._pru.set_curve_block(block_next)

    # @property
    # def pru_curve_length(self):
    #     """PRU curves length."""
    #     n = len(self._curves[self.device_ids[0]])
    #     return n

    # --- public methods: access to atomic methods of scan and process loops

    def bsmp_scan(self):
        """Run scan one."""
        # select devices and variable group, defining the read group
        # opertation to be performed
        device_ids, group_id = self._select_device_group_ids()
        operation = (self._bsmp_update_variables,
                     (device_ids, group_id, ))
        if len(self._queue) == 0 or \
           operation != self._queue.last_operation:
            if self.pru_sync_status == self.PRU.SYNC_STATE.OFF:
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

        # n = len(self._queue)
        # if n > 50:
        #     print('BBB queue size: {} !!!'.format(len(self._queue)))

    # --- private methods: initializations ---

    def _scanning_false_wait_empty_queue(self):
        # wait for all queued operations to be processed
        self._queue.ignore_set()  # ignore eventual new operation requests
        self.scanning = False

        while len(self._queue) > 0:
            _time.sleep(5*self._delay_sleep)  # sleep a little

    @staticmethod
    def _check_instance():
        # check if another instance is running
        if PRUController._instance_running is True:
            errmsg = ('Another instance of PRUController is already in same'
                      ' process space.')
            raise ValueError(errmsg)
        else:
            PRUController._instance_running = True

    def _init_disconnect(self):
        # disconnect method to be used before any operation is on the queue.
        self.scanning = False
        self.processing = False
        self.running = False
        PRUController._instance_running = False

    def _initialize_pru(self):

        # create PRU object
        if self._simulate:
            self._pru = _PRUSim()
        else:
            self._pru = _PRU()

        # update time interval attribute
        self._scan_interval = self._get_scan_interval()

        # initialize PRU curves
        # TODO: read curves from PRU memory.
        # CON is working in a PRU library that allows this.
        self._curves = [list(_DEFAULT_WFMDATA),  # 1st power supply
                        list(_DEFAULT_WFMDATA),  # 2nd power supply
                        list(_DEFAULT_WFMDATA),  # 3rd power supply
                        list(_DEFAULT_WFMDATA),  # 4th power supply
                        ]

    def _initialize_bsmp(self):

        # prune variables from mirror group
        self._init_prune_mirror_group()

        # create attribute with state of connections
        self._connected = {id: False for id in self.device_ids}

        # create BSMP devices
        self._bsmp = self._init_create_bsmp_connectors()

    def _bsmp_reset_ps_controllers(self):

        # turn PRU sync off
        self.pru_sync_abort()

        # initialize variable groups (first BSMP comm.)
        self._bsmp_init_groups()

        # init curves in ps controller
        # TODO: somehow this is necessary. if curves are not set in
        # initialization, RMPEND does not work! sometimes the ps controllers
        # are put in a non-responsive state!!!
        self.pru_curve_write(self.device_ids[0], self._curves[0])

    def _initialize_devices(self):

        # TODO: should something be done here?
        for id in self.device_ids:
            pass

    def _init_prune_mirror_group(self):

        # gather mirror variables that will be used
        nr_devs = len(self.device_ids)
        var_ids = []
        for var_id in list(self._groups[self.VGROUPS.MIRROR]):
            dev_idx, _ = _mirror_map[var_id]
            if dev_idx <= nr_devs:
                var_ids.append(var_id)

        # prune from mirror group variables not used
        self._groups[self.VGROUPS.MIRROR] = tuple(var_ids)

    def _init_create_bsmp_connectors(self):
        bsmp = dict()
        for id in self._device_ids:
            if self._simulate:
                # TODO: generalize using bsmp_entities
                bsmp[id] = _FBP_BSMPSim()
            else:
                if self._psmodel == 'FBP':
                    bsmp_entities = _FBPEntities()
                else:
                    # TODO: generalize here!!!
                    bsmp_entities = _FBPEntities()
                bsmp[id] = _BSMP(self._pru, id, bsmp_entities)
        return bsmp

    def _init_check_version(self):
        if not self.connected:
            return
        for id in self.device_ids:
            version = self._variables_values[id][self.BSMP.V_FIRMWARE_VERSION]
            version = parse_firmware_version(version)
            if 'Simulation' not in version and version != _ps_bsmp_version:
                self._init_disconnect()
                errmsg = ('Incompatible BSMP implementation version! '
                          '{} <> {}'.format(version, _ps_bsmp_version))
                raise ValueError(errmsg)

    # --- private methods: scan and process ---

    def _loop_scan(self):
        while self._running:

            # run scan method once
            if self.scanning:
                self.bsmp_scan()

            # update scan interval
            self._scan_interval = self._get_scan_interval()

            # wait for time_interval
            _time.sleep(self._scan_interval)

    def _loop_process(self):
        while self._running:
            if self.processing:
                self.bsmp_process()

            # sleep a little
            _time.sleep(self._delay_sleep)

    def _select_device_group_ids(self):
        """Return variable group id and device ids for the loop scan."""
        if self.pru_sync_status == self.PRU.SYNC_STATE.OFF:
            return self._device_ids, self.VGROUPS.SLOWREF
        elif self._pru.sync_mode == self.PRU.SYNC_MODE.MIGEND:
            dev_ids = self._select_next_device_id()
            return dev_ids, self.VGROUPS.MIGWFM
        elif self._pru.sync_mode == self.PRU.SYNC_MODE.RMPEND:
            dev_ids = self._select_next_device_id()
            return dev_ids, self.VGROUPS.RMPWFM
        elif self._pru.sync_mode == self.PRU.SYNC_MODE.CYCLE:
            return self._device_ids, self.VGROUPS.CYCLE
        else:
            self.disconnect()
            raise NotImplementedError('Sync mode not implemented!')

    def _select_next_device_id(self):
        # TODO: with the mirror var solution this selection is not necessary!
        #       attribute self._last_device_scanned can be deleted.
        #
        # # calc index of next single device to be scanned
        # nr_devs = len(self._device_ids)
        # dev_idx = (self._last_device_scanned + 1) % nr_devs
        # dev_id = self._device_ids[dev_idx]
        # self._last_device_scanned = dev_idx

        # now always return first device to read the selected variables of
        # all power supplies through mirror variables.
        return (self._device_ids[0], )

    def _get_scan_interval(self):
        if self.pru_sync_status == self.PRU.SYNC_STATE.OFF or \
           self.pru_sync_mode == self.PRU.SYNC_MODE.CYCLE:
            return 1.0/self.FREQ.SCAN  # [s]
        else:
            return 1.0/self.FREQ.RAMP  # [s]

    def _serial_error(self, ids, e, operation):

        # print error message to stdout
        # print()
        # print('--- Serial Error in PRUController._bsmp_update_variables')
        # print('------ last_operation: {}'.format(operation))
        # print('------ traceback:')
        # _traceback.print_exc()
        # print('---')
        # print()

        # signal disconnected for device ids.
        for id in ids:
            self._connected[id] = False

    # --- private methods: BSMP UART communications ---

    def _bsmp_update_variables(self, device_ids, group_id):
        """Read a variable group of device(s).

        This method is inserted in the operation queue my the scanning method.
        values of power supply controller variables read with the BSMP command
        are used to update a mirror state in BBBController of the power
        supplies.

        The method is invoked with two group_ids:

        01. group_id = PRUController.VGROUPS.SYNCOFF
            Used for 'SlowRef' and 'Cycle' power supply operation modes.

        02. group_id = PRUController.VGROUPS.MIRROR
            used for 'SlowRefSync', 'RmpWfm' and 'MigWfm' operation modes.
            In this case mirror variables are read from a single device (power
            supply) in order to update a subset of variables for all devices
            at 2 Hz.
        """
        # TODO: profile method in order to reduce its 20% CPU usage in BBB1

        ack, data = dict(), dict()
        # --- send requests to serial line
        t0 = _time.time()
        try:
            # if group_id == self.VGROUPS.RMPWFM:
            #     print('reading mirror variable group for ids:{}...'.format(
            #         device_ids))
            for id in device_ids:
                ack[id], data[id] = self._bsmp[id].read_group_variables(
                    group_id=group_id,
                    timeout=self._delay_read_group_variables)
            # if group_id == self.VGROUPS.RMPWFM:
            #     print('finished reading.')
            tstamp = _time.time()
            dtime = tstamp - t0
            operation = ('V', tstamp, dtime, device_ids, group_id, False)
            self._last_operation = operation
        except (_SerialError, IndexError) as e:
            tstamp = _time.time()
            dtime = tstamp - t0
            operation = ('V', tstamp, dtime, device_ids, group_id, True)
            self._last_operation = operation
            self._serial_error(device_ids, e, operation)
            return

        # TODO: stopping method execution at this point, not processing
        # returned data from controllers, reduce CPU usage from 20% to 11.5%
        # at BBB1.
        # for id in device_ids:
        #     self._connected[id] = False
        # return

        # processing time up to this point: 9 ms @ BBB1
        # print('time1: ', _time.time() - t0)

        # --- make copy of state for updating
        PRUController._lock.acquire()
        copy_var_vals = _dcopy(self._variables_values)
        # copy_var_vals = self._variables_values
        PRUController._lock.release()
        # processing time up to this point: 18.3 ms @ BBB1
        # processing time up to this point (w/o locks): 17.1 ms @ BBB1
        # processing time up to this point (w/o locks,dcopy): 9.0 ms @ BBB1
        #                                                     11% CPU usage.
        # print('time2: ', _time.time() - t0)

        # --- update variables, if ack is ok
        nr_devs = len(self.device_ids)
        var_ids = self._groups[group_id]
        for id in device_ids:
            if ack[id] == _Response.ok:
                self._connected[id] = True
                values = data[id]
                for i in range(len(values)):
                    var_id = var_ids[i]
                    if group_id == self.VGROUPS.MIRROR:
                        # --- update from read of group of mirror variables
                        #
                        # this code assumes that first entry in each mirror
                        # variable block corresponds to the device with
                        # lowest dev_id, the second entry to the second lowest
                        # dev_id, and so on.
                        #
                        mir_dev_idx, mir_var_id = _mirror_map[var_id]
                        if mir_dev_idx <= nr_devs:
                            mir_dev_id = self.device_ids[mir_dev_idx-1]
                            copy_var_vals[mir_dev_id][mir_var_id] = values[i]
                    else:
                        # --- update from read of other variables groups
                        copy_var_vals[id][var_id] = values[i]

                # add random fluctuation to V_I_LOAD variables (tests)
                # in order to avoid measuring wrong update rates due to
                # power supply discretization of current readout.
                # TODO: turn off added random fluctuations.
                # commenting out this fluctuation cpu usage is reduced from
                # 20% to 19.5% at BBB1
                copy_var_vals[id][self.BSMP.V_I_LOAD] += \
                    0.00001*_random.uniform(-1.0, +1.0)

            else:
                self._connected[id] = False
        # processing time up to this point: 19.4 ms @ BBB1
        # print('time3: ', _time.time() - t0)

        # update psc_state
        for id in self.device_ids:
            self._psc_state[id].ps_status = \
                copy_var_vals[id][self.BSMP.V_PS_STATUS]

        # --- use updated copy
        self._variables_values = copy_var_vals  # atomic operation
        # processing time up to this point: 20.4 ms @ BBB1
        # print('time4: ', _time.time() - t0)

        # PRUController._lock.release()

    def _bsmp_exec_function(self, device_ids, function_id, args=None):
        # --- send func exec request to serial line

        # BSMP device's 'execute_function' needs to lock code execution
        # so as to avoid more than one thread reading each other's responses.
        # class BSMP method 'request' should always do that

        ack, data = dict(), dict()

        # --- send requests to serial line
        t0 = _time.time()
        try:
            for id in device_ids:
                ack[id], data[id] = \
                    self._bsmp[id].execute_function(function_id, args)
        except (_SerialError, IndexError):
            print('SerialError exception in {}'.format(
                ('F', device_ids, function_id)))
            return None
        dtime = _time.time() - t0
        self._last_operation = ('F', dtime,
                                device_ids, function_id)

        # --- check if all function executions succeeded.
        success = True
        for id in device_ids:
            connected = (ack[id] == _Response.ok)
            self._connected[id] == connected
            success &= connected

        if success:
            #
            # power supplies need time after specific commands before it is
            # able to receive any other command from master.
            #
            # this is the place to give it since if other BSMP messages are
            # sent to the power supply in the meantime it will put the
            # ps controller in a wrong state.
            #
            if function_id in (self.BSMP.F_TURN_ON, self.BSMP.F_TURN_OFF):
                # print('waiting {} s for TURN_ON or TURN_OFF'.format(
                #     self._delay_turn_on_off))
                _time.sleep(self._delay_turn_on_off)
            elif function_id in (self.BSMP.F_OPEN_LOOP,
                                 self.BSMP.F_CLOSE_LOOP):
                # print('waiting {} s for CLOSE_LOOP or OPEN_LOOP'.format(
                #     self._delay_loop_open_close))
                _time.sleep(self._delay_loop_open_close)
            return data
        else:
            return None

    def _bsmp_read_parameters(self, device_ids, parameter_ids=None):
        # TODO: this method is not being used yet.
        # reads parameters into pdata dictionary
        pdata = {id: {pid: [] for pid in parameter_ids} for id in device_ids}
        for id in device_ids:
            for pid in parameter_ids:
                indices = [0]
                for idx in indices:
                    data = self._bsmp_exec_function((id,),
                                                    self.BSMP.F_GET_PARAM,
                                                    args=(pid, idx))
                    if data[id] is None:
                        return None
                    else:
                        if len(indices) > 1:
                            pdata[id][pid].append(data[id])
                        else:
                            pdata[id][pid] = data[id]

        # update _parameters_values
        for id in pdata:
            for pid in pdata[id]:
                self._parameters_values[id][pid] = pdata[id][pid]

    def _bsmp_init_update(self):

        # initialize variables_values, a mirror state of BSMP devices
        self._bsmp_init_variable_values()

        # check if ps controller version is compatible with bsmp.py
        self._init_check_version()

        # initialize parameters_values, a mirror state of BSMP devices
        # TODO: finish implementation of _bsmp_init_parameters_values!
        # self._bsmp_init_parameters_values()

    def _bsmp_init_groups(self):

        # check if groups have consecutive ids
        groups_ids = sorted(self._groups.keys())
        if len(groups_ids) < 3:
            self._init_disconnect()
            raise ValueError('Invalid variable group definition!')
        for i in range(len(groups_ids)):
            if i not in groups_ids:
                self._init_disconnect()
                raise ValueError('Invalid variable group definition!')

        # loop over bsmp devices
        for id in self._device_ids:
            # remove previous variables groups and fresh ones
            try:
                self._bsmp[id].remove_all_groups(
                    timeout=self._delay_remove_groups)
                self._connected[id] = True
                for group_id in groups_ids[3:]:
                    var_ids = self._groups[group_id]
                    self._bsmp[id].create_group(
                        var_ids, timeout=self._delay_create_group)
            except _SerialError:
                print('_bsmp_init_groups: serial error!')
                self._connected[id] = False

    def _bsmp_init_variable_values(self):

        # create _variables_values
        gids = sorted(self._groups.keys())
        # TODO: try max_id = max([max(self._groups[gid]) for gid in gids)
        max_id = max([max(self._groups[gid]) for gid in gids[3:]])
        dev_variables = [None, ] * (1 + max_id)
        self._variables_values = \
            {id: dev_variables[:] for id in self._device_ids}

        # read all variable from BSMP devices
        self._bsmp_update_variables(device_ids=self._device_ids,
                                    group_id=self.VGROUPS.ALLRELEVANT)

    def _bsmp_init_parameters_values(self, bsmp_entities):

        # create _parameters_values
        self._parameters_values = {id: {} for id in self._device_ids}

        # read from ps controllers
        self._bsmp_update_parameters(device_ids=self._device_ids,
                                     parameter_ids=_Parameters.get_eids())
