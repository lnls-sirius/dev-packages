"""Power supply controller classes."""

import time as _time
import random as _random
from siriuspy import util as _util
from siriuspy.bsmp import Const as _ack
from siriuspy.bsmp import BSMP
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ps_opmode as _ps_opmode
from siriuspy.pwrsupply.bsmp import Const as _BSMPConst
from siriuspy.pwrsupply.bsmp import Status as _Status
from siriuspy.pwrsupply.bsmp import get_variables_FBP as _get_variables_FBP


__version__ = _util.get_last_commit_hash()


class PSDevice:
    """Map device to BSMP."""

    def __init__(self):
        self._variables = {}
        self._groups = {}
        self._curves = {}
        self._functions = {}

    def get_variable_id(self, variable):
        return self._variables[variable]

    def get_function_id(self, function):
        return self._functions[function]


class PSController:
    """High level PS controller."""

    def __init__(self, slave_address):
        self._slave_address = slave_address
        self._setpoints = {}
        # self._variables = {}
        self._ps = PSDevice()
        self._bsmp = BSMP()

    # API
    @property
    def setpoints(self):
        """Controller variables."""
        return self._setpoints

    @property
    def variables(self):
        """Device variables."""
        return self.read_all_variables()
        # return self._variables

    def read(self, field):
        """Read a field from device."""
        if field in self._variables:
            return self._read_variable(field)
        elif field in self._setpoints:
            return self._setpoints[field]
        else:
            raise ValueError("Field {} not mapped.".format(field))

    def write(self, field, value):
        """Write to device field.

        True - ok
        False - something went wrong
            Error
            Disonnection
        """
        value = self._handle_write(field, value)
        if value is None:
            return False
        if field in self._variables:
            return True
        elif field in self._setpoints:
            return True
        else:
            raise ValueError("Field {} not mapped.".format(field))

    def read_all_variables(self):
        """Read all variable from group 0."""
        return self._bsmp.read_variables_group(self._slave_address, 0)

    # Private
    def _read_variable(self, field):
        id_variable = self._ps.get_variable_id(field)
        return self._bsmp.read_variable(self._slave_address, id_variable)
        # return self._variables[field]

    # def _read_setpoint(self, field):
    #     return self._setpoints[field]


class PSCommInterface:
    """Communication interface class for power supplies."""

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

    This class implements

    """

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
    }

    _write_field2func = {
        'PwrState-Sel': '_set_pwrstate',
        'OpMode-Sel': '_set_opmode',
        'Current-SP': 'cmd_set_slowref',
        'WfmData-SP': '_set_wfmdata',
        'Reset-Cmd': '_reset',
    }

    # --- API: general power supply 'variables' ---

    def __init__(self, serial_comm, ID_device, ps_database):
        """Init method."""
        PSCommInterface.__init__(self)
        self._serial_comm = serial_comm
        self._ID_device = ID_device
        self._ps_db = ps_database
        # self._opmode = _PSConst.OpMode.SlowRef
        self._wfmdata = [v for v in self._ps_db['WfmData-SP']['value']]

        # ps_status = self._get_ps_status()

        # reset interlocks
        self.cmd_reset_interlocks()

        # turn ps on and implicitly close control loop
        # self.pwrstate = _PSConst.PwrState.On
        # self._pwrstate = _Status.pwrstate(ps_status)

        # set opmode do SlowRef
        # self.opmode = _PSConst.OpMode.SlowRef
        # self._opmode = _Status.opmode(ps_status)

        # set reference current to zero
        # self.cmd_set_slowref(0.0)

    @property
    def scanning(self):
        """Return scanning state of serial comm."""
        return self._serial_comm.scanning

    # --- API: power supply 'functions' ---

    def cmd_turn_on(self):
        """Turn power supply on."""
        r = self._bsmp_run_function(ID_function=_BSMPConst.turn_on)
        _time.sleep(0.3)  # Eduardo-CON said it is necessary!
        return r

    def cmd_turn_off(self):
        """Turn power supply off."""
        ret = self._bsmp_run_function(ID_function=_BSMPConst.turn_off)
        _time.sleep(0.3)  # Eduardo-CON said it is necessary!
        return ret

    def cmd_open_loop(self):
        """Open DSP control loop."""
        return self._bsmp_run_function(ID_function=_BSMPConst.open_loop)

    def cmd_close_loop(self):
        """Close DSP control loop."""
        ret = self._bsmp_run_function(_BSMPConst.close_loop)
        return ret

    def cmd_reset_interlocks(self):
        """Reset interlocks."""
        r = self._bsmp_run_function(_BSMPConst.reset_interlocks)
        _time.sleep(0.1)  # Eduardo-CON said it is necessary!
        return r

    def cmd_set_slowref(self, setpoint):
        """Set SlowRef reference value."""
        if not self._ps_interface_in_remote():
            return
        setpoint = max(self._ps_db['Current-SP']['lolo'], setpoint)
        setpoint = min(self._ps_db['Current-SP']['hihi'], setpoint)
        self._bsmp_run_function(ID_function=_BSMPConst.set_slowref,
                                setpoint=setpoint)
        return setpoint

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
        return self._wfmdata

    def _get_wfmindex(self):
        return self._serial_comm.sync_pulse_count

    def _get_firmware_version(self):
        # value = self._bsmp_get_variable(_BSMPConst.firmware_version)
        # firmware_version = __version__ + ':' + '-'.join([c for c in value])
        firmware_version = __version__ + ':' + '0x00:0x00'
        return firmware_version

    def _get_ps_status(self):
        return self._bsmp_get_variable(_BSMPConst.ps_status)

    def _get_ps_setpoint(self):
        return self._bsmp_get_variable(_BSMPConst.ps_setpoint)

    def _get_ps_reference(self):
        return self._bsmp_get_variable(_BSMPConst.ps_reference)

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
        ps_status = self._get_ps_status()
        value = _Status.interface(ps_status)
        return value

    def _get_pwrstate(self):
        ps_status = self._get_ps_status()
        value = _Status.pwrstate(ps_status)
        return value

    def _get_opmode(self):
        ps_status = self._get_ps_status()
        value = _Status.opmode(ps_status)
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
        """Set pwrstate state."""
        # print('1. set_opmode', value)
        if not self._ps_interface_in_remote():
            return
        value = int(value)
        if not(0 <= value < len(_ps_opmode)):
            return None
        # set opmode state
        # print('2. set_opmode', value)
        if self._get_pwrstate() == _PSConst.PwrState.On:
            ps_status = self._get_ps_status()
            ps_status = _Status.set_opmode(ps_status, value)
            op_mode = _Status.opmode(ps_status)
            # print('3. set_opmode', op_mode)
            self._cmd_select_op_mode(op_mode=op_mode)
        return value

    def _set_wfmdata(self, value):
        self._wfmdata = value[:]
        self._serial_comm.set_wfmdata(self._ID_device, self._wfmdata)
        return value

    def _cmd_select_op_mode(self, op_mode):
        return self._bsmp_run_function(_BSMPConst.select_op_mode,
                                       op_mode=op_mode)

    def _ps_interface_in_remote(self):
        ps_status = self._get_ps_status()
        interface = _Status.interface(ps_status)
        return interface == _PSConst.Interface.Remote


class PSState:
    """Power supply state.

    Objects of this class have a dictionary that stores the state of
    power supplies, as defined by its list of BSMP variables.
    """

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
                value = [chr(0), ] * 128
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
    """Simulator of power supply controller."""

    _I_LOAD_FLUCTUATION_RMS = 0.01  # [A]
    # _I_LOAD_FLUCTUATION_RMS = 0.0000  # [A]

    funcs = {
        _BSMPConst.set_slowref: '_func_set_slowref',
        _BSMPConst.select_op_mode: '_func_select_op_mode',
        _BSMPConst.turn_on: '_func_turn_on',
        _BSMPConst.turn_off: '_func_turn_off',
        _BSMPConst.reset_interlocks: '_func_reset_interlocks',
        _BSMPConst.close_loop: '_func_close_loop',
        # functions not implemented  yet:
        _BSMPConst.set_serial_termination: '_func_not_implemented',
        _BSMPConst.sync_pulse: '_func_not_implemented',
        _BSMPConst.set_slowref_fbp: '_func_not_implemented',
        _BSMPConst.reset_counters: '_func_not_implemented',
        _BSMPConst.cfg_siggen: '_func_not_implemented',
        _BSMPConst.set_siggen: '_func_not_implemented',
        _BSMPConst.enable_siggen: '_func_not_implemented',
        _BSMPConst.disable_siggen: '_func_not_implemented',
        _BSMPConst.set_slowref_readback: '_func_not_implemented',
        _BSMPConst.set_slowref_fbp_readback: '_func_not_implemented',
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

    def _func_set_slowref(self, **kwargs):
        self._state[_BSMPConst.ps_setpoint] = kwargs['setpoint']
        self._state[_BSMPConst.ps_reference] = \
            self._state[_BSMPConst.ps_setpoint]
        status = self._state[_BSMPConst.ps_status]
        if _Status.pwrstate(status) == _PSConst.PwrState.On:
            # i_load <= ps_reference
            self._state[_BSMPConst.i_load] = \
                self._state[_BSMPConst.ps_reference] + self._i_load_fluctuation
        return _ack.ok, None

    def _func_select_op_mode(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        status = _Status.set_state(status, kwargs['op_mode'])
        self._state[_BSMPConst.ps_status] = status
        return _ack.ok, None

    def _func_turn_on(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        status = _Status.set_state(status, _PSConst.States.SlowRef)
        self._state[_BSMPConst.ps_status] = status
        self._state[_BSMPConst.i_load] = \
            self._state[_BSMPConst.ps_reference] + \
            self._i_load_fluctuation
        return _ack.ok, None

    def _func_turn_off(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        status = _Status.set_state(status, _PSConst.States.Off)
        self._state[_BSMPConst.ps_status] = status
        self._state[_BSMPConst.ps_setpoint] = 0.0
        self._state[_BSMPConst.ps_reference] = 0.0
        self._state[_BSMPConst.i_load] = 0.0 + self._i_load_fluctuation
        return _ack.ok, None

    def _func_reset_interlocks(self, **kwargs):
        self._state[_BSMPConst.ps_soft_interlocks] = 0
        self._state[_BSMPConst.ps_hard_interlocks] = 0
        return _ack.ok, None

    def _func_close_loop(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        status = _Status.set_openloop(status, 0)
        return _ack.ok, None

    def _func_not_implemented(self, **kwargs):
        raise NotImplementedError(
            'Run of function not defined!'.format(hex(kwargs['ID_function'])))
