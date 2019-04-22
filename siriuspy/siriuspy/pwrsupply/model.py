"""Define Power Supply classes."""

import re as _re
import time as _time
from epics import PV as _PV

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.factory import NormalizerFactory as _NormalizerFactory
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.epics import connection_timeout as _connection_timeout
from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply import sync as _sync
from siriuspy.pwrsupply.bsmp import ConstFBP as _c
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet import util as _mutil
from .status import PSCStatus as _PSCStatus


class _Device:
    """Base class to control a device using BSMP."""

    # Constants and Setpoint regexp patterns
    _ct = _re.compile('^.*-Cte$')
    _sp = _re.compile('^.*-(SP|Sel|Cmd)$')

    def __init__(self, controller, slave_id):
        """Control a device using BSMP protocol."""
        self._connected = False
        self._slave_id = slave_id
        self._controller = controller

        # self._init_setpoints()
        # self._init_constants()

    # --- public interface

    @property
    def controller(self):
        """Controller."""
        return self._controller

    def read(self, variable_id=None):
        """Return variable value, if none return group."""
        return self.controller.read_variable(self._slave_id, variable_id)

    def write(self, variable_id, value):
        """Not used."""
        pass

    def connected(self):
        """Return wether device is connected."""
        return self.controller.connections[self._slave_id]

    def _execute_function(self, function_id, value=None):
        """Execute function."""
        if value is None:
            self.controller.exec_function(self._slave_id, function_id)
        else:
            self.controller.exec_function(self._slave_id, function_id, value)


class FBPPowerSupply(_Device):
    """Control a power supply using BSMP protocol."""

    # Device API
    def turn_on(self):
        """Turn power supply on."""
        self._execute_function(_c.F_TURN_ON)
        _time.sleep(0.3)  # TODO: really necessary? PRUController does that.
        self._execute_function(_c.F_CLOSE_LOOP)

    def turn_off(self):
        """Turn power supply off."""
        self._execute_function(_c.F_TURN_OFF)
        _time.sleep(0.3)  # TODO: really necessary? PRUController does that.

    def select_op_mode(self, value):
        """Set operation mode."""
        psc_status = _PSCStatus()
        psc_status.ioc_opmode = value
        return self._execute_function(_c.F_SELECT_OP_MODE, psc_status.state)

    def reset_interlocks(self):
        """Reset."""
        self._execute_function(_c.F_RESET_INTERLOCKS)
        _time.sleep(0.1)  # TODO: should PRUController do that?

    def set_slowref(self, value):
        """Set current."""
        return self._execute_function(_c.F_SET_SLOWREF, value)

    def cfg_siggen(self, t_siggen, num_cycles,
                   freq, amplitude, offset, aux_params):
        """Set siggen congiguration parameters."""
        value = \
            [t_siggen, num_cycles, freq, amplitude, offset]
        value.extend(aux_params)
        self._execute_function(_c.F_CFG_SIGGEN, value)

    def set_siggen(self, frequency, amplitude, offset):
        """Set siggen parameters in coninuous operation."""
        value = [frequency, amplitude, offset]
        self._execute_function(_c.SET_SIGGEN, value)

    def enable_siggen(self):
        """Enable siggen."""
        self._execute_function(_c.F_ENABLE_SIGGEN)

    def disable_siggen(self):
        """Disable siggen."""
        self._execute_function(_c.F_DISABLE_SIGGEN)

    # --- Methods called by write ---

    # --- Virtual methods ---

    def _read_group(self, group_id):
        """Parse some variables.

            Check to see if PS_STATE or V_FIRMWARE_VERSION are in the group, as
        these variables need further parsing.
        """
        values = super()._read_group(group_id)
        if values is not None:
            var_ids = self.bsmp_device.entities.list_variables(group_id)
            if _c.V_PS_STATUS in var_ids:
                # TODO: values['PwrState-Sts'] == values['OpMode-Sts'] ?
                psc_status = _PSCStatus(ps_status=values['PwrState-Sts'])
                values['PwrState-Sts'] = psc_status.ioc_pwrstate
                values['OpMode-Sts'] = psc_status.state
                values['CtrlMode-Mon'] = psc_status.interface
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
            val = psc_status.state
        elif field == 'CtrlMode-Mon':
            psc_status = _PSCStatus(ps_status=val)
            val = psc_status.interface
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

    # NOTE: check if usage of QueueThread class is not degrading
    # performance. This class implemented in siriuspy.thread is
    # under suspicion...

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
                               self._computed_pvs_queue, pvs)
        else:
            psnames = _MASearch.conv_psmaname_2_psnames(self._maname)
            if len(psnames) > 1:  # SyncPV
                # 2) SYNCPV fields
                # this is used basically for SI and BO dipoles
                sync = self._get_sync_obj(field)
                pvs = [self._prefix + device_name + ":" + field
                       for device_name in psnames]
                pvname = self._psname + ":" + field
                return _ComputedPV(pvname, sync,
                                   self._computed_pvs_queue, pvs)
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
                    n = _NormalizerFactory.create(maname=self._maname)
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
        return _NormalizerFactory.create(device_name)

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
            dipole_pv = dipole + ':' + field.replace('Kick', 'Energy')
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
