"""Power supply controller classes."""

import time as _time
from siriuspy import __version__
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ps_opmode as _ps_opmode
from siriuspy.pwrsupply.bsmp import Const as _BSMPConst
from siriuspy.pwrsupply.bsmp import Status as _Status


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


class Controller(PSCommInterface):
    """Controller class."""

    # conversion dict from PS fields to DSP properties for read method.
    _read_field2func = {
        'CtrlMode-Mon': '_get_ctrlmode',
        'PwrState-Sts': '_get_pwrstate',
        'OpMode-Sts': '_get_opmode',
        'Current-RB': '_get_ps_setpoint',
        'CurrentRef-Mon': '_get_ps_reference',
        'Current-Mon': '_get_i_load',
        'IntlkSoft-Mon': '_get_ps_soft_interlocks',
        'IntlkHard-Mon': '_get_ps_hard_interlocks',
        'Version-Cte': '_get_frmware_version',
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
        self._opmode = _PSConst.OpMode.SlowRef
        self._wfmdata = [v for v in self._ps_db['WfmData-SP']['value']]

        # reset interlocks
        self.cmd_reset_interlocks()

        # turn ps on and implicitly close control loop
        self.pwrstate = _PSConst.PwrState.On

        # set opmode do SlowRef
        self.opmode = _PSConst.OpMode.SlowRef

        # set reference current to zero
        self.cmd_set_slowref(0.0)

    @property
    def scanning(self):
        """Return scanning state of serial comm."""
        return self._serial_comm.scanning

    @property
    def pwrstate(self):
        """Return PS power state."""
        return self._pwrstate

    @pwrstate.setter
    def pwrstate(self, value):
        """Set PS power state."""
        value = int(value)
        if value == _PSConst.PwrState.Off:
            self._pwrstate = value
            self.cmd_turn_off()
        elif value == _PSConst.PwrState.On:
            # turn ps on
            self._pwrstate = value
            self.cmd_turn_on()
            # close control loop
            self.cmd_close_loop()
            # set ps opmode to stored value
            self.opmode = self._opmode
        else:
            raise ValueError

    @property
    def opmode(self):
        """Return PS opmode."""
        return self._opmode

    @opmode.setter
    def opmode(self, value):
        """Set PS opmode."""
        value = int(value)
        if not(0 <= value < len(_ps_opmode)):
            raise ValueError
        # set opmode state
        self._opmode = value
        if self.pwrstate == _PSConst.PwrState.On:
            ps_status = self._get_ps_status()
            op_mode = _Status.set_opmode(ps_status, value)
            self._cmd_select_op_mode(op_mode=op_mode)

    # --- API: power supply 'functions' ---

    def cmd_turn_on(self):
        """Turn power supply on."""
        r = self._bsmp_run_function(ID_function=_BSMPConst.turn_on)
        _time.sleep(0.3)  # Eduardo-CON said it is necessary!
        return r

    def cmd_turn_off(self):
        """Turn power supply off."""
        r = self._bsmp_run_function(ID_function=_BSMPConst.turn_off)
        _time.sleep(0.3)  # Eduardo-CON said it is necessary!
        return r

    def cmd_open_loop(self):
        """Open DSP control loop."""
        return self._bsmp_run_function(ID_function=_BSMPConst.open_loop)

    def cmd_close_loop(self):
        """Open DSP control loop."""
        return self._bsmp_run_function(_BSMPConst.close_loop)

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
        if field in Controller._read_field2func:
            func = getattr(self, Controller._read_field2func[field])
            value = func()
            return value
        else:
            raise ValueError('Field "{}" not valid!'.format(field))

    def write(self, field, value):
        """Write value to a field."""
        if field in Controller._write_field2func:
            func = getattr(self, Controller._write_field2func[field])
            ret = func(value)
            return ret

    # --- private methods ---
    #     These are the functions that all subclass have to implement!

    def _connected(self):
        """Return status of connection with BSMP slaves."""
        # TODO: read serial_comm and check whether conns to slaves are ok.
        return True

    def _get_wfmdata(self):
        return self._wfmdata

    def _get_wfmindex(self):
        return self._serial_comm.sync_pulse_count

    def _get_frmware_version(self):
        value = self._bsmp_get_variable(_BSMPConst.frmware_version)
        vmajor = str((value & 0xFF00) >> 8)
        vminor = str(value & 0xFF)
        frmware_ver = '.'.join([vmajor, vminor])
        return __version__ + '-' + frmware_ver

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
        return self.pwrstate

    def _get_opmode(self):
        return self.opmode

    def _reset(self, value):
        self.cmd_reset_interlocks()

    def _set_pwrstate(self, value):
        """Set pwrstate state."""
        self.pwrstate = value
        return value

    def _set_opmode(self, value):
        """Set pwrstate state."""
        self.opmode = value
        return value

    def _set_wfmdata(self, value):
        self._wfmdata = value[:]
        self._serial_comm.set_wfmdata(self._ID_device, self._wfmdata)
        return value

    def _cmd_select_op_mode(self, op_mode):
        """Set controller operation mode."""
        # return self._bsmp_run_function(_BSMPConst.select_op_mode,
        #                                op_mode=op_mode)
        pass

    def _ps_interface_in_remote(self):
        ps_status = self._get_ps_status()
        interface = _Status.interface(ps_status)
        return interface == _PSConst.Interface.Remote
