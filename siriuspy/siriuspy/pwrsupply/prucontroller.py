"""PRUController.

This module implements classes that are used to do low level BeagleBone
communications, be it with PRU or BSMP requests to power supply controllers
at the other end of the serial line.
"""

from time import sleep as _sleep, time as _time
from copy import deepcopy as _dcopy
from threading import Thread as _Thread
from threading import Lock as _Lock

from siriuspy.bsmp import constants as _const_bsmp
from siriuspy.bsmp import SerialError as _SerialError

from .bsmp import __version__ as _devpckg_firmware_version
from .bsmp import MAP_MIRROR_2_ORIG_FBP as _mirror_map_fbp
from .udc import UDC as _UDC
from .psupply import PSupply as _PSupply


# NOTE: On current behaviour of PRUC and Power Supplies:
#
# 01. Discretization of the current-mon can mascarade measurements of update
#     rates. For testing we should add a small random fluctuation.


class PRUController:
    """Beaglebone controller.

    This class implements all basic PRU configuration and BSMP communications
    of the Beaglebone computer connected through a serial line to power supply
    controllers.
    """
    # TODO: test not dcopying self._variables_values in _bsmp_update_variables.
    #       we need to lock up whole section in that function that does
    #       updating of _variables_values, though. Also to lock up other class
    #       properties and methods that access _variables_values or _psc_status
    # TODO: move scan and process threads to BeagleBone objects. With this
    #       change the code will map to the power supply architecture more
    #       naturally.
    #
    # NOTE: All private methods starting with '_bsmp' string make a direct
    #       write to the serial line.

    # --- shortcuts, local variables and constants

    _delay_sleep = 0.020  # [s]

    _update_wfm_period = 2.0  # [s]

    # --- public interface ---

    def __init__(self,
                 pru,
                 prucqueue,
                 psmodel,
                 devices,
                 processing=True,
                 scanning=True,
                 freqs=None):
        """Init."""
        # --- Init structures ---

        # create lock
        self._lock = _Lock()

        # PRU communication object
        self._pru = pru

        # store power supply model
        self._psmodel = psmodel

        # devices
        self._devices = _dcopy(devices)

        # sorted list of device ids
        self._device_ids = sorted([dev[1] for dev in devices])

        # initialize UDC
        self._udc, self._parms, self._psupplies = \
            self._init_udc(pru, self._psmodel.name, self._device_ids, freqs)

        # prune variables of mirror groups (sync_on mode)
        self._parms.groups = \
            self._init_prune_mirror_group(
                self._psmodel.name, self._device_ids, self._parms.groups)

        # index of dev_id in self._device_ids for wfmref update
        self._wfm_update = True
        self._wfm_update_dev_idx = 0  # cyclical updates!

        # update time interval attribute
        self._scan_interval = self._get_scan_interval()

        # --- BSMP communication ---

        # reset power supply controllers (contains first BSMP comm)
        self._bsmp_reset_udc()

        # update state of PRUController from ps controller
        self._timestamp_update = _time()
        self._bsmp_init_update()

        # --- Threads ---

        # PRUCQueue is of class DequeThread which invoke BSMP communications
        # using an append-right, pop-left queue. It also processes the next
        # operation in a way as to circumvent the blocking character of UART
        # writes when PRU sync mode is on.
        # Each operation processing is a method invoked as a separate thread
        # since it run write PRU functions that might block code execution,
        # depending on the PRU sync mode. The serial read called and the
        # preceeding write function are supposed to be in a locked scope in
        # order to avoid other write executations to read the respond of
        # previous write executions.
        self._queue = prucqueue

        # define process thread
        self._thread_process = _Thread(target=self._loop_process, daemon=True)
        self._processing = processing

        # define scan thread
        self._dev_idx_last_scanned = \
            len(self._device_ids)-1  # the next will be the first bsmp dev
        self._thread_scan = _Thread(target=self._loop_scan, daemon=True)
        self._scanning = scanning

        # after all initializations, threads are started
        self._running = True
        self._thread_process.start()
        self._thread_scan.start()

    # --- properties to read and set controller state and access functions ---

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
        """Store number of operations currently in the queue."""
        return len(self._queue)

    @property
    def params(self):
        """Return PRUController parameters."""
        return self._parms

    @property
    def connected(self):
        """Store connection state."""
        return all((self.check_connected(id) for id in self._device_ids))

    def check_connected(self, device_id):
        """Return connection state of a device."""
        # TODO: may not be the true current connection state
        psupply = self._psupplies[device_id]
        return psupply.connected

    def timestamp_update(self, device_id):
        """Return tmestamp of last device update."""
        # TODO: reimplement this
        # psupply = self._psupplies[device_id]
        # with self._lock:
        #     tstamp = psupply.timestamp_update
        # return tstamp
        return self._timestamp_update

    # --- public methods: bbb controller ---

    def disconnect(self):
        """Disconnect to BSMP devices and stop threads."""
        self._scan_interval = self._get_scan_interval()

        # wait for empty queue
        self._scanning_false_wait_empty_queue()

        # stop processing
        self.processing = False

        # signal threads to finish
        self._running = False

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

        # NOTE: trial to move state to psupply objects
        # # builds dict of requested values
        # values = dict()
        # for dev_id in dev_ids:
        #     if variable_id is None:
        #         values[dev_id] = self._psupplies[dev_id].variables
        #     else:
        #         values[dev_id] = \
        #             self._psupplies[dev_id].get_variable(variable_id)

        # # make copy
        # with self._lock:
        #     if isinstance(device_ids, int):
        #         return _dcopy(values[device_ids])
        #     return _dcopy(values)

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
        with self._lock:
            values = _dcopy(values)

        return values

    def wfm_update_auto_enable(self):
        """Enable wfm updates."""
        self._wfm_update = True

    def wfm_update_auto_disable(self):
        """Disable wfm updates."""
        self._wfm_update = False

    @property
    def wfm_update_auto(self):
        """Return state of wfm_update_auto."""
        return self._wfm_update

    def wfm_update(self, device_ids, interval=None):
        """Queue update wfm curve."""
        if isinstance(device_ids, int):
            device_ids = (device_ids, )
        operation = (self._bsmp_update_wfm, (device_ids, interval, ))
        self._queue.append(operation)
        return True

    def wfm_rb_read(self, device_id):
        """Return wfm_rb curve."""
        psupply = self._psupplies[device_id]
        with self._lock:
            return _dcopy(psupply.wfm_rb)

    def wfmref_mon_read(self, device_id):
        """Return wfm curve."""
        psupply = self._psupplies[device_id]
        with self._lock:
            curve = psupply.wfmref_mon
            # if device_id == 1:
            #     print('update wfmref_mon ', curve[100])
            return _dcopy(curve)

    def wfm_mon_read(self, device_id):
        """Return Wfm-Mon curve."""
        psupply = self._psupplies[device_id]
        with self._lock:
            return _dcopy(psupply.wfm_mon)

    def wfmref_mon_index(self, device_id):
        """Return current index into DSP selected curve."""
        # TODO: this should be done within either psupply or psbsmp!
        # psupply = self._psupplies[device_id]
        # with self._lock:
        #     index = psypply.wfmref_mon_index
        # return index
        psupply = self._psupplies[device_id]
        dev_variables = self._variables_values[device_id]
        with self._lock:
            curve_id = \
                dev_variables[self.params.CONST_PSBSMP.V_WFMREF_SELECTED]
            if curve_id == 0:
                beg = dev_variables[self.params.CONST_PSBSMP.V_WFMREF0_START]
                end = dev_variables[self.params.CONST_PSBSMP.V_WFMREF0_END]
            else:
                beg = dev_variables[self.params.CONST_PSBSMP.V_WFMREF1_START]
                end = dev_variables[self.params.CONST_PSBSMP.V_WFMREF1_END]
        index = psupply.psbsmp.curve_index_calc(beg, end)
        return index

    def wfm_write(self, device_ids, data):
        """Write wfm curves."""
        # in PRU sync off mode, append BSM function exec operation to queue
        if isinstance(device_ids, int):
            device_ids = (device_ids, )
        operation = (self._bsmp_wfm_write, (device_ids, data))
        self._queue.append(operation)
        return True

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

    # --- public methods: access to atomic methods of scan and process loops

    def bsmp_scan(self):
        """Run scan one."""
        # select devices and variable group, defining the read group
        # opertation to be performed
        device_ids, group_id = self._select_device_group_ids()
        operation = (self._bsmp_update,
                     (device_ids, group_id, ))
        if not self._queue or operation != self._queue.last_operation:
            self._queue.append(operation)
            # self._queue.append(operation, unique=True)
        else:
            # does not append if last operation is the same as last one
            # operation appended to queue
            pass

    def bsmp_process(self):
        """Run process once."""
        # process first operation in queue, if any.
        self._queue.process()

    # --- private methods: initializations ---

    def _init_udc(self, pru, psmodel_name, device_ids, freqs):

        # create UDC
        udc = _UDC(pru, psmodel_name, device_ids)
        parms = udc.prucparms

        # create PSupply objects
        psupplies = dict()
        for dev_id in device_ids:
            psupplies[dev_id] = _PSupply(psbsmp=udc[dev_id])

        # bypass psmodel default frequencies
        if freqs is not None:
            parms.FREQ_SCAN = freqs[0]
            parms.FREQ_RAMP = freqs[1]

        # print info on scan frequency
        fstr = ('id:{:2d}, FREQS  sync_off:{:4.1f} Hz  sync_on:{:4.1f} Hz')
        for dev in device_ids:
            freqs = (10, 2) if freqs is None else freqs
            print(fstr.format(dev, *freqs))
        print()

        return udc, parms, psupplies

    def _init_prune_mirror_group(self, psmodel_name, device_ids, groups):

        if psmodel_name != 'FBP':
            return groups

        # gather mirror variables that will be used
        nr_devs = len(device_ids)
        var_ids = []
        for var_id in list(groups[self._parms.MIRROR]):
            dev_idx, _ = _mirror_map_fbp[var_id]
            if dev_idx <= nr_devs:
                var_ids.append(var_id)

        # prune from mirror group variables not used
        groups[self._parms.MIRROR] = tuple(var_ids)

        return groups

    def _scanning_false_wait_empty_queue(self):
        # wait for all queued operations to be processed
        self._queue.ignore_set()  # ignore eventual new operation requests
        self.scanning = False

        while len(self._queue) > 0:
            _sleep(5*self._delay_sleep)  # sleep a little

    def _init_disconnect(self):
        # disconnect method to be used before any operation is on the queue.
        self.scanning = False
        self.processing = False

    def _init_check_version(self):
        if not self.connected:
            return
        for dev_id in self._device_ids:
            # V_FIRMWARE_VERSION should be defined for all BSMP devices
            _udc_firmware_version = self._variables_values[dev_id][
                self._parms.CONST_PSBSMP.V_FIRMWARE_VERSION]
            _udc_firmware_version = \
                self._udc.parse_firmware_version(_udc_firmware_version)
            if 'Simulation' not in _udc_firmware_version and \
               _udc_firmware_version != _devpckg_firmware_version:
                self._init_disconnect()
                errmsg = ('Incompatible bsmp implementation version '
                          'for device id:{}')
                print(errmsg.format(dev_id))
                errmsg = 'lib version: {}'
                print(errmsg.format(_devpckg_firmware_version))
                errmsg = 'udc version: {}'
                print(errmsg.format(_udc_firmware_version))
                print()
                # raise ValueError(errmsg)

    # --- private methods: scan and process ---

    def _loop_scan(self):
        while self._running:

            # run scan method once
            if self.scanning and self._scan_interval != 0:
                self.bsmp_scan()

            # update scan interval
            self._scan_interval = self._get_scan_interval()

            # wait for time_interval
            _sleep(self._scan_interval)

    def _loop_process(self):
        while self._running:
            if self.processing:
                self.bsmp_process()

            # sleep a little
            _sleep(self._delay_sleep)

    def _select_device_group_ids(self):
        """Return variable group id and device ids for the loop scan."""
        return self._device_ids, self._parms.SLOWREF

    def _select_next_device_id(self):
        # select device ids to be read (when not in sync_off mode)
        if self._psmodel.name in ('FBP', ):
            # with the mirror var solution for FBP we can always read only
            # one of them and get updates for all the others
            dev_id = self._device_ids[0]
        else:
            # cycle through bsmp devices
            nr_devs = len(self._device_ids)
            dev_idx = (self._dev_idx_last_scanned + 1) % nr_devs
            dev_id = self._device_ids[dev_idx]
            self._dev_idx_last_scanned = dev_idx
        return (dev_id, )

    def _get_scan_interval(self):
        if self._parms.FREQ_SCAN == 0:
            return 0
        else:
            return 1.0/self._parms.FREQ_SCAN  # [s]

    def _serial_error(self, device_ids):
        # signal disconnected for device ids.
        for dev_id in device_ids:
            psupply = self._psupplies[dev_id]
            psupply._connected = False

    def _update_copy_var_vals(self, device_id, copy_var_vals, nr_devs,
                              value, group_id, var_id):
        if self._psmodel.name == 'FBP' and group_id == self._parms.MIRROR:
            # TODO: generalize this !
            # --- update from read of group of mirror variables
            #
            # this code assumes that first entry in each mirror
            # variable block corresponds to the device with
            # lowest device_id, the second entry to the second lowest
            # device_id, and so on.
            #
            mir_dev_idx, mir_var_id = _mirror_map_fbp[var_id]
            if mir_dev_idx <= nr_devs:
                mir_dev_id = self._device_ids[mir_dev_idx-1]
                copy_var_vals[mir_dev_id][mir_var_id] = value
        else:
            # --- update from read of other variables groups
            copy_var_vals[device_id][var_id] = value

    def _check_groups(self):
        group_ids = sorted(self._parms.groups.keys())

        # needs to have all default groups
        if len(group_ids) < 3:
            self._init_disconnect()
            raise ValueError(('Invalid variable group definition: '
                              'default group missing!'))
        # needs to have all consecutive groups
        for i in range(len(group_ids)):
            if i not in group_ids:
                self._init_disconnect()
                raise ValueError(('Invalid variable group definition: '
                                  'non-consecutive group ids!'))

    # --- private methods: BSMP UART communications ---

    def _bsmp_reset_udc(self):

        self._scan_interval = self._get_scan_interval()

        # initialize variable groups (first BSMP comm.)
        self._bsmp_init_devices()

    def _bsmp_init_devices(self):

        # create vars groups list from dict
        groups = PRUController._dict2list_vargroups(self._parms.groups)

        # 1. reset group of bsmp variables for all devices
        for dev_id in self._device_ids:
            psbsmp = self._udc[dev_id]
            ack, _ = \
                psbsmp.reset_groups_of_variables(groups[3:], add_wfmref_group=True)
            if ack != self._udc.CONST_BSMP.ACK_OK:
                raise ValueError('Could not reset group in device!')

        # 2. disable DSP from writting to bufsample (uses first device)
        self._udc.bufsample_disable()

    def _bsmp_update(self, device_ids, group_id):
        # update
        self._timestamp_update = _time()

        # update variables
        self._bsmp_update_variables(device_ids, group_id)
        # self._bsmp_update_variables_new(device_ids, group_id)

        # return of wfm is not to be updated
        if not self._wfm_update:
            return  # does not update wfm!

        # update device wfm curves cyclically
        self._wfm_update_dev_idx = \
            (self._wfm_update_dev_idx + 1) % len(self._device_ids)
        dev_id = self._device_ids[self._wfm_update_dev_idx]
        self._bsmp_update_wfm([dev_id, ])

    def _bsmp_update_variables_new(self, device_ids, group_id):
        # update variables
        for dev_id, psupply in self._psupplies.items():
            psupply.update_variables()
            self._variables_values[dev_id] = psupply._variables

    def _bsmp_update_variables(self, device_ids, group_id):
        """Read a variable group of device(s).

        This method is inserted in the operation queue my the scanning method.
        values of power supply controller variables read with the BSMP command
        are used to update a mirror state in BBBController of the power
        supplies.

        The method is invoked with two group_ids:

        01. group_id = self._model.SYNCOFF
            Used for 'SlowRef' and 'Cycle' power supply operation modes.

        02. group_id = self._model.MIRROR
            used for 'SlowRefSync', 'RmpWfm' and 'MigWfm' operation modes.
            In this case mirror variables are read from a single device (power
            supply) in order to update a subset of variables for all devices
            at 2 Hz.
        """
        ack, data = dict(), dict()
        # --- send requests to serial line
        try:
            for dev_id in device_ids:
                ack[dev_id], data[dev_id] = \
                    self._udc[dev_id].read_group_of_variables(
                        group_id=group_id)

        except (_SerialError, IndexError):
            print('error!!!')
            self._serial_error(device_ids)
            return

        # --- make copy of state for updating
        with self._lock:
            copy_var_vals = _dcopy(self._variables_values)
            # update psupply connection state.
            for dev_id in device_ids:
                psupply = self._psupplies[dev_id]
                if ack[dev_id] == _const_bsmp.ACK_OK:
                    psupply._connected = True
                else:
                    psupply._connected = False

        # --- update variables, if ack is ok
        nr_devs = len(self._device_ids)
        var_ids = self._parms.groups[group_id]
        for dev_id in device_ids:
            if ack[dev_id] == _const_bsmp.ACK_OK:
                values = data[dev_id]
                for i, value in enumerate(values):
                    # ===
                    # NOTE: fixit!
                    # When changing from SlowRef to RmpWfm mode in TB-04-PS-CH,
                    # 1. i >= len(var_ids)
                    # 2. WfmData-RB != WfmData_SP
                    # try/exception necessary!
                    try:
                        var_id = var_ids[i]
                    except IndexError:
                        print('device_ids:', device_ids)
                        print('group_id:', group_id)
                        print('i:', i)
                        print('var_ids:', var_ids)
                        print('len(values):', len(values))
                    # ===
                    self._update_copy_var_vals(dev_id, copy_var_vals, nr_devs,
                                               value, group_id, var_id)

                # add random fluctuation to V_I_LOAD variables (tests)
                # in order to avoid measuring wrong update rates due to
                # power supply discretization of current readout.
                # NOTE: turn off added random fluctuations.
                # commenting out this fluctuation cpu usage is reduced from
                # 20% to 19.5% at BBB1
                # if self._psmodel.name == 'FBP':
                #     copy_var_vals[id][self._parms.CONST_PSBSMP.V_I_LOAD] \
                #         += 0.00001*_random.uniform(-1.0, +1.0)
                # elif self._psmodel.name == 'FBP_DCLink':
                #     copy_var_vals[id][self._parms.CONST_PSBSMP.V_V_OUT] \
                #         += 0.00001*_random.uniform(-1.0, +1.0)
                # elif self._psmodel.name == 'FAC':
                #     copy_var_vals[id][self._parms.CONST_PSBSMP.V_I_LOAD1] \
                #         += 0.00001*_random.uniform(-1.0, +1.0)
                #     copy_var_vals[id][self._parms.CONST_PSBSMP.V_I_LOAD2] \
                #         += 0.00001*_random.uniform(-1.0, +1.0)

            elif ack[dev_id] == _const_bsmp.ACK_INVALID_ID:
                self._bsmp_init_groups()  # NOTE: necessary?!

        # --- use updated copy
        self._variables_values = copy_var_vals  # atomic operation

    def _bsmp_update_wfm(self, device_ids, interval=None):
        """Read curve from devices."""
        if interval is None:
            interval = self._update_wfm_period
        # copy structure
        with self._lock:
            psupplies = _dcopy(self._psupplies)

        try:
            for dev_id in device_ids:
                psupply = psupplies[dev_id]
                psupply.update_wfm(interval=interval)
        except (_SerialError, IndexError):
            print('bsmp_wfm_update error!')

        # stores updated psupplies dict
        self._psupplies = psupplies  # atomic operation

    def _bsmp_wfm_write(self, device_ids, curve):
        """Write curve to devices."""
        try:
            # write curves
            for dev_id in device_ids:
                psupply = self._psupplies[dev_id]
                curve = psupply.psbsmp.wfmref_mon_write(curve)
                with self._lock:
                    psupply.wfm_rb = curve
                    psupply.update_wfm(interval=0.0)
        except (_SerialError, IndexError):
            print('bsmp_wfm_write error!')
            self._serial_error(device_ids)

    def _bsmp_exec_function(self, device_ids, function_id, args=None):
        # --- send func exec request to serial line

        # BSMP device's 'execute_function' needs to lock code execution
        # so as to avoid more than one thread reading each other's responses.
        # class BSMP method 'request' should always do that

        ack, data = dict(), dict()

        # --- send requests to serial line
        try:
            for dev_id in device_ids:
                ack[dev_id], data[dev_id] = \
                    self._udc[dev_id].execute_function(function_id, args)
                # check anomalous response
                if ack[dev_id] != _const_bsmp.ACK_OK:
                    print('PRUController: anomalous response !')
                    self._udc[dev_id]._anomalous_response(
                        _const_bsmp.CMD_EXECUTE_FUNCTION, ack[dev_id],
                        device_id=dev_id,
                        function_id=function_id,
                        data=data[dev_id])
                    # print('ack        : {}'.format(ack[dev_id]))
                    # print('device_id  : {}'.format(dev_id))
                    # print('function_id: {}'.format(function_id))
                    # print('response   : {}'.format(data[dev_id]))
        except _SerialError:
            print('SerialError exception in {}'.format(
                ('F', device_ids, function_id, args)))
            return None

        # --- check if all function executions succeeded.
        success = True
        for dev_id in device_ids:
            connected = (ack[dev_id] == _const_bsmp.ACK_OK)
            success &= connected

        if success:
            return data
        else:
            return None

    def _bsmp_init_update(self):

        # initialize variables_values, a mirror state of BSMP devices
        # print('disable init_variables!!!')
        self._bsmp_init_variable_values()

        # raise ValueError('!!! Debug stop !!!')

        # initialize ps curves
        self._bsmp_init_wfm()

        # raise ValueError

        # check if ps controller version is compatible with bsmp.py
        self._init_check_version()

        # raise ValueError('!!! Debug stop !!!')

        # initialize parameters_values, a mirror state of BSMP devices
        # TODO: finish implementation of _bsmp_init_parameters_values!
        # self._bsmp_init_parameters_values()

    def _bsmp_init_wfm(self):

        for psupply in self._psupplies.values():

            # update
            psupply.update_wfm(interval=0.0)

            # raise ValueError('!!! Debug stop !!!')

            # registers RB using psupply object
            psupply.wfm_rb = psupply.wfmref_mon

            # raise ValueError('!!! Debug stop !!!')

        # raise ValueError('!!! Debug stop !!!')

        # enable bufsample
        # self._udc.bufsample_enable()

        # raise ValueError('!!! Debug stop !!!')

    def _bsmp_init_variable_values(self):

        # init psupplies variables
        for psupply in self._psupplies.values():
            psupply.update_variables(interval=0.0)

        # create _variables_values
        gids = sorted(self._parms.groups.keys())
        max_id = max([max(self._parms.groups[gid]) for gid in gids[3:]])
        dev_variables = [None, ] * (1 + max_id)
        with self._lock:
            self._variables_values = \
                {dev_id: dev_variables[:] for dev_id in self._device_ids}

        # read all variable from BSMP devices
        self._bsmp_update_variables(device_ids=self._device_ids,
        # self._bsmp_update_variables_new(device_ids=self._device_ids,
                          group_id=self._parms.ALLRELEVANT)

    @staticmethod
    def _dict2list_vargroups(groups_dict):
        group_ids = sorted(groups_dict.keys())
        if len(group_ids) < 3:  # needs to have all default groups
            print('Incorrect variables group definition: '
                  'it does not have all three standard groups!')
            raise ValueError
        for i in range(len(group_ids)):  # consecutive?
            if i not in group_ids:
                print('Incorrect variables group definition: '
                      'it does not have consecutive group ids!')
                raise ValueError
        # create list of variable ids
        groups_list = [groups_dict[gid] for gid in group_ids]
        return groups_list

    # def _bsmp_init_parameters_values(self, bsmp_entities):
    #
    #     # create _parameters_values
    #     self._parameters_values = {id: {} for id in self._device_ids}
    #
    #     # read from ps controllers
    #     self._bsmp_update_parameters(device_ids=self._device_ids,
    #                                  parameter_ids=_Parameters.get_eids())

    # def _bsmp_read_parameters(self, device_ids, parameter_ids=None):
    #     # NOTE: this method is not being used yet.
    #     # reads parameters into pdata dictionary
    #     pdata = {id: {pid: [] for pid in parameter_ids} for id in device_ids}
    #     for id in device_ids:
    #         for pid in parameter_ids:
    #             indices = [0]
    #             for idx in indices:
    #                 data = self._bsmp_exec_function(
    #                     (id,), self._parms.CONST_PSBSMP.F_GET_PARAM,
    #                     args=(pid, idx))
    #                 if data[id] is None:
    #                     return None
    #                 else:
    #                     if len(indices) > 1:
    #                         pdata[id][pid].append(data[id])
    #                     else:
    #                         pdata[id][pid] = data[id]
    #
    #     # update _parameters_values
    #     for id in pdata:
    #         for pid in pdata[id]:
    #             self._parameters_values[id][pid] = pdata[id][pid]
