"""Power supply controller classes."""

import time as _time
import random as _random
from siriuspy import util as _util
from siriuspy.bsmp import Const as _ack
from siriuspy.csdevice.pwrsupply import max_wfmsize as _max_wfmsize
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ps_opmode as _ps_opmode
from siriuspy.csdevice.pwrsupply import ps_cycle_type as _ps_cycle_type
from siriuspy.pwrsupply.bsmp import Const as _BSMPConst
from siriuspy.pwrsupply.bsmp import PSCStatus as _PSCStatus
from siriuspy.pwrsupply.bsmp import get_variables_FBP as _get_variables_FBP


__version__ = _util.get_last_commit_hash()


class PSCommInterface:
    """Communication interface class for power supplies."""

    # TODO: should this class have its own python module?
    # TODO: this class is not specific to PS! its name should be updated to
    # something line CommInterface or IOCConnInterface. In this case the class
    # should be moved to siriuspy.util or another python module.

    # --- public interface ---

    def __init__(self):
        """Init method."""
        self._callbacks = {}

    @property
    def connected(self):
        """Return connection status."""
        return self._connected()

    def read(self, field):
        """Return field value."""
        raise NotImplementedError

    def write(self, field, value):
        """Write value to a field.

        Return write value if command suceeds or None if it fails.
        """
        raise NotImplementedError

    def add_callback(self, func, index=None):
        """Add callback function."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        if index is None:
            index = 0 if len(self._callbacks) == 0 \
                else max(self._callbacks.keys()) + 1
        self._callbacks[index] = func

    # --- virtual private methods ---

    def _connected(self):
        raise NotImplementedError


class ControllerIOC(PSCommInterface):
    """ControllerIOC class.

        This class implements methods and attributes to interact with power
    supply controllers (ControllerPS) through the serial line (SeriaConn).
    It can be used with any kind of power supply (any value of psmodel).
    """

    _WAIT_TURN_ON_OFF = 0.3  # [s]
    _WAIT_RESET_INTLCKS = 0.1  # [s]

    # conversion dict from PS fields to DSP properties for read method.
    _read_field2func = {
        'Version-Cte': '_get_firmware_version',
        'CtrlMode-Mon': '_get_ctrlmode',
        'PwrState-Sts': '_get_pwrstate',
        'OpMode-Sts': '_get_opmode',
        'Current-RB': '_get_ps_setpoint',
        'CurrentRef-Mon': '_get_ps_reference',
        'Current-Mon': '_get_i_load',
        'IntlkSoft-Mon': '_get_ps_soft_interlocks',
        'IntlkHard-Mon': '_get_ps_hard_interlocks',
        'WfmIndex-Mon': '_get_wfmindex',
        'WfmData-RB': '_get_wfmdata',
        'CycleEnbl-RB': '_get_cycle_enable',
        'CycleType-Sts': '_get_cycle_type',
        'CycleNrCycles-RB': '_get_cycle_num_cycles',
        'CycleIndex-Mon': '_get_cycle_n',
        'CycleFreq-RB': '_get_cycle_freq',
        'CycleAmpl-RB': '_get_cycle_amplitude',
        'CycleOffset-RB': '_get_cycle_offset',
        'CycleAuxParam-RB': '_get_cycle_aux_param',
    }

    _write_field2func = {
        'PwrState-Sel': '_set_pwrstate',
        'OpMode-Sel': '_set_opmode',
        'Current-SP': '_set_slowref',
        'WfmData-SP': '_set_wfmdata',
        'Reset-Cmd': '_reset',
        'CycleType-Sel': '_set_cycle_type',
    }

    # --- API: general power supply 'variables' ---

    def __init__(self, serial_comm, ID_device, ps_database):
        """Init method."""
        PSCommInterface.__init__(self)
        self._serial_comm = serial_comm
        self._ID_device = ID_device
        self._ps_db = ps_database
        # self._opmode = _PSConst.OpMode.SlowRef
        # self._wfmdata = [v for v in self._ps_db['WfmData-SP']['value']]

        # ps_status = self._get_ps_status()

        # reset interlocks
        self.cmd_reset_interlocks()

        # --- initializations ---
        # (it was decided that IOC will only read status from PS controller)
        # turn ps on and implicitly close control loop
        # self._set_pwrstate(_PSConst.PwrState.On)
        # set opmode do SlowRef
        # self._set_opmode(_PSConst.OpMode.SlowRef)
        # set reference current to zero
        # self.cmd_set_slowref(0.0)

    @property
    def scanning(self):
        """Return scanning state of serial comm."""
        return self._serial_comm.scanning

    # --- API: power supply 'functions' ---

    def cmd_turn_on(self):
        """PS controller function: turn power supply on."""
        r = self._bsmp_run_function(ID_function=_BSMPConst.turn_on)
        _time.sleep(ControllerIOC._WAIT_TURN_ON_OFF)
        return r

    def cmd_turn_off(self):
        """PS controller function: turn power supply off."""
        r = self._bsmp_run_function(ID_function=_BSMPConst.turn_off)
        _time.sleep(ControllerIOC._WAIT_TURN_ON_OFF)
        return r

    def cmd_open_loop(self):
        """Open DSP control loop."""
        r = self._bsmp_run_function(ID_function=_BSMPConst.open_loop)
        return r

    def cmd_close_loop(self):
        """PS controller command: close DSP control loop."""
        r = self._bsmp_run_function(_BSMPConst.close_loop)
        return r

    def cmd_select_op_mode(self, op_mode):
        """Select pscontroller operation mode."""
        r = self._bsmp_run_function(_BSMPConst.select_op_mode,
                                    op_mode=op_mode)
        return r

    def cmd_reset_interlocks(self):
        """PS controller function: reset interlocks."""
        r = self._bsmp_run_function(_BSMPConst.reset_interlocks)
        _time.sleep(ControllerIOC._WAIT_RESET_INTLCKS)
        return r

    def cmd_set_slowref(self, setpoint):
        """Set SlowRef reference value."""
        r = self._bsmp_run_function(ID_function=_BSMPConst.set_slowref,
                                    setpoint=setpoint)
        return r

    def cmd_cfg_siggen(self,
                       type=None,
                       num_cycles=None,
                       freq=None,
                       amplitude=None,
                       offset=None,
                       aux_param0=None,
                       aux_param1=None,
                       aux_param2=None,
                       aux_param3=None):
        """Configure SigGen parameters."""
        if type is None:
            type = self._bsmp_get_variable(_BSMPConst.siggen_type)
        if num_cycles is None:
            num_cycles = self._bsmp_get_variable(_BSMPConst.siggen_num_cycles)
        if freq is None:
            freq = self._bsmp_get_variable(_BSMPConst.siggen_freq)
        if amplitude is None:
            amplitude = self._bsmp_get_variable(_BSMPConst.siggen_amplitude)
        if offset is None:
            offset = self._bsmp_get_variable(_BSMPConst.siggen_offset)
        param = self._bsmp_get_variable(_BSMPConst.siggen_aux_param)
        if aux_param0 is None:
            aux_param0 = param[0]
        if aux_param1 is None:
            aux_param1 = param[1]
        if aux_param2 is None:
            aux_param2 = param[2]
        if aux_param3 is None:
            aux_param3 = param[3]
        r = self._bsmp_run_function(
            ID_function=_BSMPConst.cfg_siggen,
            type=type,
            num_cycles=num_cycles,
            freq=freq,
            amplitude=amplitude,
            offset=offset,
            aux_param0=aux_param0,
            aux_param1=aux_param1,
            aux_param2=aux_param2,
            aux_param3=aux_param3)
        return r

    # --- API: public properties and methods ---

    def read(self, field):
        """Return value of a field."""
        if field in ControllerIOC._read_field2func:
            func = getattr(self, ControllerIOC._read_field2func[field])
            value = func()
            return value
        else:
            print('Invalid controller.reader of {}'.format(field))

    def write(self, field, value):
        """Write value to a field."""
        if field in ControllerIOC._write_field2func:
            func = getattr(self, ControllerIOC._write_field2func[field])
            ret = func(value)
            return ret

    # --- private methods ---
    #     These are the functions that all subclass have to implement!

    def _connected(self):
        """Return status of connection with BSMP slaves."""
        return self._serial_comm.get_connected(self._ID_device)

    def _get_wfmdata(self):
        wfmdata = self._serial_comm.get_wfmdata(self._ID_device)
        return wfmdata[:]

    def _get_wfmindex(self):
        return self._serial_comm.sync_pulse_count

    def _get_firmware_version(self):
        # get firmaware version from PS controller and prepend package
        # version number (IOC version)
        value = self._bsmp_get_variable(_BSMPConst.firmware_version)
        firmware_version = 'ioc:' + __version__ + ' ' + value
        return firmware_version

    def _get_ps_status(self):
        return self._bsmp_get_variable(_BSMPConst.ps_status)

    def _get_ps_setpoint(self):
        return self._bsmp_get_variable(_BSMPConst.ps_setpoint)

    def _get_ps_reference(self):
        return self._bsmp_get_variable(_BSMPConst.ps_reference)

    def _get_cycle_enable(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_enable)

    def _get_cycle_type(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_type)

    def _get_cycle_num_cycles(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_num_cycles)

    def _get_cycle_n(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_n)

    def _get_cycle_freq(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_freq)

    def _get_cycle_amplitude(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_amplitude)

    def _get_cycle_offset(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_offset)

    def _get_cycle_aux_param(self):
        return self._bsmp_get_variable(_BSMPConst.siggen_aux_param)

    def _get_ps_soft_interlocks(self):
        return self._bsmp_get_variable(_BSMPConst.ps_soft_interlocks)

    def _get_ps_hard_interlocks(self):
        return self._bsmp_get_variable(_BSMPConst.ps_hard_interlocks)

    def _get_i_load(self):
        return self._bsmp_get_variable(_BSMPConst.i_load)

    def _get_v_load(self):
        return self._bsmp_get_variable(_BSMPConst.v_load)

    def _get_v_dclink(self):
        return self._bsmp_get_variable(_BSMPConst.v_dclink)

    def _bsmp_get_variable(self, ID_variable):
        # read ps_variable as mirrored in the serial_comm object.
        value = self._serial_comm.get_variable(
            ID_device=self._ID_device,
            ID_variable=ID_variable)
        return value

    def _bsmp_run_function(self, ID_function, **kwargs):
        # check if ps is in remote ctrlmode
        if not self._ps_interface_in_remote():
            return
        kwargs.update({'ID_function': ID_function})
        self._serial_comm.put(ID_device=self._ID_device,
                              ID_cmd=0x50,
                              kwargs=kwargs)

    def _get_ctrlmode(self):
        psc_status = _PSCStatus(self._get_ps_status())
        value = psc_status.interface
        return value

    def _get_pwrstate(self):
        psc_status = _PSCStatus(self._get_ps_status())
        value = psc_status.ioc_pwrstate
        return value

    def _get_opmode(self):
        psc_status = _PSCStatus(self._get_ps_status())
        value = psc_status.ioc_opmode
        return value

    def _reset(self, value):
        self.cmd_reset_interlocks()

    def _set_pwrstate(self, value):
        """Set pwrstate state."""
        if not self._ps_interface_in_remote():
            return
        value = int(value)
        if value == _PSConst.PwrState.Off:
            self.cmd_turn_off()
        elif value == _PSConst.PwrState.On:
            # turn ps on
            self.cmd_turn_on()
            # close control loop
            self.cmd_close_loop()
        return value

    def _set_opmode(self, value):
        """Set opmode state."""
        # print('1. set_opmode', value)
        if not self._ps_interface_in_remote():
            return
        value = int(value)
        if not(0 <= value < len(_ps_opmode)):
            return None
        # set opmode state
        # print('2. set_opmode', value)
        if self._get_pwrstate() == _PSConst.PwrState.On:
            psc_status = _PSCStatus(self._get_ps_status())
            psc_status.ioc_opmode = value
            op_mode = psc_status.state
            # print('3. set_opmode', op_mode)
            self.cmd_select_op_mode(op_mode=op_mode)
        return value

    def _set_slowref(self, value):
        if not self._ps_interface_in_remote():
            return
        value = max(self._ps_db['Current-SP']['lolo'], value)
        value = min(self._ps_db['Current-SP']['hihi'], value)
        self.cmd_set_slowref(setpoint=value)

    def _set_cycle_type(self, value):
        """Set CycleType."""
        if not self._ps_interface_in_remote():
            return
        value = int(value)
        if not(0 <= value < len(_ps_cycle_type)):
            return None
        self.cmd_cfg_siggen(type=value)
        return value

    def _set_wfmdata(self, value):
        if isinstance(value, (int, float)):
            value = [value, ]
        elif len(value) > _max_wfmsize:
            value = value[:_max_wfmsize]
        self._wfmdata = value[:]
        self._serial_comm.set_wfmdata(self._ID_device, self._wfmdata)
        return value

    def _ps_interface_in_remote(self):
        psc_status = _PSCStatus(self._get_ps_status())
        interface = psc_status.interface
        return interface == _PSConst.Interface.Remote


class PSState:
    """Power supply state.

    Objects of this class have a dictionary that stores the state of
    power supplies, as defined by its list of BSMP variables.
    """

    # TODO: should this class be moved to bsmp.py module?

    def __init__(self, variables):
        """Init method."""
        self._state = {}
        for ID_variable, variable in variables.items():
            name, type_t, writable = variable
            if type_t == _BSMPConst.t_float:
                value = 0.0
            elif type_t in (_BSMPConst.t_status,
                            _BSMPConst.t_state,
                            _BSMPConst.t_remote,
                            _BSMPConst.t_model,
                            _BSMPConst.t_uint8,
                            _BSMPConst.t_uint16,
                            _BSMPConst.t_uint32):
                value = 0
            elif type_t == _BSMPConst.t_float4:
                value = [0.0, 0.0, 0.0, 0.0]
            elif type_t == _BSMPConst.t_char128:
                value = 'Simulated-ControllerPS'
            else:
                raise ValueError('Invalid BSMP variable type!')
            self._state[ID_variable] = value

    @property
    def variables(self):
        """Return ps variable IDs."""
        return self._state.keys()

    def __getitem__(self, key):
        """Return value corresponfing to a certain key (ps_variable)."""
        return self._state[key]

    def __setitem__(self, key, value):
        """Set value for a certain key (ps_variable)."""
        self._state[key] = value
        return value


class ControllerPSSim:
    """Simulator of power supply controller.

        This class implements simulation of power supply controllers. These
    controllers respond to BSMP commands from the IOC controller
    (ControllerIOC) sent through the serial line.
    """

    _I_LOAD_FLUCTUATION_RMS = 0.01  # [A]
    # _I_LOAD_FLUCTUATION_RMS = 0.0000  # [A]

    funcs = {
        _BSMPConst.turn_on: '_func_turn_on',
        _BSMPConst.turn_off: '_func_turn_off',
        _BSMPConst.open_loop: '_func_open_loop',
        _BSMPConst.close_loop: '_func_close_loop',
        _BSMPConst.select_op_mode: '_func_select_op_mode',
        _BSMPConst.reset_interlocks: '_func_reset_interlocks',
        _BSMPConst.set_serial_termination: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.sync_pulse: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.set_slowref: '_func_set_slowref',
        _BSMPConst.set_slowref_fbp: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.reset_counters: '_func_reset_counters',
        _BSMPConst.cfg_siggen: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.set_siggen: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.enable_siggen: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.disable_siggen: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.set_slowref_readback: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.set_slowref_fbp_readback: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.set_param: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.get_param: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.save_param_eeprom: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.load_param_eeprom: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.save_param_bank: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.load_param_bank: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.set_dsp_coeffs: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.get_dsp_coeff: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.save_dsp_coeffs_eeprom: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.load_dsp_coeffs_eeprom: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.save_dsp_modules_eeprom: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.load_dsp_modules_eeprom: '_FUNC_NOT_IMPLEMENTED',
        _BSMPConst.reset_udc: '_FUNC_NOT_IMPLEMENTED',
    }

    def __init__(self):
        """Init method."""
        self._state = PSState(variables=_get_variables_FBP())
        self._i_load_fluctuation = 0.0

    @property
    def state(self):
        """Return power supply state."""
        self._update_state()
        state = {variable: self._state[variable] for variable in
                 self._state.variables}
        if _BSMPConst.i_load in state:
            state[_BSMPConst.i_load] += self._i_load_fluctuation
        return state

    def __getitem__(self, key):
        """Return ps variable."""
        state = self.state
        return state[key]

    def exec_function(self, ID_function, **kwargs):
        """Execute powr supply function."""
        if ID_function in ControllerPSSim.funcs:
            # if bsmp function is defined, get corresponding method and run it
            func = getattr(self, ControllerPSSim.funcs[ID_function])
            return func(**kwargs)
        else:
            raise ValueError(
                'Run of {} function not defined!'.format(hex(ID_function)))

    def _update_state(self):
        if ControllerPSSim._I_LOAD_FLUCTUATION_RMS != 0.0:
            self._i_load_fluctuation = \
                _random.gauss(0.0, ControllerPSSim._I_LOAD_FLUCTUATION_RMS)

    def _func_turn_on(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        psc_status = _PSCStatus(status)
        psc_status.ioc_opmode = _PSConst.States.SlowRef
        self._state[_BSMPConst.ps_status] = psc_status.ps_status
        self._state[_BSMPConst.i_load] = \
            self._state[_BSMPConst.ps_reference] + \
            self._i_load_fluctuation
        return _ack.ok, None

    def _func_turn_off(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        psc_status = _PSCStatus(status)
        psc_status.ioc_pwrstate = _PSConst.States.Off
        self._state[_BSMPConst.ps_status] = psc_status.ps_status
        self._state[_BSMPConst.ps_setpoint] = 0.0
        self._state[_BSMPConst.ps_reference] = 0.0
        self._state[_BSMPConst.i_load] = 0.0 + self._i_load_fluctuation
        return _ack.ok, None

    def _func_open_loop(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        psc_status = _PSCStatus(status)
        psc_status.open_loop = 1
        self._state[_BSMPConst.ps_status] = psc_status.ps_status
        return _ack.ok, None

    def _func_close_loop(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        psc_status = _PSCStatus(status)
        psc_status.open_loop = 0
        self._state[_BSMPConst.ps_status] = psc_status.ps_status
        return _ack.ok, None

    def _func_select_op_mode(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        psc_status = _PSCStatus(status)
        psc_status.state = kwargs['op_mode']
        self._state[_BSMPConst.ps_status] = psc_status.ps_status
        return _ack.ok, None

    def _func_reset_interlocks(self, **kwargs):
        self._state[_BSMPConst.ps_soft_interlocks] = 0
        self._state[_BSMPConst.ps_hard_interlocks] = 0
        return _ack.ok, None

    def _func_set_slowref(self, **kwargs):
        self._state[_BSMPConst.ps_setpoint] = kwargs['setpoint']
        self._state[_BSMPConst.ps_reference] = \
            self._state[_BSMPConst.ps_setpoint]
        status = self._state[_BSMPConst.ps_status]
        psc_status = _PSCStatus(status)
        if psc_status.ioc_pwrstate == _PSConst.PwrState.On:
            # i_load <= ps_reference
            self._state[_BSMPConst.i_load] = \
                self._state[_BSMPConst.ps_reference] + self._i_load_fluctuation
        return _ack.ok, None

    def _func_reset_counters(self, **kwargs):
        self._state[_BSMPConst.counter_set_slowref] = 0
        self._state[_BSMPConst.counter_sync_pulse] = 0
        return _ack.ok, None

    def _FUNC_NOT_IMPLEMENTED(self, **kwargs):
        raise NotImplementedError(
            'Run of function not defined!'.format(hex(kwargs['ID_function'])))
