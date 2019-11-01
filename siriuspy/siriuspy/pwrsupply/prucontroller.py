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
# from .bsmp import MAP_MIRROR_2_ORIG_FBP as _mirror_map_fbp
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
    # NOTE: All private methods starting with '_bsmp' string make a direct
    #       write to the serial line.

    _sleep_process_loop = 0.020  # [s]

    # --- public interface ---

    def __init__(self,
                 pru,
                 prucqueue,
                 psmodel,
                 devices,
                 processing=True,
                 scanning=True,
                 freq=None):
        """Init."""
        # --- Init structures ---

        print()
        print('PRUController: struct initialization')
        print('devices: {}'.format(devices))

        # init timetsamp
        self._timestamp_update = _time()

        # init time interval
        time0 = _time()

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
        self._udc, self._parms, self._psupplies = PRUController._init_udc(
            pru, self._psmodel.name, self._device_ids, freq)

        # index of dev_id in self._device_ids for wfmref update
        self._wfm_update = True
        self._wfm_update_dev_idx = 0  # cyclical updates!

        # update time interval attribute
        self._scan_interval = self._get_scan_interval()

        # time interval
        time1 = _time()
        print('TIMING struct init [{:.3f} ms]'.format(
            1000*(time1 - time0)))

        # --- BSMP communication ---

        print()
        print('PRUController: bsmp initialization')
        # init time interval
        time0 = _time()

        # reset power supply controllers (contains first BSMP comm)
        self._bsmp_reset_udc()

        # update state of PRUController from ps controller
        self._bsmp_init_update()

        # time interval
        time1 = _time()
        print('TIMING bsmp init [{:.3f} ms]\n'.format(
            1000*(time1 - time0)))

        # --- Threads ---

        print('PRUController: scan and process threads initialization')
        print()

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

    def timestamp_update(self):
        """Return tmestamp of last device update."""
        return self._timestamp_update
        # psupply = self._psupplies[device_id]
        # with self._lock:
        #     tstamp = psupply.timestamp_update
        # return tstamp

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

        # builds dict of requested values
        values = dict()
        for dev_id in dev_ids:
            if variable_id is None:
                values[dev_id] = self._psupplies[dev_id].variables
            else:
                values[dev_id] = \
                    self._psupplies[dev_id].get_variable(variable_id)

        # make copy
        with self._lock:
            if isinstance(device_ids, int):
                return _dcopy(values[device_ids])
            return _dcopy(values)

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
        psupply = self._psupplies[device_id]
        with self._lock:
            index = psupply.wfmref_mon_index
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
        operation = (self._bsmp_update, ())
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

    @staticmethod
    def _init_udc(pru, psmodel_name, device_ids, freq):

        # create UDC
        udc = _UDC(pru, psmodel_name, device_ids)
        parms = udc.prucparms

        # create PSupply objects
        psupplies = dict()
        for dev_id in device_ids:
            psupplies[dev_id] = _PSupply(psbsmp=udc[dev_id])

        # bypass psmodel default frequencies
        if freq is not None:
            parms.FREQ_SCAN = freq

        # print info on scan frequency
        fstr = ('device_id:{:2d}, scan_freq: {:4.1f} Hz')
        for dev in device_ids:
            freq = 10.0 if freq is None else freq
            print(fstr.format(dev, parms.FREQ_SCAN))
        print()

        return udc, parms, psupplies

    def _init_check_version(self):
        if not self.connected:
            return
        for dev_id in self._device_ids:
            # V_FIRMWARE_VERSION should be defined for all BSMP devices
            psupply = self._psupplies[dev_id]
            _udc_firmware_version = psupply.get_variable(
                self._parms.CONST_PSBSMP.V_FIRMWARE_VERSION)
            _udc_firmware_version = \
                self._udc.parse_firmware_version(_udc_firmware_version)
            if 'Simulation' not in _udc_firmware_version and \
               _udc_firmware_version != _devpckg_firmware_version:
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
            _sleep(self._sleep_process_loop)

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

    def _check_groups(self):
        group_ids = sorted(self._parms.groups.keys())

        # needs to have all default groups
        if len(group_ids) < 3:
            raise ValueError(('Invalid variable group definition: '
                              'default group missing!'))
        # needs to have all consecutive groups
        for i in range(len(group_ids)):
            if i not in group_ids:
                raise ValueError(('Invalid variable group definition: '
                                  'non-consecutive group ids!'))

    # --- private methods: BSMP UART communications ---

    def _bsmp_reset_udc(self):

        # set scan interval
        self._scan_interval = self._get_scan_interval()

        # initialize variable groups (first BSMP comm.)
        self._bsmp_init_devices()

    def _bsmp_init_devices(self):

        # create vars groups list from dict
        groups = PRUController._dict2list_vargroups(self._parms.groups)

        # init time interval
        time0 = _time()

        # 1. reset group of bsmp variables for all devices
        for psupply in self._psupplies.values():
            psupply.reset_variables_groups(groups)

        # time interval
        time1 = _time()
        print('  - bsmp_init_devices (reset groups) [{:.3f} ms]'.format(
            1000*(time1 - time0)))

        # init time interval
        time0 = _time()

        # 2. update psupply groups
        for psupply in self._psupplies.values():
            psupply.update_groups(interval=0.0)

        # time interval
        time1 = _time()
        print('  - bsmp_init_devices (update groups) [{:.3f} ms]'.format(
            1000*(time1 - time0)))

        # init time interval
        time0 = _time()

        # 3. disable DSP from writting to bufsample (uses first device)
        self._udc.bufsample_disable()

        # time interval
        time1 = _time()
        print('  - bsmp_init_devices (bufsample_disable) [{:.3f} ms]'.format(
            1000*(time1 - time0)))

    def _bsmp_update(self):

        # time0 = _time()

        # update timestamp
        self._timestamp_update = _time()

        # update variables
        self._bsmp_update_variables()

        # return of wfm is not to be updated
        if not self._wfm_update:
            return  # does not update wfm!

        # update device wfm curves cyclically
        self._wfm_update_dev_idx = \
            (self._wfm_update_dev_idx + 1) % len(self._device_ids)
        dev_id = self._device_ids[self._wfm_update_dev_idx]
        self._bsmp_update_wfm(dev_id)

        # time1 = _time()
        # print('devices: {}, time {}'.format(
        #     self._device_ids, 1000*(time1 - time0)))

    def _bsmp_update_variables(self):

        # time0 = _time()

        # update variables
        for psupply in self._psupplies.values():
            try:
                psupply.update_variables()
            except _SerialError:
                # no serial connection !
                pass

        # time1 = _time()
        # print('TIMING _bsmp_update_variables [{:.3f} ms]'.format(1000*(time1-time0)))

    def _bsmp_update_wfm(self, device_id):
        """Read curve from devices."""

        # time0 = _time()

        # TODO: Ih this really OK?!
        # copy structure
        # t0 = _time()
        # with self._lock:
        #     psupplies = _dcopy(self._psupplies)
        # t1 = _time()
        # print(1000*(t1-t0))
        psupplies = self._psupplies

        try:
            psupply = psupplies[device_id]
            psupply.update_wfm()
        except _SerialError:
            # no serial connection !
            pass

        # stores updated psupplies dict
        self._psupplies = psupplies  # atomic operation

        # time1 = _time()
        # print('TIMING _bsmp_update_wfm [{:.3f} ms]'.format(1000*(time1-time0)))

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
                        data_len=len(data[dev_id]),
                        data=data[dev_id])
                    # print('ack        : {}'.format(ack[dev_id]))
                    # print('device_id  : {}'.format(dev_id))
                    # print('function_id: {}'.format(function_id))
                    # print('response   : {}'.format(data[dev_id]))
        except _SerialError:
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

        # init time interval
        time0 = _time()

        # initialize variables_values, a mirror state of BSMP devices
        self._bsmp_init_variable_values()

        # time interval
        time1 = _time()
        print('  - bsmp_init_update (variables_values) [{:.3f} ms]'.format(
            1000*(time1 - time0)))

        # init time interval
        time0 = _time()

        # initialize ps curves
        self._bsmp_init_wfm()

        # time interval
        time1 = _time()
        print('  - bsmp_init_update (waveforms) [{:.3f} ms]'.format(
            1000*(time1 - time0)))

        # check if ps controller version is compatible with bsmp.py
        # self._init_check_version()

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

        # read all variable from BSMP devices
        self._bsmp_update_variables()

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
