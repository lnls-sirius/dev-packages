"""Beagle Bone implementation module."""
# NOTE on current behaviour of BeagleBone:
#
# 01. While in RmpWfm, MigWfm or SlowRefSync, the PS_I_LOAD variable read from
#     power supplies after setting the last curve point may not be the
#     final value given by PS_REFERENCE. This is due to the fact that the
#     power supply control loop takes some time to converge and the PRU may
#     block serial comm. before it. This is evident in SlowRefSync mode, where
#     reference values may change considerably between two setpoints.
#     (see identical note in PRUController)

# TODO: improve code
#
# 01. try to optimize it. At this point it is taking up 80% of BBB1 CPU time.
#     from which ~20% comes from PRController. I think we could keep some kind
#     of device state mirror in E2SController such that it does not have to
#     invoke PRUController read at every device field update. This mirror state
#     could be updated in one go.

import time as _time
from copy import deepcopy as _deepcopy

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.pru import PRU as _PRU
from siriuspy.pwrsupply.pru import PRUSim as _PRUSim
from siriuspy.pwrsupply.prucontroller import PRUCQueue as _PRUCQueue
from siriuspy.pwrsupply.prucontroller import PRUController as _PRUController
from siriuspy.pwrsupply.fields import Constant as _Constant
from siriuspy.pwrsupply.fields import Setpoint as _Setpoint
from siriuspy.pwrsupply.fields import Setpoints as _Setpoints
from siriuspy.pwrsupply import fields as _fields
from siriuspy.pwrsupply import functions as _functions
from siriuspy.pwrsupply import bsmp as _bsmp
from siriuspy.pwrsupply import controller as _controller


class BeagleBone:
    """BeagleBone is a set of PSControllers.

    This class simply redirects read, write connected requests to the
    aproppriate controller.
    """

    def __init__(self, controllers, databases):
        """Init object.

        controllers is a list of PSController
        """
        self._controllers = controllers
        self._databases = databases

        # init mirror variables and last update timestamp dicts
        self._init_mirror_and_timestamp()

    @property
    def psnames(self):
        """PS names."""
        return list(self._controllers.keys())

    def update_interval(self, device_name=None):
        """Update interval, as defined in PRUcontrollers."""
        if device_name is not None:
            pruc = self._controllers[device_name].pru_controller
            f_max = max(pruc.params.FREQ_SCAN, pruc.params.FREQ_RAMP)
        else:
            f_ramp = tuple(c.pru_controller.params.FREQ_RAMP for c in
                           self._controllers.values())
            f_scan = tuple(c.pru_controller.params.FREQ_SCAN for c in
                           self._controllers.values())
            f_max = max(f_ramp + f_scan)
        return 1.0 / f_max

    def read(self, device_name, field=None):
        """Read from device."""
        now = _time.time()
        last = self._timestamps[device_name]
        interval = self.update_interval(device_name)

        # reads, if updating is needed
        if last is None or now - last > interval:
            updated = True
            self._mirror[device_name] = \
                self._controllers[device_name].read_all_fields(device_name)
            self._timestamps[device_name] = now
        else:
            updated = False

        if field is None:
            return self._mirror[device_name], updated
        else:
            return self._mirror[device_name][field], updated

    def read_old(self, device_name, field=None):
        """Read from device."""
        if field is None:
            return self._controllers[device_name].read_all_fields(device_name)
        return self._controllers[device_name].read(device_name, field)

    def write(self, device_name, field, value):
        """Write to device."""
        self._controllers[device_name].write(device_name, field, value)

    def check_connected(self, device_name):
        """Check wether device is connected."""
        return self._controllers[device_name].check_connected(device_name)

    def database(self, device_name):
        """Device database."""
        return self._databases[device_name]

    def _init_mirror_and_timestamp(self):
        self._timestamps = dict()
        self._mirror = dict()
        for device_name in self._controllers:
            self._timestamps[device_name] = None
            self._mirror[device_name] = dict()


class BBBFactory:
    """Build BeagleBones."""

    @staticmethod
    def get(bbbname=None, devices=None, simulate=False):
        """Return BBB object."""
        # Create PRU and PRUCQueue
        pru = _PRUSim() if simulate else _PRU()
        prucqueue = _PRUCQueue()
        db = dict()

        # if bbbname == 'BBB1_TEST1':
        #     devices = (('BO-01U:PS-CH', 1),
        #                ('BO-01U:PS-CV', 2),
        #                ('BO-03U:PS-CH', 5),
        #                ('BO-03U:PS-CV', 6))
        # elif bbbname is not None:
        #     devices = _PSSearch.conv_bbbname_2_bsmps(bbbname)
        # elif devices is not None:
        #     devices = devices
        # else:
        #     raise ValueError

        # Build psmodels dict with bsmp devices
        # psmodels = BBBFactory._build_psmodels_dict(devices)

        udc_list = _PSSearch.conv_bbb_2_udc(bbbname)

        controllers = dict()  # 1 controller per UDC
        databases = dict()
        for udc in udc_list:
            print(udc)
            devices = _PSSearch.conv_udc_2_bsmps(udc)
            # Check if there is only one psmodel
            psmodel = BBBFactory.check_ps_models(devices)
            # Get out model object
            model_factory = ModelFactory.get(psmodel)
            # Create pru controller for devices
            ids = [device[1] for device in devices]
            pru_controller = _PRUController(pru, prucqueue, psmodel, ids)
            # Get model database
            database = _PSData(devices[0][0]).propty_database
            # Build setpoints
            setpoints = BBBFactory._build_setpoints_dict(devices, database)
            # Build fields and functions dicts
            fields, functions = BBBFactory._build_fields_functions_dict(
                db, model_factory, setpoints,
                devices, database, pru_controller)
            # Build connections and device_ids dicts
            connections, devices_ids = dict(), dict()
            for dev_name, dev_id in devices:
                devices_ids[dev_name] = dev_id
                connections[dev_name] = Connection(dev_id, pru_controller)
            # Build controller
            controller = model_factory.controller(
                fields, functions, connections, pru_controller, devices_ids)
            for dev_name, dev_id in devices:
                controllers[dev_name] = controller
                databases[dev_name] = database

        return BeagleBone(controllers, databases), db

    @staticmethod
    def check_ps_models(devices):
        """Check number of ps models.

        Raise exception in case the given devices have more than on psmodel
        type.
        """
        psmodels = {_PSData(psname[0]).psmodel for psname in devices}
        if len(psmodels) > 1:
            raise ValueError('Too many psmodels')
        return psmodels.pop()

    @staticmethod
    def _build_psmodels_dict(devices):
        # Build psmodels dict with bsmp devices
        psmodels = dict()
        for device in devices:
            psname = device[0]
            psmodel = _PSData(psname).psmodel
            if psmodel not in psmodels:
                psmodels[psmodel] = list()
            psmodels[psmodel].append(device)
        return psmodels

    @staticmethod
    def _build_setpoints_dict(devices, database):
        # Build setpoints
        setpoints = {}
        for field in database:
            for device in devices:
                dev_name = device[0]
                if _Setpoint.match(field):
                    setpoints[dev_name + ':' + field] = \
                        _Setpoint(field, database[field])
        return setpoints

    @staticmethod
    def _build_fields_functions_dict(db, model_factory, setpoints, devices,
                                     database, pru_controller):
        functions = dict()
        fields = dict()
        for field in database:
            if _Setpoint.match(field):
                functions.update(BBBFactory._get_functions(
                    model_factory, field, devices, setpoints, pru_controller))
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    db[pvname] = _deepcopy(database[field])
                    fields[pvname] = setpoints[pvname]
            elif _Constant.match(field) and field != 'Version-Cte':
                for dev_name, dev_id in devices:
                    name = dev_name + ':' + field
                    db[name] = _deepcopy(database[field])
                    fields[name] = _Constant(database[field]['value'])
            else:
                for dev_name, dev_id in devices:
                    name = dev_name + ':' + field
                    db[name] = _deepcopy(database[field])
                    fields[name] = model_factory.field(
                        dev_id, field, pru_controller)
        return fields, functions

    @staticmethod
    def _get_functions(model_factory, field, devices,
                       setpoints, pru_controller):
        if isinstance(model_factory, (FBPFactory, FACFactory, FAPFactory)):
            if field in ('OpMode-Sel', 'CycleType-Sel', 'CycleNrCycles-SP',
                         'CycleFreq-SP', 'CycleAmpl-SP',
                         'CycleOffset-SP', 'CycleAuxParam-SP'):
                # Make one object for all devices
                ids, sps = list(), list()
                for dev_name, dev_id in devices:
                    pvname = dev_name + ':' + field
                    ids.append(dev_id)
                    sps.append(setpoints[pvname])
                function = model_factory.function(
                    ids, field, pru_controller, _Setpoints(sps))
                return {device[0] + ':' + field: function
                        for device in devices}

        funcs = dict()
        for dev_name, dev_id in devices:
            setpoint = setpoints[dev_name + ':' + field]
            funcs[dev_name + ':' + field] = model_factory.function(
                [dev_id], field, pru_controller, setpoint)
        return funcs


class ModelFactory:
    """Abstract factory for power supply models."""

    @staticmethod
    def get(model):
        """Return ModelFactory object."""
        if model == 'FBP':
            return FBPFactory()
        elif model == 'FBP_DCLink':
            return FBPDCLinkFactory()
        elif model == 'FBP_FOFB':
            return FBPFactory()

        elif model == 'FAC_DCDC':
            return FACFactory()
        elif model == 'FAC_ACDC':
            return FACDCLinkFactory()
        elif model == 'FAC_2S_DCDC':
            return FACFactory()
        elif model == 'FAC_2S_ACDC':
            return FACDCLinkFactory()
        elif model == 'FAC_2P4S_DCDC':
            return FACFactory()
        elif model == 'FAC_2P4S_ACDC':
            return FAC2P4SFactory()

        elif model == 'FAP':
            return FAPFactory()
        elif model == 'FAP_2P2S_MASTER':
            return FAPFactory()
        elif model == 'FAP_4P_Master':
            return FAPFactory()
        elif model == 'FAP_4P_Slave':
            return FBPFactory()

        elif model == 'Commercial':
            return FACFactory()
        else:
            raise ValueError('{} not defined'.format(model))

    # Abstract Factory methods
    def database(self):
        """Return database."""
        raise NotImplementedError

    def field(self, device_id, epics_field, pru_controller):
        """Return field."""
        field = self._common_fields(device_id, epics_field, pru_controller)
        if field is None:
            field = \
                self._specific_fields(device_id, epics_field, pru_controller)
        return field

    def function(self, device_ids, epics_field, pru_controller, setpoints):
        """Return function."""
        raise NotImplementedError

    def controller(self, readers, writers, connections,
                   pru_controller, devices):
        """Return controller."""
        raise NotImplementedError

    def _common_fields(self, device_id, epics_field, pru_controller):
        _c = _bsmp.ConstBSMP
        if epics_field == 'CycleEnbl-Mon':
            return _fields.Variable(
                pru_controller, device_id, _c.V_SIGGEN_ENABLE)
        elif epics_field == 'CycleType-Sts':
            return _fields.Variable(
                pru_controller, device_id, _c.V_SIGGEN_TYPE)
        elif epics_field == 'CycleNrCycles-RB':
            return _fields.Variable(
                pru_controller, device_id, _c.V_SIGGEN_NUM_CYCLES)
        elif epics_field == 'CycleIndex-Mon':
            return _fields.Variable(pru_controller, device_id, _c.V_SIGGEN_N)
        elif epics_field == 'CycleFreq-RB':
            return _fields.Variable(
                pru_controller, device_id, _c.V_SIGGEN_FREQ)
        elif epics_field == 'CycleAmpl-RB':
            return _fields.Variable(
                pru_controller, device_id, _c.V_SIGGEN_AMPLITUDE)
        elif epics_field == 'CycleOffset-RB':
            return _fields.Variable(
                pru_controller, device_id, _c.V_SIGGEN_OFFSET)
        elif epics_field == 'CycleAuxParam-RB':
            return _fields.Variable(
                pru_controller, device_id, _c.V_SIGGEN_AUX_PARAM)
        elif epics_field == 'PwrState-Sts':
            return _fields.PwrState(
                _fields.Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'OpMode-Sts':
            return _fields.OpMode(
                _fields.Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'CtrlMode-Mon':
            return _fields.CtrlMode(
                _fields.Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'CtrlLoop-Sts':
            return _fields.CtrlLoop(
                _fields.Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'Version-Cte':
            return _fields.Version(
                _fields.Variable(
                    pru_controller, device_id, _c.V_FIRMWARE_VERSION))
        # PRU related variables
        elif epics_field == 'WfmData-RB':
            return _fields.PRUCurve(pru_controller, device_id)
        elif epics_field == 'WfmIndex-Mon':
                return _fields.Constant(0)
        elif epics_field == 'PRUSyncMode-Mon':
            return _fields.PRUSyncMode(pru_controller)
        elif epics_field == 'PRUBlockIndex-Mon':
            return _fields.PRUProperty(pru_controller, 'pru_curve_block')
        elif epics_field == 'PRUSyncPulseCount-Mon':
            return _fields.PRUProperty(pru_controller, 'pru_sync_pulse_count')
        elif epics_field == 'PRUCtrlQueueSize-Mon':
            return _fields.PRUProperty(pru_controller, 'queue_length')

        return None

    def _specific_fields(self, device_id, epics_field, pru_controller):
        # Specific fields
        if epics_field in self._variables:
            var_id = self._variables[epics_field]
            return _fields.Variable(pru_controller, device_id, var_id)
        return None


# Standard PS that supply magnets
class FBPFactory(ModelFactory):
    """FBP model factory."""

    _variables = {
        'IntlkSoft-Mon':  _bsmp.ConstFBP.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon':  _bsmp.ConstFBP.V_PS_HARD_INTERLOCKS,
        'Current-RB':  _bsmp.ConstFBP.V_PS_SETPOINT,
        'CurrentRef-Mon':  _bsmp.ConstFBP.V_PS_REFERENCE,
        'Current-Mon':  _bsmp.ConstFBP.V_I_LOAD,
    }

    def database(self):
        """Return model database."""
        pass

    def function(self, device_ids, epics_field, pru_controller, setpoints):
        """Return function."""
        _c = _bsmp.ConstFBP
        if epics_field == 'PwrState-Sel':
            return _functions.PSPwrState(device_ids, pru_controller, setpoints)
        elif epics_field == 'OpMode-Sel':
            return _functions.PSOpMode(
                device_ids,
                _functions.BSMPFunction(
                    device_ids, pru_controller, _c.F_SELECT_OP_MODE),
                setpoints)
        elif epics_field == 'Current-SP':
            return _functions.Current(device_ids, pru_controller, setpoints)
        elif epics_field == 'Reset-Cmd':
            return _functions.BSMPFunction(
                device_ids, pru_controller, _c.F_RESET_INTERLOCKS, setpoints)
        elif epics_field == 'Abort-Cmd':
            return _functions.BSMPFunctionNull()
        elif epics_field == 'CycleDsbl-Cmd':
            return _functions.BSMPFunction(
                device_ids, pru_controller, _c.F_DISABLE_SIGGEN, setpoints)
        elif epics_field == 'CycleType-Sel':
            return _functions.CfgSiggen(
                device_ids, pru_controller, 0, setpoints)
        elif epics_field == 'CycleNrCycles-SP':
            return _functions.CfgSiggen(
                device_ids, pru_controller, 1, setpoints)
        elif epics_field == 'CycleFreq-SP':
            return _functions.CfgSiggen(
                device_ids, pru_controller, 2, setpoints)
        elif epics_field == 'CycleAmpl-SP':
            return _functions.CfgSiggen(
                device_ids, pru_controller, 3, setpoints)
        elif epics_field == 'CycleOffset-SP':
            return _functions.CfgSiggen(
                device_ids, pru_controller, 4, setpoints)
        elif epics_field == 'CycleAuxParam-SP':
            return _functions.CfgSiggen(
                device_ids, pru_controller, 5, setpoints)
        elif epics_field == 'WfmData-SP':
            return _functions.PRUCurve(device_ids, pru_controller, setpoints)
        else:
            return _functions.BSMPFunctionNull()

    def controller(self, readers, writers, connections,
                   pru_controller, devices):
        """Return controller."""
        return _controller.StandardPSController(
            readers, writers, connections, pru_controller, devices)


class FACFactory(FBPFactory):
    """FAC model factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFAC_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_DCDC.V_PS_HARD_INTERLOCKS,
        'Current-RB': _bsmp.ConstFAC_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAC_DCDC.V_PS_REFERENCE,
        'Current-Mon': _bsmp.ConstFAC_DCDC.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAC_DCDC.V_I_LOAD2,
    }

    pass


class FAPFactory(FBPFactory):
    """FAP model factory."""

    pass


# Auxiliaty power supplies (DCLinks)
class FBPDCLinkFactory(ModelFactory):
    """FBP dclink factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFBP_DCLink.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFBP_DCLink.V_PS_HARD_INTERLOCKS,
        'ModulesStatus-Mon': _bsmp.ConstFBP_DCLink.V_DIGITAL_INPUTS,
        'Voltage-RB': _bsmp.ConstFBP_DCLink.V_PS_SETPOINT,
        'VoltageRef-Mon': _bsmp.ConstFBP_DCLink.V_PS_REFERENCE,
        'Voltage-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT,
        'Voltage1-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT_1,
        'Voltage2-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT_2,
        'Voltage3-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT_3,
        'VoltageDig-Mon': _bsmp.ConstFBP_DCLink.V_DIG_POT_TAP,
    }

    def database(self):
        """Return model database."""
        pass

    def function(self, device_ids, epics_field, pru_controller, setpoints):
        """Return function."""
        _c = _bsmp.ConstFBP_DCLink
        if epics_field == 'PwrState-Sel':
            return _functions.PSPwrStateFBP_DCLink(
                device_ids, pru_controller, setpoints)
        elif epics_field == 'CtrlLoop-Sel':
            return _functions.CtrlLoop(device_ids, pru_controller, setpoints)
        elif epics_field == 'OpMode-Sel':
            return _functions.PSOpMode(
                device_ids,
                _functions.BSMPFunction(
                    device_ids, pru_controller, _c.F_SELECT_OP_MODE),
                setpoints)
        elif epics_field == 'Voltage-SP':
            return _functions.BSMPFunction(
                device_ids, pru_controller, _c.F_SET_SLOWREF, setpoints)
        elif epics_field == 'Reset-Cmd':
            return _functions.BSMPFunction(
                device_ids, pru_controller, _c.F_RESET_INTERLOCKS, setpoints)
        elif epics_field == 'Abort-Cmd':
            return _functions.BSMPFunctionNull()
        else:
            return _functions.BSMPFunctionNull()

    def controller(self, readers, writers, connections,
                   pru_controller, devices):
        """Return controller."""
        return _controller.PSController(
            readers, writers, connections, pru_controller)


class FACDCLinkFactory(FBPDCLinkFactory):
    """FAC ACDC factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFAC_ACDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_ACDC.V_PS_HARD_INTERLOCKS,
        'CapacitorBankVoltage-Mon': _bsmp.ConstFAC_ACDC.V_CAPACITOR_BANK,
        'RectifierVoltage-Mon': _bsmp.ConstFAC_ACDC.V_OUT_RECTIFIER,
        'RectifierCurrent-Mon': _bsmp.ConstFAC_ACDC.I_OUT_RECTIFIER,
        'HeatSinkTemperature-Mon': _bsmp.ConstFAC_ACDC.TEMP_HEATSINK,
        'InductorsTemperature-Mon': _bsmp.ConstFAC_ACDC.TEMP_INDUCTORS,
        'PWMDutyCycle-Mon': _bsmp.ConstFAC_ACDC.DUTY_CYCLE,
    }

    pass


class FAC2SFactory(FACDCLinkFactory):
    """FAC 2S factoy."""

    pass


class FAC2P4SFactory(FACDCLinkFactory):
    """FAC 2P4S factoy."""

    pass


class Connection:
    """Object that checks if a device is connected."""

    def __init__(self, device_id, pru_controller):
        """Init."""
        self._device_id = device_id
        self._pru_controller = pru_controller

    def connected(self):
        """Return wether device is connected."""
        return self._pru_controller.check_connected(self._device_id)
