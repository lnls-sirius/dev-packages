"""Define Power Supply classes."""

import re as _re
import time as _time
# import random as _random

from epics import PV as _PV

from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
# from siriuspy.csdevice.pwrsupply import max_wfmsize as _max_wfmsize
from siriuspy.factory import NormalizerFactory as _NormalizerFactory
from siriuspy.epics import connection_timeout as _connection_timeout
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet import util as _mutil
from siriuspy.pwrsupply import sync as _sync
# PowerSupply
from ..bsmp import Response
from ..bsmp import SerialError as _SerialError
from .status import PSCStatus as _PSCStatus
from siriuspy.pwrsupply.bsmp import Const as _c
from siriuspy.pwrsupply.bsmp import ps_group_id as _ps_group_id


class Device:
    """Control a device using BSMP protocol."""

    # Setpoints regexp pattern
    _sp = _re.compile('^.*-(SP|Sel|Cmd)$')

    def __init__(self, controller, slave_id, database):
        """Control a device using BSMP protocol."""
        self._connected = False
        self._slave_id = slave_id
        self._controller = controller
        self._database = database

        # add current device as slave to used controller
        self._controller.add_slave(slave_id)

        # initialize setpoints
        self._setpoints = dict()
        for field, db in self.database.items():
            if self._sp.match(field):
                self._setpoints[field] = db
        self._init_setpoints()

    # API
    @property
    def controller(self):
        """Controller."""
        return self._controller

    @property
    def device(self):
        """BSMP instance for this device."""
        return self._controller[self._slave_id]

    @property
    def database(self):
        """Device database."""
        return self._database

    @property
    def setpoints(self):
        """Device setpoints."""
        return self._setpoints

    @property
    def connected(self):
        """Return connection state."""
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value

    def read(self, field):
        """Read a field from device."""
        if field in self._setpoints:
            value = self.setpoints[field]['value']
        else:
            try:
                value = self._read_variable(field)
            except _SerialError:
                self.connected = False
                return None
            self.connected = True
        return value

    def write(self, field, value):
        """Write to device field."""
        try:
            if field in self._setpoints:
                self._write_setpoint(field, value)  # SerialError
            else:
                pass  # SerialError
            self.connected = True
        except _SerialError:
            self.connected = False
            return False
        return True

    def read_all_variables(self):
        """Read all variables."""
        return self._read_group(0)

    # Groups
    def _read_group(self, group_id):
        """Read a group of variables and return a dict."""
        # Read values
        sts, val = self.device.read_group_variables(group_id)
        if sts == Response.ok:
            ret = dict()
            variables = self.device.entities.list_variables(group_id)
            for idx, var_id in enumerate(variables):
                try:  # TODO: happens because bsmp_2_epics is not complete
                    field = self.bsmp_2_epics[var_id]
                except KeyError:
                    continue
                if isinstance(field, tuple):
                    for f in field:
                        ret[f] = val[idx]
                else:
                    ret[field] = val[idx]
            return ret
        return None

    def _create_group(self, fields):
        """Create a group of variables."""
        ids = set()
        for field in fields:
            ids.add(self.epics_2_bsmp[field])
        sts, _ = self.device.create_group(ids)
        if sts == Response.ok:
            return True
        return False

    # IOC
    def read_setpoints(self):
        """Read sepoints."""
        ret = dict()
        for setpoint, db in self.setpoints.items():
            ret[setpoint] = db['value']
        return ret

    def read_status(self):
        """Read parameters."""
        return {}

    def _init_setpoints(self):
        try:
            values = self.read_all_variables()
        except Exception as e:
            print('{}'.format(e))
            pass
        else:
            # Init Setpoints
            for setpoint in self.setpoints:
                if '-Cmd' in setpoint:
                    continue
                readback = \
                    setpoint.replace('-Sel', '-Sts').replace('-SP', '-RB')
                try:
                    self.setpoints[setpoint]['value'] = values[readback]
                except KeyError:
                    continue
            self._connected = True

    def _read_variable(self, field):
        var_id = self.epics_2_bsmp[field]
        sts, val = self.device.read_variable(var_id)
        if sts == Response.ok:
            return val
        else:
            return None

    def _execute_function(self, func_id, value=None):
        sts, val = self.device.execute_function(func_id, value)
        if sts == Response.ok:
            return True
        else:
            return False

    def _write_setpoint(self, field, value):
        """Map a setpoint to a controller operation."""
        raise NotImplementedError()


class FBPPowerSupply(Device):
    """Control a power supply using BSMP protocol."""

    bsmp_2_epics = {
        _c.V_PS_STATUS: ('PwrState-Sts', 'OpMode-Sts'),
        _c.V_PS_SETPOINT: 'Current-RB',
        _c.V_PS_REFERENCE: 'CurrentRef-Mon',
        _c.V_FIRMWARE_VERSION: 'Version-Cte',
        _c.V_SIGGEN_ENABLE: 'CycleEnbl-Mon',
        _c.V_SIGGEN_TYPE: 'CycleType-Sts',
        _c.V_SIGGEN_NUM_CYCLES: 'CycleNrCycles-RB',
        _c.V_SIGGEN_N: 'CycleIndex-Mon',
        _c.V_SIGGEN_FREQ: 'CycleFreq-RB',
        _c.V_SIGGEN_AMPLITUDE: 'CycleAmpl-RB',
        _c.V_SIGGEN_OFFSET: 'CycleOffset-RB',
        _c.V_SIGGEN_AUX_PARAM: 'CycleAuxParam-RB',
        _c.V_PS_SOFT_INTERLOCKS: 'IntlkSoft-Mon',
        _c.V_PS_HARD_INTERLOCKS: 'IntlkHard-Mon',
        _c.V_I_LOAD: 'Current-Mon',
    }

    epics_2_bsmp = {
        'PwrState-Sts': _c.V_PS_STATUS,
        'OpMode-Sts': _c.V_PS_STATUS,
        'Current-RB': _c.V_PS_SETPOINT,
        'CurrentRef-Mon': _c.V_PS_REFERENCE,
        'Version-Cte': _c.V_FIRMWARE_VERSION,
        'CycleEnbl-Mon': _c.V_SIGGEN_ENABLE,
        'CycleType-Sts': _c.V_SIGGEN_TYPE,
        'CycleNrCycles-RB': _c.V_SIGGEN_NUM_CYCLES,
        'CycleIndex-Mon': _c.V_SIGGEN_N,
        'CycleFreq-RB': _c.V_SIGGEN_FREQ,
        'CycleAmpl-RB': _c.V_SIGGEN_AMPLITUDE,
        'CycleOffset': _c.V_SIGGEN_OFFSET,
        'CycleAuxParam-RB': _c.V_SIGGEN_AUX_PARAM,
        'IntlkSoft-Mon': _c.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _c.V_PS_HARD_INTERLOCKS,
        'Current-Mon': _c.V_I_LOAD,
    }

    _epics_2_wfuncs = {
        'PwrState-Sel': '_set_pwrstate',
        'OpMode-Sel': '_set_opmode',
        'Current-SP': '_set_current',
        'Reset-Cmd': '_reset',
        'CycleEnbl-Cmd': '_enable_cycle',
        'CycleDsbl-Cmd': '_disable_cycle',
        'CycleType-Sel': '_set_cycle_type',
        'CycleNrCycles-SP': '_set_cycle_nr_cycles',
        'CycleFreq-SP': '_set_cycle_frequency',
        'CycleAmpl-SP': '_set_cycle_amplitude',
        'CycleOffset-SP': '_set_cycle_offset',
        'CycleAuxParam-SP': '_set_cycle_aux_params',
        'WfmData-SP': '_set_wfmdata_sp',
    }

    def __init__(self, controller, slave_id, database):
        """High level PS.

        The controller object implements the BSMP interface.
        All properties map an epics field to a BSMP property.
        """
        super().__init__(controller, slave_id, database)
        self._pru = self.controller.pru

        # initialize groups
        self.device.remove_all_groups()  # TODO: check errors, create group 3?
        var_ids = self.device.entities.list_variables(group_id=0)
        var_ids.remove(_c.V_FIRMWARE_VERSION)
        self.device.create_group(var_ids=var_ids)

        # close DSP loop
        # TODO: this breaks the concept that the IOC should init w/o setting PS
        self.device.execute_function(_c.F_CLOSE_LOOP)

    def read_ps_variables(self):
        """Read called to update DB."""
        return self._read_group(_ps_group_id)

    def read_status(self):
        """Read fields that are not setpoinrs nor bsmp variables."""
        ret = dict()
        ret['WfmData-RB'] = self.database['WfmData-RB']['value']
        ret['WfmIndex-Mon'] = self.controller.pru.sync_pulse_count
        return ret

    # BSMP specific
    def _turn_on(self):
        """Turn power supply on."""
        ret = self._execute_function(_c.F_TURN_ON)
        if ret:
            _time.sleep(0.3)
            return self._execute_function(_ps_group_id)  # Close control loop

    def _turn_off(self):
        """Turn power supply off."""
        ret = self._execute_function(_c.F_TURN_OFF)
        if ret:
            _time.sleep(0.3)
        return ret

    def _select_op_mode(self, value):
        """Set operation mode."""
        psc_status = _PSCStatus()
        psc_status.ioc_opmode = value
        return self._execute_function(_c.F_SELECT_OP_MODE, psc_status.state)

    def _reset_interlocks(self):
        """Reset."""
        ret = self._execute_function(_c.F_RESET_INTERLOCKS)
        if ret:
            _time.sleep(0.1)
        return ret

    def _set_slowref(self, value):
        """Set current."""
        return self._execute_function(_c.F_SET_SLOWREF, value)

    def _cfg_siggen(self, t_siggen, num_cycles,
                    freq, amplitude, offset, aux_params):
        """Set siggen congiguration parameters."""
        value = \
            [t_siggen, num_cycles, freq, amplitude, offset]
        value.extend(aux_params)
        return self._execute_function(_c.F_CFG_SIGGEN, value)

    def _set_siggen(self, frequency, amplitude, offset):
        """Set siggen parameters in coninuous operation."""
        value = [frequency, amplitude, offset]
        return self._execute_function(_c.SET_SIGGEN, value)

    def _enable_siggen(self):
        """Enable siggen."""
        return self._execute_function(_c.F_ENABLE_SIGGEN)

    def _disable_siggen(self):
        """Disable siggen."""
        return self._execute_function(_c.F_DISABLE_SIGGEN)

    # --- Methods called by write ---

    def _set_pwrstate(self, setpoint):
        """Set PwrState setpoint."""
        if setpoint == 1:
            ret = self._turn_on()
        elif setpoint == 0:
            ret = self._turn_off()
        else:
            self.setpoints['PwrState-Sel']['value'] = setpoint
            return

        if ret:
            self.setpoints['Current-SP']['value'] = 0.0
            self.setpoints['OpMode-Sel']['value'] = 0
            self.setpoints['PwrState-Sel']['value'] = setpoint

    def _set_opmode(self, setpoint):
        """Operation mode setter."""
        if setpoint < 0 or \
                setpoint > len(self.setpoints['OpMode-Sel']['enums']):
            self.setpoints['OpMode-Sel']['value'] = setpoint
            # raise InvalidValue("OpMode {} out of range.".format(setpoint))

        if self._select_op_mode(setpoint):
            self.setpoints['OpMode-Sel']['value'] = setpoint

    def _set_current(self, setpoint):
        """Set current."""
        setpoint = max(self.setpoints['Current-SP']['lolo'], setpoint)
        setpoint = min(self.setpoints['Current-SP']['hihi'], setpoint)

        if self._set_slowref(setpoint):
            self.setpoints['Current-SP']['value'] = setpoint

    def _reset(self, setpoint):
        """Reset command."""
        if setpoint:
            if self._reset_interlocks():
                self.setpoints['Reset-Cmd']['value'] += 1

    def _enable_cycle(self, setpoint):
        """Enable cycle command."""
        if setpoint:
            if self._enable_siggen():
                self.setpoints['CycleEnbl-Cmd']['value'] += 1

    def _disable_cycle(self, setpoint):
        """Disable cycle command."""
        if setpoint:
            if self._disable_siggen():
                self.setpoints['CycleDsbl-Cmd']['value'] += 1

    def _set_cycle_type(self, setpoint):
        """Set cycle type."""
        self.setpoints['CycleType-Sel']['value'] = setpoint
        # if setpoint < 0 or \
        #         setpoint > len(self.setpoints['CycleType-Sel']['enums']):
        #     return
        return self._cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_nr_cycles(self, setpoint):
        """Set number of cycles."""
        self.setpoints['CycleNrCycles-SP']['value'] = setpoint
        return self._cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_frequency(self, setpoint):
        """Set cycle frequency."""
        self.setpoints['CycleFreq-SP']['value'] = setpoint
        return self._cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_amplitude(self, setpoint):
        """Set cycle amplitude."""
        self.setpoints['CycleAmpl-SP']['value'] = setpoint
        return self._cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_offset(self, setpoint):
        """Set cycle offset."""
        self.setpoints['CycleOffset-SP']['value'] = setpoint
        return self._cfg_siggen(*self._cfg_siggen_args())

    def _set_cycle_aux_params(self, setpoint):
        """Set cycle offset."""
        # trim setpoint list
        cur_sp = self.setpoints['CycleAuxParam-SP']['value']
        setpoint = setpoint[:len(cur_sp)]
        setpoint += cur_sp[len(setpoint):]
        # update setpoint
        self.setpoints['CycleAuxParam-SP']['value'] = setpoint
        return self._cfg_siggen(*self._cfg_siggen_args())

    def _cfg_siggen_args(self):
        """Get cfg_siggen args and execute it."""
        args = []
        args.append(self.setpoints['CycleType-Sel']['value'])
        args.append(self.setpoints['CycleNrCycles-SP']['value'])
        args.append(self.setpoints['CycleFreq-SP']['value'])
        args.append(self.setpoints['CycleAmpl-SP']['value'])
        args.append(self.setpoints['CycleOffset-SP']['value'])
        args.append(self.setpoints['CycleAuxParam-SP']['value'])
        return args

    def _set_wfmdata_sp(self, setpoint):
        """Set wfmdata."""
        self.setpoints['WfmData-SP']['value'] = setpoint
        self.database['WfmData-RB']['value'] = setpoint
        return True

    # --- Virtual methods ---

    def _read_group(self, group_id):
        """Parse some variables.

            Check to see if PS_STATE or V_FIRMWARE_VERSION are in the group, as
        these variables need further parsing.
        """
        var_ids = self.device.entities.list_variables(group_id)
        values = super()._read_group(group_id)
        if _c.V_PS_STATUS in var_ids:
            # TODO: values['PwrState-Sts'] == values['OpMode-Sts'] ?
            psc_status = _PSCStatus(ps_status=values['PwrState-Sts'])
            values['PwrState-Sts'] = psc_status.ioc_pwrstate
            values['OpMode-Sts'] = psc_status.ioc_opmode
        if _c.V_FIRMWARE_VERSION in var_ids:
            version = ''.join([c.decode() for c in values['Version-Cte']])
            try:
                values['Version-Cte'], _ = version.split('\x00', 1)
            except ValueError:
                values['Version-Cte'] = version
        return values

    def _read_variable(self, field):
        """Parse some variables.

            Check to see if PS_STATE or V_FIRMWARE_VERSION are in the group, as
        these variables need further parsing.
        """
        val = super()._read_variable(field)

        if val is None:
            return None

        if field == 'PwrState-Sts':
            psc_status = _PSCStatus(ps_status=val)
            val = psc_status.ioc_pwrstate
        elif field == 'OpMode-Sts':
            psc_status = _PSCStatus(ps_status=val)
            val = psc_status.ioc_opmode
        elif field == 'Version-Cte':
            version = ''.join([c.decode() for c in val])
            try:
                val, _ = version.split('\x00', 1)
            except ValueError:
                val = version

        return val

    def _write_setpoint(self, field, setpoint):
        """Write operation."""
        if field in FBPPowerSupply._epics_2_wfuncs:
            func_name = FBPPowerSupply._epics_2_wfuncs[field]
            func = getattr(self, func_name)
            return func(setpoint=setpoint)


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


class PSEpics(PSCommInterface):
    """Power supply with Epics communication."""

    # TODO: should we merge this base class into MAEpics?

    def __init__(self, psname, fields=None, use_vaca=True):
        """Create epics PVs and expose them through public controller API."""
        PSCommInterface.__init__(self)
        # Attributes use build a full PV address
        self._psname = psname
        # self._sort_fields()
        if use_vaca:
            self._prefix = _VACA_PREFIX
        else:
            self._prefix = ''
        # Get pv db
        self._base_db = self._get_base_db()
        # Get fields, if none is passed they'll will be retrieved from the db
        if fields is None:
            self._fields = self._get_fields()
        else:
            self._fields = fields
        # Holds PVs objects
        self._pvs = dict()
        self._create_pvs()

    # --- PSCommInterface implementation ---

    def read(self, field):
        """Read a field value."""
        # if field not in self.valid_fields:
        #     return None
        if self._pvs[field].connected:
            return self._pvs[field].get()
        else:
            # print("Not connected")
            return None

    def write(self, field, value):
        """Write a value to a field."""
        # Check wether value is valid and return 0
        # if field not in self.valid_fields:
        #     return None
        if self._pvs[field].connected:
            return self._pvs[field].put(value)
        else:
            # print("Not connected")
            return None

    def add_callback(self, func):
        """Add callback to field."""
        if not callable(func):
            raise ValueError("Tried to set non callable as a callback")
        else:
            for pvname, pv in self._pvs.items():
                # field = pvname.split(':')[-1]
                # if field in self.valid_fields:
                pv.add_callback(func)

    def _connected(self):
        for pv in self._pvs.values():
            if not pv.connected:
                return False
        return True

    # --- public methods ---

    def get_database(self, prefix=""):
        """Fill base DB with values and limits read from PVs.

        Optionally add a prefix to the dict keys.
        """
        db = self._fill_database()

        if prefix:
            prefixed_db = {}
            for key, value in db.items():
                prefixed_db[prefix + ":" + key] = value
            return prefixed_db
        else:
            return db

    # --- private methods ---

    def _create_pvs(self):
        # No/rmally create normal PV objects
        # In case more than one source is supplied creates a SyncPV
        # In case the device is a Magnet with a normalized force being supplied
        # as one of the fields, a NormalizedPV is created
        self._sort_fields()
        for field in self._fields:
            # if field in self.valid_fields:
            self._pvs[field] = self._create_pv(field)

    def _create_pv(self, field):
        return _PV(self._prefix + self._psname + ":" + field,
                   connection_timeout=_connection_timeout)

    def _get_base_db(self):
        return _PSData(self._psname).propty_database

    def _get_fields(self):
        return self._base_db.keys()

    def _fill_database(self):
        db = dict()
        db.update(self._base_db)
        for field in db:
            value = self.read(field)
            if value is not None:
                db[field]['value'] = value

                # calc pv limits
                if 'KL' in field or 'Energy' in field or \
                   'SL' in field or 'Kick' in field:
                    cpv = self._pvs[field]
                    lims = cpv.computer.compute_limits(cpv)
                    # cpv.upper_alarm_limit = lims[0]
                    # cpv.upper_warning_limit = lims[1]
                    # cpv.upper_disp_limit = lims[2]
                    # cpv.lower_disp_limit = lims[3]
                    # cpv.lower_warning_limit = lims[4]
                    # cpv.lower_alarm_limit = lims[5]
                    db[field]['hihi'] = lims[0]
                    db[field]['high'] = lims[1]
                    db[field]['hilim'] = lims[2]
                    db[field]['lolim'] = lims[3]
                    db[field]['low'] = lims[4]
                    db[field]['lolo'] = lims[5]

        return db

    def _sort_fields(self):
        fields = []
        for field in self._fields:
            if not self._is_strength.match(field):
                fields.insert(0, field)
            else:
                fields.append(field)

        self._fields = fields


class MAEpics(PSEpics):
    """Magnet power supply with Epics communication."""

    _is_strength = _re.compile('(Energy|KL|SL|Kick).+$')
    _is_multi_ps = _re.compile('(SI|BO)-\w{2,4}:MA-B.*$')

    def __init__(self, maname, lock=False, **kwargs):
        """Create epics PVs and expose them through public controller API."""
        # Attributes use build a full PV address
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname)
        self._lock = lock
        self._computed_pvs_queue = _QueueThread()
        super().__init__(
            self._maname.replace("MA", "PS").replace("PM", "PU"),
            **kwargs)

    # --- virtual methods ---

    def _create_pvs(self):
        self._sort_fields()
        super()._create_pvs()

    def _create_pv(self, field):
        # Build either a real or computed PV
        if MAEpics._is_strength.match(field):
            # 1) STRENGTH magnet fields
            # an intermediate computed_pv is created in order for the
            # strength to be calculated from currents.
            pvname = self._prefix + self._maname + ":" + field
            str_obj = self._get_normalizer(self._maname)
            pvs = self._get_str_pv(field)
            return _ComputedPV(pvname, str_obj,
                               self._computed_pvs_queue, *pvs)
        else:
            if len(self._psnames()) > 1:  # SyncPV
                # 2) SYNCPV fields
                # this is used basically for SI and BO dipoles
                sync = self._get_sync_obj(field)
                pvs = [self._prefix + device_name + ":" + field
                       for device_name in self._psnames()]
                pvname = self._psname + ":" + field
                return _ComputedPV(pvname, sync,
                                   self._computed_pvs_queue, *pvs)
            else:
                # 3) PV
                # a normal pv mirroring the power supply pv.
                # no computed_pv is needed.
                return super()._create_pv(field)

    def _get_base_db(self):
        # set dipole energy limits
        n, db = None, self._madata.get_database(self._madata.psnames[0])
        for pvname in db:
            if 'Energy' in pvname:
                pvname_ps = pvname.replace('Energy', 'Current')
                if n is None:
                    n = _NormalizerFactory.factory(maname=self._maname)
                currents = []
                currents.append(db[pvname_ps]['hihi'])
                currents.append(db[pvname_ps]['high'])
                currents.append(db[pvname_ps]['hilim'])
                currents.append(db[pvname_ps]['lolim'])
                currents.append(db[pvname_ps]['low'])
                currents.append(db[pvname_ps]['lolo'])
                lims = sorted(n.conv_current_2_strength(currents=currents))
                db[pvname]['hihi'] = lims[0]
                db[pvname]['high'] = lims[1]
                db[pvname]['hilim'] = lims[2]
                db[pvname]['lolim'] = lims[3]
                db[pvname]['low'] = lims[4]
                db[pvname]['lolo'] = lims[5]
        return db

    # --- class methods ---

    def _get_normalizer(self, device_name):
        # Return Normalizer object
        return _NormalizerFactory.factory(device_name)

    def _get_sync_obj(self, field):
        # Return SyncWrite or SyncRead object
        if "SP" in field or "Sel" in field or "Cmd" in field:
            return _sync.SyncWrite(lock=self._lock)
        else:
            return _sync.SyncRead()

    def _get_str_pv(self, field):
        ma_class = _mutil.magnet_class(self._maname)
        if 'dipole' == ma_class:
            field = field.replace('Energy', 'Current')
            return [self._pvs[field], ]
        elif 'pulsed' == ma_class:
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pv = dipole + ':' + field.replace('Kick', 'Current')
            return [self._pvs[field.replace('Kick', 'Voltage')],
                    dipole_pv]
        elif 'trim' == ma_class:
            field = field.replace('KL', 'Current')
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pv = dipole + ':' + field.replace('Current', 'Energy')
            fam_name = _mutil.get_magnet_family_name(self._maname)
            fam = self._prefix + fam_name
            family_pv = fam + ':' + field.replace('Current', 'KL')

            # use Ref-Mon, instead of -Mon
            # (this is not necessary anymore for efficiency standpoint, since
            #  now only the main current pv is being used to trigger
            #  conversion. The line below may be commented out or deleted. )
            dipole_pv = dipole_pv.replace('Energy-Mon', 'EnergyRef-Mon')
            family_pv = family_pv.replace('KL-Mon', 'KLRef-Mon')

            return [self._pvs[field], dipole_pv, family_pv]
        else:
            field = field.replace('KL', 'Current')
            field = field.replace('SL', 'Current')
            field = field.replace('Kick', 'Current')
            dipole_name = _mutil.get_section_dipole_name(self._maname)
            dipole = self._prefix + dipole_name
            dipole_pv = dipole + ':' + field.replace('Current', 'Energy')

            # use Ref-Mon, instead of -Mon
            # (this is not necessary anymore for efficiency standpoint, since
            #  now only the main current pv is being used to trigger
            #  conversion. The line below may be commented out or deleted. )
            dipole_pv = dipole_pv.replace('Energy-Mon', 'EnergyRef-Mon')

            return [self._pvs[field], dipole_pv]

    def _psnames(self):
        ma_class = _mutil.magnet_class(self._maname)
        if 'dipole' == ma_class:
            if 'SI' == self._maname.sec:
                return ['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']
            elif 'BO' == self._maname.sec:
                return ['BO-Fam:PS-B-1', 'BO-Fam:PS-B-2']
        elif 'pulsed' == ma_class:
            return [self._maname.replace(':PM', ':PU')]

        return [self._maname.replace(':MA', ':PS')]
