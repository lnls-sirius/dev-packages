"""BeagleBone Controller.

This module implements classes that are used to do low level BeagleBone
communications, be it with PRU or BSMP requests to power supply controllers
at the other end of the serial line.
"""

import time as _time
from collections import deque as _deque
from collections import namedtuple as _namedtuple
from threading import Thread as _Thread
from threading import Lock as _Lock
from copy import deepcopy as _dcopy


from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Response as _Response
from siriuspy.pwrsupply.pru import PRUInterface as _PRUInterface
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.bsmp import Const as _c
from siriuspy.pwrsupply.bsmp import MAP_MIRROR_2_ORIG as _mirror_map


# TODO: Notes on current behaviour of PRU and Power Supplies:
#
# 01. Currently curve block changes are implemented upon the arrival of the
#     timing trigger that corresponds to the last waveform point.
#     This better preserves magnetic history of the magnet while being
#     able to change the waveform on the fly.
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
# 03. The time taken by the BSMP command 0x12 (read group of variables) with
#     group_id used during RmpWfm mode needs to be measured and 'sync_start'
#     delay chosen appropriatelly.
#
# 04. In order to avoid having many concurrent processes|threads accessing
#     the UART through the PRU library by mistake it is desirable to have a
#     semaphore the PRU memory to guarantee that only one process access it.
#     Think about how this could be implemented in a safe but simple way...

# TODO: discuss with patricia:
#
# 01. What does the 'delay' param in 'PRUserial485.UART_write' mean exactly?
# 02. Request a 'sync_abort' function in the PRUserial485 library.
# 03. Request a semaphore for using the PRU library.


class BSMPOpQueue(_deque):
    """BSMPOpQueue.

    This class manages operations which invoque BSMP communications using
    an append-right, pop-left queue. It also processes the next operation in a
    way as to circumvent the blocking character of UART writes when PRU sync
    mode is on.
    """

    # TODO: maybe methods 'ignore_set' and 'ignore_clear' are not needed!
    # BBBController's scan setter could be set to False instead.

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


class BSMPVarGroups:
    """Beaglebone Variagle groups.

    Namespace to group usefull BSMP variable groups used by BBBController.
    """

    # group ids
    ALL = 0
    READONLY = 1
    WRITEABLE = 2
    ALLRELEVANT = 3
    SYNCOFF = 4
    MIRROR = 5

    SLOWREF = SYNCOFF
    MIGWFM = SYNCOFF
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

    # new variable groups usefull for BBBController.
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


class BBBController:
    """BeagleBone controller.

    This class implements all basic PRU configuration and BSMP communications
    of the BeagleBone computer connected through a serial line to power supply
    controllers.
    """

    # TODO: make class robust to BSMP errors!!!
    # TODO: test class in sync on mode and trigger from timing
    # TODO: implement BSMP function executions

    # TODO: Improve update frequency in WfmRamp/MigRamp (done - testing)
    #
    # Gabriel from ELP proposed the idea of a privilegded slave that
    # could define BSMP variables that corresponded to other slaves variables
    # By defining a BSMP variable group with selected variables from all
    # devices we could update all device states with a single BSMP request
    # thus providing higher refresh rates.

    # frequency constants
    FREQ = _namedtuple('FREQ', '')
    FREQ.RAMP = 2.0  # [Hz]
    FREQ.SCAN = 10.0  # [Hz]

    # PRU constants
    SYNC = _namedtuple('SYNC', '')
    SYNC.OFF = _PRUInterface._SYNC_OFF
    SYNC.ON = _PRUInterface._SYNC_ON
    SYNC.MIGINT = _PRUInterface.SYNC_MIGINT
    SYNC.MIGEND = _PRUInterface.SYNC_MIGEND
    SYNC.RMPINT = _PRUInterface.SYNC_RMPINT
    SYNC.RMPEND = _PRUInterface.SYNC_RMPEND
    SYNC.CYCLE = _PRUInterface.SYNC_CYCLE

    # tuple with implemented modes
    SYNC.MODES = (SYNC.OFF, SYNC.MIGEND, SYNC.RMPEND, SYNC.CYCLE)

    # BSMP variable constants
    BSMP = _c

    # BSMP variable group constants
    VGROUPS = BSMPVarGroups

    # shortcuts, local variables and constants

    # TODO: check with ELP group how short these delays can be
    _delay_turn_on_off = 0.3  # [s]
    _delay_loop_open_close = 0.3  # [s]

    _delay_sleep = 0.010  # [s]
    _groups = BSMPVarGroups.groups

    # TODO: solution works only within the name process space
    # look at linux flock facility
    _instance_running = False  # to check if another instance exists

    # default delays for sync modes

    # This this is delay PRU observes right after finishing writting to UART
    # the BSMP broadcast command 0x0F 'sync_pulse' before processing the UART
    # buffer again. This delay has to be longer than the duration of the
    # controller's response to 'sync_pulse'.
    _delay_func_sync_pulse = 100  # [us]
    _pru_delays = dict()
    _pru_delays[SYNC.MIGINT] = None  # This mode is not implemented
    _pru_delays[SYNC.MIGEND] = _delay_func_sync_pulse
    _pru_delays[SYNC.RMPINT] = None  # This mode is not implemented
    _pru_delays[SYNC.RMPEND] = _delay_func_sync_pulse
    _pru_delays[SYNC.CYCLE] = _delay_func_sync_pulse

    # lock attribute to be used when accessing _variables_values
    _lock = _Lock()

    # --- public interface ---

    def __init__(self, bsmp_entities, device_ids,
                 simulate=False, processing=True, scanning=True):
        """Init."""
        # check if another instance is running
        self._check_instance()

        # store simulation mode
        self._simulate = simulate

        # sort list of device ids
        self._device_ids = sorted(device_ids)

        # create PRU (sync mode off).
        self._initialize_pru()

        # initialize BSMP
        self._initialize_bsmp(bsmp_entities)

        # initialize BSMP devices
        self._initialize_devices()

        # operation queue
        self._queue = BSMPOpQueue()

        # scan thread
        self._last_device_scanned = len(self._device_ids)  # next is the first
        self._last_operation = None  # registers last operation
        self._thread_scan = _Thread(target=self._loop_scan, daemon=True)
        self._scanning = scanning
        self._thread_scan.start()

        # process thread
        self._thread_process = _Thread(target=self._loop_process, daemon=True)
        self._processing = processing
        self._thread_process.start()

    @property
    def device_ids(self):
        """Device ids."""
        return self._device_ids[:]

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
    def last_operation(self):
        """Return last operation information."""
        return self._last_operation

    # ---- main methods ----

    def read_variable(self, device_id, variable_id=None):
        """Return current mirror of variable values of the BSMP device."""
        # get value
        dev_values = self._variables_values[device_id]
        if variable_id is None:
            values = dev_values
        else:
            values = dev_values[variable_id]

        # lock and make copy of value
        BBBController._lock.acquire()
        values = _dcopy(values)
        BBBController._lock.release()

        return values

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
            return True
        else:
            # does nothing if PRU sync is on, regardless of sync mode.
            return False

    # ---- PRU and BSMP properties, setters and methods ----

    # TODO: improve name of PRU methods and implement additional ones

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
        # test if sync_mode is valid
        if sync_mode not in BBBController.SYNC.MODES:
            raise NotImplementedError('Invalid sync mode {}'.format(
                hex(sync_mode)))

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
        self.scan = False

        while len(self._queue) > 0:
            _time.sleep(5*self._delay_sleep)  # sleep a little

        # update time interval according to new sync mode selected
        self._time_interval = self._get_time_interval()

        # set selected sync mode
        self._pru.sync_start(
            sync_mode=sync_mode,
            sync_address=self._device_ids[0],
            delay=BBBController._pru_delays[sync_mode])

        # accept back new operation requests
        self.scan = True
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
        # TODO: clean this temporary printout.
        n = len(self._queue)
        if n > 50:
            print('BBB queue size: {} !!!'.format(len(self._queue)))

    # --- private methods ---

    def _check_instance(self):
        # check if another instance is running
        if BBBController._instance_running is True:
            errmsg = ('Another instance of BBBController is already in same'
                      ' process space.')
            raise ValueError(errmsg)
        else:
            BBBController._instance_running = True

    def _initialize_pru(self):

        if self._simulate:
            raise NotImplementedError
        else:
            self._pru = _PRU()
        self._time_interval = self._get_time_interval()

    def _initialize_bsmp(self, bsmp_entities):

        # TODO: deal with BSMP comm errors at init!!

        # prune from mirror group variables not used
        # TODO: check this code!
        nr_devs = len(self.device_ids)
        var_ids = list(self.VGROUPS.groups[self.VGROUPS.MIRROR])
        for var_id in var_ids:
            if var_id > nr_devs:
                var_ids.remove(var_id)
        self.VGROUPS.groups[self.VGROUPS.MIRROR] = tuple(var_ids)

        # create BSMP devices
        self._bsmp = self._create_bsmp(bsmp_entities)

        # initialize variable groups
        self._initialize_groups()

        # initialize variables_values, a mirror state of BSMP devices
        self._initialize_variable_values(bsmp_entities)

        # TODO: get V_FIRMWARE_VERSION from devices and compare it with
        # pwrsupply.bsmp.__version__

    def _initialize_devices(self):

        # TODO: should something be done here?
        for id in self.device_ids:
            pass

    def _create_bsmp(self, bsmp_entities):
        bsmp = dict()
        for id in self._device_ids:
            # TODO: catch BSMP comm errors
            if self._simulate:
                raise NotImplementedError
            else:
                bsmp[id] = _BSMP(self._pru, id, bsmp_entities)
        return bsmp

    def _initialize_variable_values(self, bsmp_entities):

        # create _variables_values
        gids = sorted(self._groups.keys())
        max_id = max([max(self._groups[gid]) for gid in gids[3:]])
        dev_variables = [None, ] * (1 + max_id)
        self._variables_values = \
            {id: dev_variables[:] for id in self._device_ids}
        # TODO: should we initialize this reading the ps controllers?

        # read all variable from BSMP devices
        self._bsmp_update_variables(device_ids=self._device_ids,
                                    group_id=self.VGROUPS.ALLRELEVANT)

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
            _time.sleep(self._delay_sleep)

    def _select_device_group_ids(self):
        """Return variable group id and device ids for the loop scan."""
        if self._pru.sync_status == self.SYNC.OFF:
            return self._device_ids, self.VGROUPS.SLOWREF
        elif self._pru.sync_mode == self.SYNC.MIGEND:
            return self._device_ids, self.VGROUPS.MIGWFM
        elif self._pru.sync_mode == self.SYNC.RMPEND:
            dev_ids = self._select_next_device_id()
            return dev_ids, self.VGROUPS.RMPWFM
        elif self._pru.sync_mode == self.SYNC.CYCLE:
            return self._device_ids, self.VGROUPS.CYCLE
        else:
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
        return (self._devices_ids[0], )

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
            ack[id], data[id] = \
                self._bsmp[id].read_group_variables(group_id=group_id)
        dtime = _time.time() - t0
        self._last_operation = ('V', dtime,
                                device_ids, group_id)

        # --- make copy of state for updating
        BBBController._lock.acquire()
        copy_var_vals = _dcopy(self._variables_values)
        BBBController._lock.release()

        # --- update variables, if ack is ok
        nr_devs = len(self.device_ids)
        var_ids = self._groups[group_id]
        for id in device_ids:
            if ack[id] == _Response.ok:
                values = data[id]
                for i in range(len(values)):
                    var_id = var_ids[i]
                    # process mirror variables, if the case
                    if group_id == self.VGROUPS.MIRROR:
                        # This code assumes that first entry in each mirror
                        # variable block corresponds to the device with
                        # lowest dev_id, the second entry to the second lowest
                        # dev_id, and so on.
                        # TODO: check with ELP if this is the case (email).
                        mir_dev_idx, mir_var_id = _mirror_map[var_id]
                        if mir_dev_idx <= nr_devs:
                            mir_dev_id = self.device_ids[mir_dev_idx-1]
                            copy_var_vals[mir_dev_id][mir_var_id] = values[i]
                    else:
                        # process original variable
                        copy_var_vals[id][var_id] = values[i]
            else:
                # TODO: update 'connect' state for that device
                pass

        # --- use updated copy
        self._variables_values = copy_var_vals  # atomic operation

    def _bsmp_exec_function(self, device_id, function_id, args=None):
        # --- send func exec request to serial line
        t0 = _time.time()
        # BSMP device's 'execute_function' needs to lock code execution
        # so as to avoid more than one thread reading each other's responses.
        # class BSMP method 'request' should always do that
        ack, values = self._bsmp[device_id].execute_function(function_id, args)
        dtime = _time.time() - t0
        self._last_operation = ('F', dtime,
                                device_id, function_id)

        if ack == _Response.ok:
            #
            # power supplies need time after specific commands before it is
            # able to receive any other command from master.
            #
            # this is the place to give it since if other BSMP messages are
            # sent to the power supply in the meantime it will put the
            # ps controller in a wrong state.
            #
            if function_id in (self.BSMP.F_TURN_ON, self.BSMP.F_TURN_OFF):
                _time.sleep(self._delay_turn_on_off)
            elif function_id in (self.BSMP.F_OPEN_LOOP,
                                 self.BSMP.F_CLOSE_LOOP):
                _time.sleep(self._delay_loop_open_close)

            return values
        else:
            # TODO: update 'connect' state for that device
            return None
