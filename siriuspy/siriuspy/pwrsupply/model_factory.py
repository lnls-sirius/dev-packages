"""Model abstract factory."""
from siriuspy.pwrsupply import fields as _fields
from siriuspy.pwrsupply import functions as _functions
from siriuspy.pwrsupply import bsmp as _bsmp
from siriuspy.pwrsupply import controller as _controller

from siriuspy.pwrsupply.bsmp import EntitiesFBP as _EntitiesFBP
from siriuspy.pwrsupply.bsmp import EntitiesFBP_DCLink as _EntitiesFBP_DCLink
from siriuspy.pwrsupply.bsmp import EntitiesFAC_DCDC as _EntitiesFAC_DCDC
from siriuspy.pwrsupply.bsmp import EntitiesFAC_ACDC as _EntitiesFAC_ACDC
from siriuspy.pwrsupply.bsmp import \
    EntitiesFAC_2P4S_DCDC as _EntitiesFAC_2P4S_DCDC
from siriuspy.pwrsupply.bsmp import \
    EntitiesFAC_2P4S_ACDC as _EntitiesFAC_2P4S_ACDC
from siriuspy.pwrsupply.bsmp import EntitiesFAP as _EntitiesFAP

from siriuspy.pwrsupply.bsmp import ConstFBP as _cFBP
from siriuspy.pwrsupply.bsmp import ConstFBP_DCLink as _cFBP_DCLink
from siriuspy.pwrsupply.bsmp import ConstFAC_DCDC as _cFAC_DCDC
from siriuspy.pwrsupply.bsmp import ConstFAC_ACDC as _cFAC_ACDC
from siriuspy.pwrsupply.bsmp import ConstFAC_2P4S_DCDC as _cFAC_2P4S_DCDC
from siriuspy.pwrsupply.bsmp import ConstFAC_2P4S_ACDC as _cFAC_2P4S_ACDC
from siriuspy.pwrsupply.bsmp import ConstFAP as _cFAP

from siriuspy.bsmp import BSMP as _BSMP

from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FBP as _BSMPSim_FBP
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FBP_DCLink as _BSMPSim_FBP_DCLink
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FAC_DCDC as _BSMPSim_FAC_DCDC
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FAC_ACDC as _BSMPSim_FAC_ACDC
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FAC_2P4S_DCDC as _BSMPSim_FAC_2P4S_DCDC
from siriuspy.pwrsupply.bsmp_sim import \
    BSMPSim_FAC_2P4S_ACDC as _BSMPSim_FAC_2P4S_ACDC
from siriuspy.pwrsupply.bsmp_sim import BSMPSim_FAP as _BSMPSim_FAP


from siriuspy.pwrsupply.pru import Const as _PRUConst


class ModelFactory:
    """Abstract factory for power supply models."""

    _variables = {}

    # def __init__(self, name, parameters):
    #     """Set model name."""
    #     self._name = name
    #     self._parameters = parameters

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
            return FACACDCFactory()
        elif model == 'FAC_2S_DCDC':
            return FAC2SDCDCFactory()
        elif model == 'FAC_2S_ACDC':
            return FAC2SACDCFactory()
        elif model == 'FAC_2P4S_DCDC':
            return FAC2P4SDCDCFactory()
        elif model == 'FAC_2P4S_ACDC':
            return FAC2P4SACDCFactory()

        elif model == 'FAP':
            return FAPFactory()
        elif model == 'FAP_2P2S_MASTER':
            return FAP2P2SMASTERFactory()
        elif model == 'FAP_4P_Master':
            return FAP4PMasterFactory()
        elif model == 'FAP_4P_Slave':
            return FAP4PSlaveFactory()

        elif model == 'Commercial':
            return CommercialFactory()
        else:
            raise ValueError('{} not defined'.format(model))

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
        elif epics_field == 'BSMPComm-Sts':
            return _fields.PRUProperty(pru_controller, 'bsmpcomm')

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

    @property
    def name(self):
        """Model name."""
        return 'FBP'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FBP

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
        elif epics_field == 'BSMPComm-Sel':
            return _functions.BSMPComm(pru_controller, setpoints)
        else:
            return _functions.BSMPFunctionNull()

    def controller(self, readers, writers, connections,
                   pru_controller, devices):
        """Return controller."""
        return _controller.StandardPSController(
            readers, writers, connections, pru_controller, devices)


class FBPFOFBFactory(FBPFactory):
    """FBP FOFB model factory."""

    @property
    def name(self):
        """Model name."""
        return 'FBP_FOFB'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FBP  # change to FBP_FOFB

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

    @property
    def name(self):
        """Model name."""
        return 'FAC_DCDC'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAC

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


class FAC2SDCDCFactory(FACFactory):
    """FAC 2S model factory."""

    @property
    def name(self):
        """Model name."""
        return 'FAC_2S_DCDC'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAC  # TODO: Change to PRUCParms_2S_DCDC

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


class FAC2P4SDCDCFactory(FACFactory):
    """FAC 2P4S model factory."""

    _variables = {
        'Current-RB': _bsmp.ConstFAC_2P4S_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_PS_REFERENCE,
        'IntlkSoft-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_PS_HARD_INTERLOCKS,
        'Current-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_LOAD2,
        'LoadVoltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_LOAD,
        'CapacitorBank1Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK1,
        'CapacitorBank2Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK2,
        'CapacitorBank3Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK3,
        'CapacitorBank4Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK4,
        'CapacitorBank5Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK5,
        'CapacitorBank6Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK6,
        'CapacitorBank7Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK7,
        'CapacitorBank8Voltage-Mon':
            _bsmp.ConstFAC_2P4S_DCDC.V_V_CAPACITOR_BANK8,
        'Module1Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT1,
        'Module2Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT2,
        'Module3Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT3,
        'Module4Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT4,
        'Module5Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT5,
        'Module6Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT6,
        'Module7Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT7,
        'Module8Voltage-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_V_OUT8,
        'PWMDutyCycle1-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE1,
        'PWMDutyCycle2-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE2,
        'PWMDutyCycle3-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE3,
        'PWMDutyCycle4-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE4,
        'PWMDutyCycle5-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE5,
        'PWMDutyCycle6-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE6,
        'PWMDutyCycle7-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE7,
        'PWMDutyCycle8-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE8,
        'Arm1Current-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_ARM1,
        'Arm2Current-Mon': _bsmp.ConstFAC_2P4S_DCDC.V_I_ARM2,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2P4S_DCDC'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAC_2P4S

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


class FAPFactory(FBPFactory):
    """FAP model factory."""

    _variables = {
        'IntlkSoft-Mon': _bsmp.ConstFAP.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAP.V_PS_HARD_INTERLOCKS,
        'Current-RB': _bsmp.ConstFAP.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAP.V_PS_REFERENCE,
        'Current-Mon': _bsmp.ConstFAP.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAP.V_I_LOAD2,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAP'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAP

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


class FAP2P2SMASTERFactory(FBPFactory):
    """FAP model factory."""

    @property
    def name(self):
        """Model name."""
        return 'FAP_2P2S_MASTER'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FBP  # TODO: change to FAP_2P2S_MASTER

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


class FAP4PMasterFactory(FBPFactory):
    """FAP model factory."""

    @property
    def name(self):
        """Model name."""
        return 'FAP_4P_Master'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FBP  # TODO: change to FAP_4P_Master

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


class FAP4PSlaveFactory(FBPFactory):
    """FAP model factory."""

    @property
    def name(self):
        """Model name."""
        return 'FAP_4P_Slave'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FBP  # TODO: change to FAP_4P_Slave

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

    # @property
    # def database(self):
    #     """Return model database."""
    #     return _get_ps_FAP_4P_Slave_propty_database()


class CommercialFactory(FACFactory):
    """Commercial model factory."""

    @property
    def name(self):
        """Model name."""
        return 'Commercial'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAC  # TODO: change to commercial

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

    @property
    def name(self):
        """Model name."""
        return 'FBP_DCLink'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FBP_DCLink

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


class FACACDCFactory(FBPDCLinkFactory):
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

    @property
    def name(self):
        """Model name."""
        return 'FAC_ACDC'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAC_ACDC

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_ACDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_ACDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_ACDC


class FAC2SACDCFactory(FACACDCFactory):
    """FAC 2S factory."""

    @property
    def name(self):
        """Model name."""
        return 'FAC_2S_ACDC'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAC_ACDC  # TODO: change to FAC_2S_ACDC

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _cFAC_ACDC

    @property
    def entities(self):
        """Model entities."""
        return _EntitiesFAC_ACDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _BSMPSim_FAC_ACDC


class FAC2P4SACDCFactory(FACACDCFactory):
    """FAC 2P4S factoy."""

    @property
    def name(self):
        """Model name."""
        return 'FAC_2P4S_ACDC'

    @property
    def parameters(self):
        """PRU Controller parameters."""
        return PRUCParms_FAC_2P4S_ACDC

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


# --- PRUC Parameter classes ---

class _PRUCParms:
    """PRUC parameters.

    Namespace to group useful parameters used by PRUController.
    """

    # group ids
    ALL = 0
    READONLY = 1
    WRITEABLE = 2
    ALLRELEVANT = 3
    SYNCOFF = 4
    MIRROR = 5

    SLOWREF = SYNCOFF
    MIGWFM = MIRROR
    CYCLE = SYNCOFF
    RMPWFM = MIRROR

    PRU = _PRUConst


class PRUCParms_FBP(_PRUCParms):
    """FBP-specific PRUC parameters."""

    FREQ_RAMP = 2.0  # [Hz]
    FREQ_SCAN = 10.0  # [Hz]

    # UDC model
    # udcmodel = 'FBP'
    model = ModelFactory.get('FBP')
    ConstBSMP = model.bsmp_constants
    Entities = model.entities

    groups = dict()
    # reserved variable groups (not to be used)
    groups[_PRUCParms.ALL] = tuple(sorted(Entities.list_variables(0)))
    groups[_PRUCParms.READONLY] = tuple(sorted(Entities.list_variables(1)))
    groups[_PRUCParms.WRITEABLE] = tuple(sorted(Entities.list_variables(2)))
    # new variable groups usefull for PRUController.
    groups[_PRUCParms.ALLRELEVANT] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_FIRMWARE_VERSION,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FBP variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD,
        ConstBSMP.V_V_LOAD,
        ConstBSMP.V_V_DCLINK,
        ConstBSMP.V_TEMP_SWITCHES,
        ConstBSMP.V_DUTY_CYCLE,)
    groups[_PRUCParms.SYNCOFF] = (
        # =======================================================
        # cmd exec_funcion read_group:
        #   17.2 ± 0.3 ms @ BBB1, 4 ps as measured from Python
        #   180us @ BBB1, 1 ps as measured in the oscilloscope
        # =======================================================
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FSB variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD,
        ConstBSMP.V_V_LOAD,
        ConstBSMP.V_V_DCLINK,
        ConstBSMP.V_TEMP_SWITCHES,)
    groups[_PRUCParms.MIRROR] = (
        # --- mirror variables ---
        ConstBSMP.V_PS_STATUS_1,
        ConstBSMP.V_PS_STATUS_2,
        ConstBSMP.V_PS_STATUS_3,
        ConstBSMP.V_PS_STATUS_4,
        ConstBSMP.V_PS_SETPOINT_1,
        ConstBSMP.V_PS_SETPOINT_2,
        ConstBSMP.V_PS_SETPOINT_3,
        ConstBSMP.V_PS_SETPOINT_4,
        ConstBSMP.V_PS_REFERENCE_1,
        ConstBSMP.V_PS_REFERENCE_2,
        ConstBSMP.V_PS_REFERENCE_3,
        ConstBSMP.V_PS_REFERENCE_4,
        ConstBSMP.V_PS_SOFT_INTERLOCKS_1,
        ConstBSMP.V_PS_SOFT_INTERLOCKS_2,
        ConstBSMP.V_PS_SOFT_INTERLOCKS_3,
        ConstBSMP.V_PS_SOFT_INTERLOCKS_4,
        ConstBSMP.V_PS_HARD_INTERLOCKS_1,
        ConstBSMP.V_PS_HARD_INTERLOCKS_2,
        ConstBSMP.V_PS_HARD_INTERLOCKS_3,
        ConstBSMP.V_PS_HARD_INTERLOCKS_4,
        ConstBSMP.V_I_LOAD_1,
        ConstBSMP.V_I_LOAD_2,
        ConstBSMP.V_I_LOAD_3,
        ConstBSMP.V_I_LOAD_4,)


class PRUCParms_FBP_DCLink(_PRUCParms):
    """FBP_DCLink-specific PRUC parameters."""

    FREQ_RAMP = 2.0  # [Hz]
    FREQ_SCAN = 2.0  # [Hz]

    # UDC model
    model = ModelFactory.get('FBP_DCLink')
    ConstBSMP = model.bsmp_constants
    Entities = model.entities

    groups = dict()
    # reserved variable groups (not to be used)
    groups[_PRUCParms.ALL] = tuple(sorted(Entities.list_variables(0)))
    groups[_PRUCParms.READONLY] = tuple(sorted(Entities.list_variables(1)))
    groups[_PRUCParms.WRITEABLE] = tuple(sorted(Entities.list_variables(2)))
    # new variable groups usefull for PRUController.
    groups[_PRUCParms.ALLRELEVANT] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_FIRMWARE_VERSION,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        # ConstBSMP.V_SIGGEN_ENABLE,
        # ConstBSMP.V_SIGGEN_TYPE,
        # ConstBSMP.V_SIGGEN_NUM_CYCLES,
        # ConstBSMP.V_SIGGEN_N,
        # ConstBSMP.V_SIGGEN_FREQ,
        # ConstBSMP.V_SIGGEN_AMPLITUDE,
        # ConstBSMP.V_SIGGEN_OFFSET,
        # ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FBP_DCLink variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_DIGITAL_INPUTS,
        ConstBSMP.V_V_OUT,
        ConstBSMP.V_V_OUT_1,
        ConstBSMP.V_V_OUT_2,
        ConstBSMP.V_V_OUT_3,
        ConstBSMP.V_DIG_POT_TAP,)
    groups[_PRUCParms.SYNCOFF] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        # ConstBSMP.V_SIGGEN_ENABLE,
        # ConstBSMP.V_SIGGEN_TYPE,
        # ConstBSMP.V_SIGGEN_NUM_CYCLES,
        # ConstBSMP.V_SIGGEN_N,
        # ConstBSMP.V_SIGGEN_FREQ,
        # ConstBSMP.V_SIGGEN_AMPLITUDE,
        # ConstBSMP.V_SIGGEN_OFFSET,
        # ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FBP_DCLink variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_DIGITAL_INPUTS,
        ConstBSMP.V_V_OUT,
        ConstBSMP.V_V_OUT_1,
        ConstBSMP.V_V_OUT_2,
        ConstBSMP.V_V_OUT_3,
        ConstBSMP.V_DIG_POT_TAP,)
    groups[_PRUCParms.MIRROR] = groups[_PRUCParms.SYNCOFF]


class PRUCParms_FAC(_PRUCParms):
    """FAC-specific PRUC parameters.

    Represent FAC, FAC_2S, FAC_2P4S psmodels.
    """

    FREQ_RAMP = 2.0  # [Hz]
    FREQ_SCAN = 10.0  # [Hz]

    # UDC model
    model = ModelFactory.get('FAC_DCDC')
    ConstBSMP = model.bsmp_constants
    Entities = model.entities

    groups = dict()
    # reserved variable groups (not to be used)
    groups[_PRUCParms.ALL] = tuple(sorted(Entities.list_variables(0)))
    groups[_PRUCParms.READONLY] = tuple(sorted(Entities.list_variables(1)))
    groups[_PRUCParms.WRITEABLE] = tuple(sorted(Entities.list_variables(2)))
    # new variable groups usefull for PRUController.
    groups[_PRUCParms.ALLRELEVANT] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_FIRMWARE_VERSION,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD1,
        ConstBSMP.V_I_LOAD2,
        ConstBSMP.V_V_LOAD,
        ConstBSMP.V_V_CAPACITOR_BANK,
        ConstBSMP.V_TEMP_INDUCTORS,
        ConstBSMP.V_TEMP_IGBTS,
        ConstBSMP.V_DUTY_CYCLE,)
    groups[_PRUCParms.SYNCOFF] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD1,
        ConstBSMP.V_I_LOAD2,
        ConstBSMP.V_V_LOAD,
        ConstBSMP.V_V_CAPACITOR_BANK,
        ConstBSMP.V_TEMP_INDUCTORS,
        ConstBSMP.V_TEMP_IGBTS,
        ConstBSMP.V_DUTY_CYCLE,)
    groups[_PRUCParms.MIRROR] = groups[_PRUCParms.SYNCOFF]


class PRUCParms_FAC_ACDC(_PRUCParms):
    """FAC_ACDC-specific PRUC parameters."""

    FREQ_RAMP = 2.0  # [Hz]
    FREQ_SCAN = 2.0  # [Hz]

    # UDC model
    model = ModelFactory.get('FAC_ACDC')
    ConstBSMP = model.bsmp_constants
    Entities = model.entities

    groups = dict()
    # reserved variable groups (not to be used)
    groups[_PRUCParms.ALL] = tuple(sorted(Entities.list_variables(0)))
    groups[_PRUCParms.READONLY] = tuple(sorted(Entities.list_variables(1)))
    groups[_PRUCParms.WRITEABLE] = tuple(sorted(Entities.list_variables(2)))
    # new variable groups usefull for PRUController.
    groups[_PRUCParms.ALLRELEVANT] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_FIRMWARE_VERSION,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        # ConstBSMP.V_SIGGEN_ENABLE,
        # ConstBSMP.V_SIGGEN_TYPE,
        # ConstBSMP.V_SIGGEN_NUM_CYCLES,
        # ConstBSMP.V_SIGGEN_N,
        # ConstBSMP.V_SIGGEN_FREQ,
        # ConstBSMP.V_SIGGEN_AMPLITUDE,
        # ConstBSMP.V_SIGGEN_OFFSET,
        # ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC_ACDC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_CAPACITOR_BANK,
        ConstBSMP.V_OUT_RECTIFIER,
        ConstBSMP.I_OUT_RECTIFIER,
        ConstBSMP.TEMP_HEATSINK,
        ConstBSMP.TEMP_INDUCTORS,
        ConstBSMP.DUTY_CYCLE,)
    groups[_PRUCParms.SYNCOFF] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        # ConstBSMP.V_SIGGEN_ENABLE,
        # ConstBSMP.V_SIGGEN_TYPE,
        # ConstBSMP.V_SIGGEN_NUM_CYCLES,
        # ConstBSMP.V_SIGGEN_N,
        # ConstBSMP.V_SIGGEN_FREQ,
        # ConstBSMP.V_SIGGEN_AMPLITUDE,
        # ConstBSMP.V_SIGGEN_OFFSET,
        # ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC_ACDC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_CAPACITOR_BANK,
        ConstBSMP.V_OUT_RECTIFIER,
        ConstBSMP.I_OUT_RECTIFIER,
        ConstBSMP.TEMP_HEATSINK,
        ConstBSMP.TEMP_INDUCTORS,
        ConstBSMP.DUTY_CYCLE,)
    groups[_PRUCParms.MIRROR] = groups[_PRUCParms.SYNCOFF]


class PRUCParms_FAC_2P4S(_PRUCParms):
    """FAC-specific PRUC parameters.

    Represent FAC_2P4S psmodels.
    """

    FREQ_RAMP = 2.0  # [Hz]
    FREQ_SCAN = 10.0  # [Hz]

    # UDC model
    model = ModelFactory.get('FAC_2P4S_DCDC')
    ConstBSMP = model.bsmp_constants
    Entities = model.entities

    groups = dict()
    # reserved variable groups (not to be used)
    groups[_PRUCParms.ALL] = tuple(sorted(Entities.list_variables(0)))
    groups[_PRUCParms.READONLY] = tuple(sorted(Entities.list_variables(1)))
    groups[_PRUCParms.WRITEABLE] = tuple(sorted(Entities.list_variables(2)))
    # new variable groups usefull for PRUController.
    groups[_PRUCParms.ALLRELEVANT] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_FIRMWARE_VERSION,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD1,
        ConstBSMP.V_I_LOAD2,
        ConstBSMP.V_V_LOAD,
        ConstBSMP.V_V_CAPACITOR_BANK1,
        ConstBSMP.V_V_CAPACITOR_BANK2,
        ConstBSMP.V_V_CAPACITOR_BANK3,
        ConstBSMP.V_V_CAPACITOR_BANK4,
        ConstBSMP.V_V_CAPACITOR_BANK5,
        ConstBSMP.V_V_CAPACITOR_BANK6,
        ConstBSMP.V_V_CAPACITOR_BANK7,
        ConstBSMP.V_V_CAPACITOR_BANK8,
        ConstBSMP.V_V_OUT1,
        ConstBSMP.V_V_OUT2,
        ConstBSMP.V_V_OUT3,
        ConstBSMP.V_V_OUT4,
        ConstBSMP.V_V_OUT5,
        ConstBSMP.V_V_OUT6,
        ConstBSMP.V_V_OUT7,
        ConstBSMP.V_V_OUT8,
        ConstBSMP.V_DUTY_CYCLE1,
        ConstBSMP.V_DUTY_CYCLE2,
        ConstBSMP.V_DUTY_CYCLE3,
        ConstBSMP.V_DUTY_CYCLE4,
        ConstBSMP.V_DUTY_CYCLE5,
        ConstBSMP.V_DUTY_CYCLE6,
        ConstBSMP.V_DUTY_CYCLE7,
        ConstBSMP.V_DUTY_CYCLE8,
        ConstBSMP.V_I_ARM1,
        ConstBSMP.V_I_ARM2)
    groups[_PRUCParms.SYNCOFF] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD1,
        ConstBSMP.V_I_LOAD2,
        ConstBSMP.V_V_LOAD,
        ConstBSMP.V_V_CAPACITOR_BANK1,
        ConstBSMP.V_V_CAPACITOR_BANK2,
        ConstBSMP.V_V_CAPACITOR_BANK3,
        ConstBSMP.V_V_CAPACITOR_BANK4,
        ConstBSMP.V_V_CAPACITOR_BANK5,
        ConstBSMP.V_V_CAPACITOR_BANK6,
        ConstBSMP.V_V_CAPACITOR_BANK7,
        ConstBSMP.V_V_CAPACITOR_BANK8,
        ConstBSMP.V_V_OUT1,
        ConstBSMP.V_V_OUT2,
        ConstBSMP.V_V_OUT3,
        ConstBSMP.V_V_OUT4,
        ConstBSMP.V_V_OUT5,
        ConstBSMP.V_V_OUT6,
        ConstBSMP.V_V_OUT7,
        ConstBSMP.V_V_OUT8,
        ConstBSMP.V_DUTY_CYCLE1,
        ConstBSMP.V_DUTY_CYCLE2,
        ConstBSMP.V_DUTY_CYCLE3,
        ConstBSMP.V_DUTY_CYCLE4,
        ConstBSMP.V_DUTY_CYCLE5,
        ConstBSMP.V_DUTY_CYCLE6,
        ConstBSMP.V_DUTY_CYCLE7,
        ConstBSMP.V_DUTY_CYCLE8,
        ConstBSMP.V_I_ARM1,
        ConstBSMP.V_I_ARM2)
    groups[_PRUCParms.MIRROR] = groups[_PRUCParms.SYNCOFF]


class PRUCParms_FAC_2P4S_ACDC(_PRUCParms):
    """FAC_ACDC-specific PRUC parameters."""

    FREQ_RAMP = 2.0  # [Hz]
    FREQ_SCAN = 2.0  # [Hz]

    # UDC model
    model = ModelFactory.get('FAC_ACDC')
    ConstBSMP = model.bsmp_constants
    Entities = model.entities

    groups = dict()
    # reserved variable groups (not to be used)
    groups[_PRUCParms.ALL] = tuple(sorted(Entities.list_variables(0)))
    groups[_PRUCParms.READONLY] = tuple(sorted(Entities.list_variables(1)))
    groups[_PRUCParms.WRITEABLE] = tuple(sorted(Entities.list_variables(2)))
    # new variable groups usefull for PRUController.
    groups[_PRUCParms.ALLRELEVANT] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_FIRMWARE_VERSION,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        # ConstBSMP.V_SIGGEN_ENABLE,
        # ConstBSMP.V_SIGGEN_TYPE,
        # ConstBSMP.V_SIGGEN_NUM_CYCLES,
        # ConstBSMP.V_SIGGEN_N,
        # ConstBSMP.V_SIGGEN_FREQ,
        # ConstBSMP.V_SIGGEN_AMPLITUDE,
        # ConstBSMP.V_SIGGEN_OFFSET,
        # ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC_ACDC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_CAPACITOR_BANK,
        ConstBSMP.V_OUT_RECTIFIER,
        ConstBSMP.I_OUT_RECTIFIER,
        ConstBSMP.TEMP_HEATSINK,
        ConstBSMP.TEMP_INDUCTORS,
        ConstBSMP.DUTY_CYCLE,)
    groups[_PRUCParms.SYNCOFF] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        # ConstBSMP.V_SIGGEN_ENABLE,
        # ConstBSMP.V_SIGGEN_TYPE,
        # ConstBSMP.V_SIGGEN_NUM_CYCLES,
        # ConstBSMP.V_SIGGEN_N,
        # ConstBSMP.V_SIGGEN_FREQ,
        # ConstBSMP.V_SIGGEN_AMPLITUDE,
        # ConstBSMP.V_SIGGEN_OFFSET,
        # ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAC_ACDC variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_CAPACITOR_BANK,
        ConstBSMP.V_OUT_RECTIFIER,
        ConstBSMP.I_OUT_RECTIFIER,
        ConstBSMP.TEMP_HEATSINK,
        ConstBSMP.TEMP_INDUCTORS,
        ConstBSMP.DUTY_CYCLE,)
    groups[_PRUCParms.MIRROR] = groups[_PRUCParms.SYNCOFF]


class PRUCParms_FAP(_PRUCParms):
    """FAC-specific PRUC parameters.

    Represent FAP
    """

    FREQ_RAMP = 2.0  # [Hz]
    FREQ_SCAN = 10.0  # [Hz]

    # UDC model
    model = ModelFactory.get('FAP')
    ConstBSMP = model.bsmp_constants
    Entities = model.entities

    groups = dict()
    # reserved variable groups (not to be used)
    groups[_PRUCParms.ALL] = tuple(sorted(Entities.list_variables(0)))
    groups[_PRUCParms.READONLY] = tuple(sorted(Entities.list_variables(1)))
    groups[_PRUCParms.WRITEABLE] = tuple(sorted(Entities.list_variables(2)))
    # new variable groups usefull for PRUController.
    groups[_PRUCParms.ALLRELEVANT] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_FIRMWARE_VERSION,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAP variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD1,
        ConstBSMP.V_I_LOAD2,
        ConstBSMP.V_V_DCLINK,
        ConstBSMP.V_I_IGBT_1,
        ConstBSMP.V_I_IGBT_2,
        ConstBSMP.V_DUTY_CYCLE_1,
        ConstBSMP.V_DUTY_CYCLE_1,
        ConstBSMP.V_DUTY_DIFF,)
    groups[_PRUCParms.SYNCOFF] = (
        # --- common variables
        ConstBSMP.V_PS_STATUS,
        ConstBSMP.V_PS_SETPOINT,
        ConstBSMP.V_PS_REFERENCE,
        ConstBSMP.V_COUNTER_SET_SLOWREF,
        ConstBSMP.V_COUNTER_SYNC_PULSE,
        ConstBSMP.V_SIGGEN_ENABLE,
        ConstBSMP.V_SIGGEN_TYPE,
        ConstBSMP.V_SIGGEN_NUM_CYCLES,
        ConstBSMP.V_SIGGEN_N,
        ConstBSMP.V_SIGGEN_FREQ,
        ConstBSMP.V_SIGGEN_AMPLITUDE,
        ConstBSMP.V_SIGGEN_OFFSET,
        ConstBSMP.V_SIGGEN_AUX_PARAM,
        # --- FAP variables ---
        ConstBSMP.V_PS_SOFT_INTERLOCKS,
        ConstBSMP.V_PS_HARD_INTERLOCKS,
        ConstBSMP.V_I_LOAD1,
        ConstBSMP.V_I_LOAD2,
        ConstBSMP.V_V_DCLINK,
        ConstBSMP.V_I_IGBT_1,
        ConstBSMP.V_I_IGBT_2,
        ConstBSMP.V_DUTY_CYCLE_1,
        ConstBSMP.V_DUTY_CYCLE_1,
        ConstBSMP.V_DUTY_DIFF,)
    groups[_PRUCParms.MIRROR] = groups[_PRUCParms.SYNCOFF]


class UDC:
    """UDC."""

    def __init__(self, pru, udcmodel, device_ids):
        """Init."""
        self._pru = pru
        self._device_ids = device_ids
        self._udcmodel = udcmodel
        # self._udcmodel = self._get_udcmodel(udcmodel)
        self._bsmp = self._create_bsmp_connectors()

    # def _get_udcmodel(self, udcmodel):
    #     if udcmodel not in udcmodels:
    #         raise ValueError('{}'.format(udcmodel))
    #     return udcmodel

    def _create_bsmp_connectors(self):
        bsmp = dict()
        # d = udcmodels[self._udcmodel]
        model = ModelFactory.get(self._udcmodel)
        entities, bsmpsim_class = model.entities, model.simulation_class
        for id in self._device_ids:
            if self._pru.simulated:
                bsmp[id] = bsmpsim_class(self._pru)
            else:
                bsmp[id] = _BSMP(self._pru, id, entities)
        return bsmp

    def __getitem__(self, index):
        """Return BSMP."""
        return self._bsmp[index]
