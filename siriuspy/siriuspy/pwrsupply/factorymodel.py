"""Model abstract factory."""

from siriuspy.pwrsupply import fields as _fields
from siriuspy.pwrsupply import functions as _functions
from siriuspy.pwrsupply import bsmp as _bsmp
from siriuspy.pwrsupply import controller as _controller


# --- Entities DCDC ---
from siriuspy.pwrsupply.bsmp import EntitiesFBP as _EntitiesFBP
from siriuspy.pwrsupply.bsmp import EntitiesFAC_DCDC as _EntitiesFAC_DCDC
from siriuspy.pwrsupply.bsmp import \
    EntitiesFAC_2P4S_DCDC as _EntitiesFAC_2P4S_DCDC
from siriuspy.pwrsupply.bsmp import \
    EntitiesFAC_2S_DCDC as _EntitiesFAC_2S_DCDC
from siriuspy.pwrsupply.bsmp import EntitiesFAP as _EntitiesFAP
from siriuspy.pwrsupply.bsmp import EntitiesFAP_4P as _EntitiesFAP_4P
from siriuspy.pwrsupply.bsmp import EntitiesFAP_2P2S as _EntitiesFAP_2P2S
# --- Entities ACDC ---
from siriuspy.pwrsupply.bsmp import EntitiesFBP_DCLink as _EntitiesFBP_DCLink

from siriuspy.pwrsupply.bsmp import \
    EntitiesFAC_2P4S_ACDC as _EntitiesFAC_2P4S_ACDC
from siriuspy.pwrsupply.bsmp import \
    EntitiesFAC_2S_ACDC as _EntitiesFAC_2S_ACDC

# --- Const DCDC ---
from siriuspy.pwrsupply.bsmp import ConstFBP as _cFBP
from siriuspy.pwrsupply.bsmp import ConstFAC_DCDC as _cFAC_DCDC
from siriuspy.pwrsupply.bsmp import ConstFAC_2P4S_DCDC as _cFAC_2P4S_DCDC
from siriuspy.pwrsupply.bsmp import ConstFAC_2S_DCDC as _cFAC_2S_DCDC
from siriuspy.pwrsupply.bsmp import ConstFAP as _cFAP
from siriuspy.pwrsupply.bsmp import ConstFAP_4P as _cFAP_4P
from siriuspy.pwrsupply.bsmp import ConstFAP_2P2S as _cFAP_2P2S

# --- Const ACDC ---
from siriuspy.pwrsupply.bsmp import ConstFBP_DCLink as _cFBP_DCLink
from siriuspy.pwrsupply.bsmp import ConstFAC_2P4S_ACDC as _cFAC_2P4S_ACDC
from siriuspy.pwrsupply.bsmp import ConstFAC_2S_ACDC as _cFAC_2S_ACDC

# --- BSMP DCDC ---
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FBP as _BSMPSim_FBP
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FAC_DCDC as _BSMPSim_FAC_DCDC
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FAC_2P4S_DCDC as _BSMPSim_FAC_2P4S_DCDC
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FAC_2S_DCDC as _BSMPSim_FAC_2S_DCDC
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FAP as _BSMPSim_FAP
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FAP_4P as _BSMPSim_FAP_4P
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FAP_2P2S as _BSMPSim_FAP_2P2S

# --- BSMP ACDC ---
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FBP_DCLink as _BSMPSim_FBP_DCLink
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FAC_2P4S_ACDC as _BSMPSim_FAC_2P4S_ACDC
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FAC_2S_ACDC as _BSMPSim_FAC_2S_ACDC


class FactoryModel:
    """Abstract factory for power supply models."""

    _c = _bsmp.ConstBSMP
    _e2v = {
        'CycleEnbl-Mon': _c.V_SIGGEN_ENABLE,
        'CycleType-Sts': _c.V_SIGGEN_TYPE,
        'CycleNrCycles-RB': _c.V_SIGGEN_NUM_CYCLES,
        'CycleIndex-Mon': _c.V_SIGGEN_N,
        'CycleFreq-RB': _c.V_SIGGEN_FREQ,
        'CycleAmpl-RB': _c.V_SIGGEN_AMPLITUDE,
        'CycleOffset-RB': _c.V_SIGGEN_OFFSET,
        'CycleAuxParam-RB': _c.V_SIGGEN_AUX_PARAM}
    _e2f = {
        'PwrState-Sts': (_fields.PwrState, _c.V_PS_STATUS),
        'OpMode-Sts': (_fields.OpMode, _c.V_PS_STATUS),
        'CtrlMode-Mon': (_fields.CtrlMode, _c.V_PS_STATUS),
        'CtrlLoop-Sts': (_fields.CtrlLoop, _c.V_PS_STATUS),
        'Version-Cte': (_fields.Version, _c.V_FIRMWARE_VERSION)}
    _e2c = {
        'PRUBlockIndex-Mon': 'pru_curve_block',
        'PRUSyncPulseCount-Mon': 'pru_sync_pulse_count',
        'PRUCtrlQueueSize-Mon': 'queue_length',
        'BSMPComm-Sts': 'bsmpcomm'}

    _variables = {}

    @property
    def name(self):
        """Model name."""
        raise NotImplementedError

    @property
    def parameters(self):
        """PRU Controller parameters."""
        raise NotImplementedError

    @property
    def bsmp_constants(self):
        """PRU Controller parameters."""
        raise NotImplementedError

    @property
    def entities(self):
        """PRU Controller parameters."""
        raise NotImplementedError

    @property
    def simulation_class(self):
        """PRU Controller parameters."""
        raise NotImplementedError

    @property
    def database(self):
        """Return database."""
        raise NotImplementedError

    @staticmethod
    def create(model):
        """Return FactoryModel object."""
        name_2_factory = {
            'FBP': FactoryFBP,
            'FBP_DCLink': FactoryFBP_DCLink,
            'FBP_FOFB': FactoryFBP,
            'FAC_DCDC': FactoryFAC_DCDC,
            'FAC_2S_DCDC': FactoryFAC_2S_DCDC,
            'FAC_2S_ACDC': FactoryFAC_2S_ACDC,
            'FAC_2P4S_DCDC': FactoryFAC_2P4S_DCDC,
            'FAC_2P4S_ACDC': FactoryFAC_2P4S_ACDC,
            'FAP': FactoryFAP,
            'FAP_2P2S': FactoryFAP_2P2S,
            'FAP_4P': FactoryFAP_4P,
            'Commercial': FactoryCommercial,
        }
        if model in name_2_factory:
            factory = name_2_factory[model]
            return factory()
        else:
            raise ValueError('Model "{}" not defined'.format(model))

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
        if epics_field in self._e2v:
            bsmpid = self._e2v[epics_field]
            return _fields.Variable(pru_controller, device_id, bsmpid)
        elif epics_field in self._e2f:
            field, bsmpid = self._e2f[epics_field]
            return field(_fields.Variable(pru_controller, device_id, bsmpid))
        elif epics_field in self._e2c:
            attr = self._e2c[epics_field]
            return _fields.PRUProperty(pru_controller, attr)
        elif epics_field == 'WfmData-RB':
            return _fields.PRUCurve(pru_controller, device_id)
        elif epics_field == 'WfmIndex-Mon':
            return _fields.Constant(0)
        elif epics_field == 'PRUSyncMode-Mon':
            return _fields.PRUSyncMode(pru_controller)
        elif epics_field == 'CurveWfmRef-Mon':
            return _fields.PSCurve(pru_controller, device_id, 1)
        return None

    def _specific_fields(self, device_id, epics_field, pru_controller):
        # Specific fields
        if epics_field in self._variables:
            var_id = self._variables[epics_field]
            return _fields.Variable(pru_controller, device_id, var_id)
        return None


# Standard PS that supply magnets
class FactoryFBP(FactoryModel):
    """FBP model factory."""

    _variables = {
        'IntlkSoft-Mon':  _bsmp.ConstFBP.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon':  _bsmp.ConstFBP.V_PS_HARD_INTERLOCKS,
        'Current-RB':  _bsmp.ConstFBP.V_PS_SETPOINT,
        'CurrentRef-Mon':  _bsmp.ConstFBP.V_PS_REFERENCE,
        'Current-Mon':  _bsmp.ConstFBP.V_I_LOAD,
        'SwitchesTemperature-Mon': _bsmp.ConstFBP.V_TEMP_SWITCHES,
        'PWMDutyCycle-Mon': _bsmp.ConstFBP.V_DUTY_CYCLE,
    }

    @property
    def name(self):
        """Model name."""
        return 'FBP'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFBP

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFBP()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FBP

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
        elif epics_field == 'CtrlLoop-Sel':
            return _functions.CtrlLoop(device_ids, pru_controller, setpoints)
        elif epics_field == 'Current-SP':
            return _functions.Current(device_ids, pru_controller, setpoints)
        elif epics_field == 'Reset-Cmd':
            return _functions.Command(
                device_ids, pru_controller, _c.F_RESET_INTERLOCKS, setpoints)
        elif epics_field == 'Abort-Cmd':
            return _functions.BSMPFunctionNull()
        elif epics_field == 'CycleDsbl-Cmd':
            return _functions.Command(
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
        elif epics_field == 'BSMPComm-Sel':
            return _functions.BSMPComm(pru_controller, setpoints)
        elif epics_field == 'CurvesAcq-Sel':
            return _functions.PSCurvesAcq(device_ids, pru_controller,
                                          setpoints)
        elif epics_field == 'CurvesAcq-Cmd':
            return _functions.PSCurvesAcqCmd(device_ids, pru_controller,
                                             setpoints)
        else:
            return _functions.BSMPFunctionNull()

    def controller(self, readers, writers, connections,
                   pru_controller, devices):
        """Return controller."""
        return _controller.StandardPSController(
            readers, writers, connections, pru_controller, devices)


class FactoryFBP_FOFB(FactoryFBP):
    """FBP_FOFB model factory."""

    @property
    def name(self):
        """Model name."""
        return 'FBP_FOFB'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFBP

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFBP()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FBP


class FactoryFAC_DCDC(FactoryFBP):
    """FAC model factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFAC_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_DCDC.V_PS_HARD_INTERLOCKS,
        'Current-RB': _bsmp.ConstFAC_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAC_DCDC.V_PS_REFERENCE,
        'Current-Mon': _bsmp.ConstFAC_DCDC.V_I_LOAD_MEAN,
        'Current1-Mon': _bsmp.ConstFAC_DCDC.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAC_DCDC.V_I_LOAD2,
        'LoadVoltage-Mon': _bsmp.ConstFAC_DCDC.V_V_LOAD,
        'InductorsTemperature-Mon': _bsmp.ConstFAC_DCDC.V_TEMP_INDUCTORS,
        'IGBTSTemperature-Mon': _bsmp.ConstFAC_DCDC.V_TEMP_IGBTS,
        'PWMDutyCycle-Mon': _bsmp.ConstFAC_DCDC.V_DUTY_CYCLE,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_DCDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_DCDC


class FactoryFAC_2S_DCDC(FactoryFBP):
    """FAC_2S_DCDC model factory."""

    _variables = {
        'Current-RB': _bsmp.ConstFAC_2S_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAC_2S_DCDC.V_PS_REFERENCE,
        'IntlkSoft-Mon': _bsmp.ConstFAC_2S_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_2S_DCDC.V_PS_HARD_INTERLOCKS,
        'Current-Mon': _bsmp.ConstFAC_2S_DCDC.V_I_LOAD_MEAN,
        'Current1-Mon': _bsmp.ConstFAC_2S_DCDC.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAC_2S_DCDC.V_I_LOAD2,
        'LoadVoltage-Mon': _bsmp.ConstFAC_2S_DCDC.V_V_LOAD,
        'Module1Voltage-Mon': _bsmp.ConstFAC_2S_DCDC.V_V_OUT_1,
        'Module2Voltage-Mon': _bsmp.ConstFAC_2S_DCDC.V_V_OUT_2,
        'CapacitorBank1Voltage-Mon':
            _bsmp.ConstFAC_2S_DCDC.V_V_CAPBANK_1,
        'CapacitorBank2Voltage-Mon':
            _bsmp.ConstFAC_2S_DCDC.V_V_CAPBANK_2,
        'PWMDutyCycle1-Mon': _bsmp.ConstFAC_2S_DCDC.V_DUTY_CYCLE_1,
        'PWMDutyCycle2-Mon': _bsmp.ConstFAC_2S_DCDC.V_DUTY_CYCLE_2,
        'PWMDutyDiff-Mon': _bsmp.ConstFAC_2S_DCDC.V_DUTY_DIFF,
        'IIB1InductorsTemperature-Mon':
            _bsmp.ConstFAC_2S_DCDC.V_TEMP_INDUCTOR_IIB_1,
        'IIB1HeatSinkTemperature-Mon':
            _bsmp.ConstFAC_2S_DCDC.V_TEMP_HEATSINK_IIB_1,
        'IIB2InductorsTemperature-Mon':
            _bsmp.ConstFAC_2S_DCDC.V_TEMP_INDUCTOR_IIB_2,
        'IIB2HeatSinkTemperature-Mon':
            _bsmp.ConstFAC_2S_DCDC.V_TEMP_HEATSINK_IIB_2,
        'IntlkIIB1-Mon': _bsmp.ConstFAC_2S_DCDC.V_IIB_INTERLOCKS_1,
        'IntlkIIB2-Mon': _bsmp.ConstFAC_2S_DCDC.V_IIB_INTERLOCKS_2,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2S_DCDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_2S_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_2S_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_2S_DCDC


class FactoryFAC_2P4S_DCDC(FactoryFAC_DCDC):
    """FAC_2P4S_DCDC model factory."""

    _variables = {
        'Current-RB': _bsmp.ConstFAC_2P4S_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_PS_REFERENCE,
        'IntlkSoft-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_PS_HARD_INTERLOCKS,
        'Current-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_LOAD_MEAN,
        'Current1-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_LOAD2,
        'LoadVoltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_LOAD,
        'CapacitorBank1Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_1,
        'CapacitorBank2Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_2,
        'CapacitorBank3Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_3,
        'CapacitorBank4Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_4,
        'CapacitorBank5Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_5,
        'CapacitorBank6Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_6,
        'CapacitorBank7Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_7,
        'CapacitorBank8Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_8,
        'Module1Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_1,
        'Module2Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_2,
        'Module3Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_3,
        'Module4Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_4,
        'Module5Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_5,
        'Module6Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_6,
        'Module7Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_7,
        'Module8Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT_8,
        'PWMDutyCycle1-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_1,
        'PWMDutyCycle2-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_2,
        'PWMDutyCycle3-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_3,
        'PWMDutyCycle4-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_4,
        'PWMDutyCycle5-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_5,
        'PWMDutyCycle6-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_6,
        'PWMDutyCycle7-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_7,
        'PWMDutyCycle8-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_8,
        'Arm1Current-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_ARM_1,
        'Arm2Current-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_ARM_2,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2P4S_DCDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_2P4S_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_2P4S_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_2P4S_DCDC


class FactoryFAP(FactoryFBP):
    """FAP model factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFAP.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAP.V_PS_HARD_INTERLOCKS,
        'IntlkIIB-Mon': _bsmp.ConstFAP.V_IIB_INTERLOCKS,
        'Current-RB': _bsmp.ConstFAP.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAP.V_PS_REFERENCE,
        'Current-Mon': _bsmp.ConstFAP.V_I_LOAD_MEAN,
        'Current1-Mon': _bsmp.ConstFAP.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAP.V_I_LOAD2,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAP'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAP

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAP()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAP


class FactoryFAP_4P(FactoryFBP):
    """FAP_4P model factory."""

    @property
    def name(self):
        """Model name."""
        return 'FAP_4P'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAP_4P

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAP_4P()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAP_4P


class FactoryFAP_2P2S(FactoryFBP):
    """FAP_2P2S model factory."""

    _variables = {
        'IntlkSoft-Mon':  _bsmp.ConstFAP_2P2S.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon':  _bsmp.ConstFAP_2P2S.V_PS_HARD_INTERLOCKS,
        'Current-RB':  _bsmp.ConstFAP_2P2S.V_PS_SETPOINT,
        'CurrentRef-Mon':  _bsmp.ConstFAP_2P2S.V_PS_REFERENCE,
        'Current-Mon':  _bsmp.ConstFAP_2P2S.V_I_LOAD_MEAN,
        'Current1-Mon': _bsmp.ConstFAP_2P2S.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAP_2P2S.V_I_LOAD2,
        'IIB1InductorTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_1,
        'IIB1HeatSinkTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_1,
        'IIB2InductorTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_2,
        'IIB2HeatSinkTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_2,
        'IIB3InductorTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_3,
        'IIB3HeatSinkTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_3,
        'IIB4InductorTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_4,
        'IIB4HeatSinkTemperature-Mon': _bsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_4,
        'Intlk1IIB-Mon': _bsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_1,
        'Intlk2IIB-Mon': _bsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_2,
        'Intlk3IIB-Mon': _bsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_3,
        'Intlk4IIB-Mon': _bsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_4,
        'Mod1Current-Mon': _bsmp.ConstFAP_2P2S.V_I_MOD_1,
        'Mod2Current-Mon': _bsmp.ConstFAP_2P2S.V_I_MOD_2,
        'Mod3Current-Mon': _bsmp.ConstFAP_2P2S.V_I_MOD_3,
        'Mod4Current-Mon': _bsmp.ConstFAP_2P2S.V_I_MOD_4,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAP_2P2S'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAP_2P2S

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAP_2P2S()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAP_2P2S


class FactoryCommercial(FactoryFAC_DCDC):
    """Commercial model factory."""

    @property
    def name(self):
        """Model name."""
        return 'Commercial'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_DCDC


# --- ACDC ---


class FactoryFBP_DCLink(FactoryModel):
    """FBP_DCLink factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFBP_DCLink.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFBP_DCLink.V_PS_HARD_INTERLOCKS,
        'ModulesStatus-Mon': _bsmp.ConstFBP_DCLink.V_MODULES_STATUS,
        'Voltage-RB': _bsmp.ConstFBP_DCLink.V_PS_SETPOINT,
        'VoltageRef-Mon': _bsmp.ConstFBP_DCLink.V_PS_REFERENCE,
        'Voltage-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT,
        'Voltage1-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT_1,
        'Voltage2-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT_2,
        'Voltage3-Mon': _bsmp.ConstFBP_DCLink.V_V_OUT_3,
        'VoltageDig-Mon': _bsmp.ConstFBP_DCLink.V_DIG_POT_TAP,
    }

    @property
    def name(self):
        """Model name."""
        return 'FBP_DCLink'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFBP_DCLink

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFBP_DCLink()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FBP_DCLink

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
            return _functions.Command(
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


class FactoryFAC_2S_ACDC(FactoryModel):
    """FAC_2S_ACDC factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFAC_2S_ACDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_2S_ACDC.V_PS_HARD_INTERLOCKS,
        'CapacitorBankVoltage-RB': _bsmp.ConstFAC_2S_ACDC.V_PS_SETPOINT,
        'CapacitorBankVoltageRef-Mon': _bsmp.ConstFAC_2S_ACDC.V_PS_REFERENCE,
        'CapacitorBankVoltage-Mon': _bsmp.ConstFAC_2S_ACDC.V_V_CAPBANK,
        'RectifierVoltage-Mon': _bsmp.ConstFAC_2S_ACDC.V_V_OUT_RECTIFIER,
        'RectifierCurrent-Mon': _bsmp.ConstFAC_2S_ACDC.V_I_OUT_RECTIFIER,
        'HeatSinkTemperature-Mon': _bsmp.ConstFAC_2S_ACDC.V_TEMP_HEATSINK,
        'InductorsTemperature-Mon': _bsmp.ConstFAC_2S_ACDC.V_TEMP_INDUCTORS,
        'PWMDutyCycle-Mon': _bsmp.ConstFAC_2S_ACDC.V_DUTY_CYCLE,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2S_ACDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_2S_ACDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_2S_ACDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_2S_ACDC

    def function(self, device_ids, epics_field, pru_controller, setpoints):
        """Return function."""
        _c = _bsmp.ConstFAC_2S_ACDC
        if epics_field == 'PwrState-Sel':
            return _functions.PSPwrState(device_ids, pru_controller, setpoints)
        elif epics_field == 'OpMode-Sel':
            return _functions.PSOpMode(
                device_ids,
                _functions.BSMPFunction(
                    device_ids, pru_controller, _c.F_SELECT_OP_MODE),
                setpoints)
        elif epics_field == 'CtrlLoop-Sel':
            return _functions.CtrlLoop(device_ids, pru_controller, setpoints)
        elif epics_field == 'CapacitorBankVoltage-SP':
            return _functions.BSMPFunction(
                device_ids, pru_controller, _c.F_SET_SLOWREF, setpoints)
        elif epics_field == 'Reset-Cmd':
            return _functions.Command(
                device_ids, pru_controller, _c.F_RESET_INTERLOCKS, setpoints)
        elif epics_field == 'Abort-Cmd':
            return _functions.BSMPFunctionNull()
        elif epics_field == 'BSMPComm-Sel':
            return _functions.BSMPComm(pru_controller, setpoints)
        else:
            return _functions.BSMPFunctionNull()

    def controller(self, readers, writers, connections,
                   pru_controller, devices):
        """Return controller."""
        return _controller.PSController(
            readers, writers, connections, pru_controller)


class FactoryFAC_2P4S_ACDC(FactoryFAC_2S_ACDC):
    """FAC_2P4S_ACDC factoy."""

    @property
    def name(self):
        """Model name."""
        return 'FAC_2P4S_ACDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_2P4S_ACDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_2P4S_ACDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_2P4S_ACDC
