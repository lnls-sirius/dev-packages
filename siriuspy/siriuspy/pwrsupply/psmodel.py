"""Power Supply Model classes."""

from . import bsmp as _psbsmp
from . import psbsmpsim as _psbsmpsim
from . import fields as _fields
from . import functions as _functions
from . import controller as _controller


class _PSModel:
    """Abstract power supply model."""

    _c = _psbsmp.ConstPSBSMP
    _e2v = {
        # Epics to direct BSMP variable
        'CycleEnbl-Mon': _c.V_SIGGEN_ENABLE,
        'CycleType-Sts': _c.V_SIGGEN_TYPE,
        'CycleNrCycles-RB': _c.V_SIGGEN_NUM_CYCLES,
        'CycleIndex-Mon': _c.V_SIGGEN_N,
        'CycleFreq-RB': _c.V_SIGGEN_FREQ,
        'CycleAmpl-RB': _c.V_SIGGEN_AMPLITUDE,
        'CycleOffset-RB': _c.V_SIGGEN_OFFSET,
        'CycleAuxParam-RB': _c.V_SIGGEN_AUX_PARAM}
    _e2f = {
        # Epics to BSMP variable with pre-processing
        'PwrState-Sts': (_fields.PwrState, _c.V_PS_STATUS),
        'OpMode-Sts': (_fields.OpMode, _c.V_PS_STATUS),
        'CtrlMode-Mon': (_fields.CtrlMode, _c.V_PS_STATUS),
        'CtrlLoop-Sts': (_fields.CtrlLoop, _c.V_PS_STATUS),
        'Version-Cte': (_fields.Version, _c.V_FIRMWARE_VERSION)}
    _e2c = {
        # Epics to PRUCrontroller property
        'PRUCtrlQueueSize-Mon': 'queue_length'}

    _variables = dict()  # this will be filled in derived classes

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
            var_id = self._e2v[epics_field]
            return _fields.Variable(pru_controller, device_id, var_id)
        elif epics_field in self._e2f:
            field, var_id = self._e2f[epics_field]
            return field(_fields.Variable(pru_controller, device_id, var_id))
        elif epics_field in self._e2c:
            attr = self._e2c[epics_field]
            return _fields.PRUProperty(pru_controller, attr)
        elif epics_field == 'TimestampUpdate-Mon':
            return _fields.TimestampUpdate(pru_controller, device_id)
        elif epics_field == 'Wfm-RB':
            return _fields.WfmRBCurve(pru_controller, device_id)
        elif epics_field == 'WfmRef-Mon':
            return _fields.WfmRefMonCurve(pru_controller, device_id)
        elif epics_field == 'Wfm-Mon':
            return _fields.WfmMonCurve(pru_controller, device_id)
        elif epics_field == 'WfmIndex-Mon':
            return _fields.WfmIndexCurve(pru_controller, device_id)
        elif epics_field == 'WfmUpdateAuto-Sts':
            return _fields.WfmUpdateAutoSts(pru_controller, device_id)
        return None

    def _specific_fields(self, device_id, epics_field, pru_controller):
        # Specific fields
        if epics_field in self._variables:
            var_id = self._variables[epics_field]
            return _fields.Variable(pru_controller, device_id, var_id)
        return None


# Standard PS that supply magnets
class PSModelFBP(_PSModel):
    """FBP model."""

    _variables = {
        'IntlkSoft-Mon':  _psbsmp.ConstFBP.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon':  _psbsmp.ConstFBP.V_PS_HARD_INTERLOCKS,
        'WfmSyncPulseCount-Mon': _psbsmp.ConstFBP.V_COUNTER_SYNC_PULSE,
        'Current-RB':  _psbsmp.ConstFBP.V_PS_SETPOINT,
        'CurrentRef-Mon':  _psbsmp.ConstFBP.V_PS_REFERENCE,
        'Current-Mon':  _psbsmp.ConstFBP.V_I_LOAD,
        'SwitchesTemperature-Mon': _psbsmp.ConstFBP.V_TEMP_SWITCHES,
        'PWMDutyCycle-Mon': _psbsmp.ConstFBP.V_DUTY_CYCLE,
    }

    @property
    def name(self):
        """Model name."""
        return 'FBP'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFBP

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFBP()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FBP

    def function(self, device_ids, epics_field, pru_controller, setpoints):
        """Return function."""
        _c = _psbsmp.ConstFBP
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
        elif epics_field == 'SyncPulse-Cmd':
            return _functions.Command(
                device_ids, pru_controller, _c.F_SYNC_PULSE, setpoints)
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
        elif epics_field == 'Wfm-SP':
            return _functions.WfmSP(
                device_ids, pru_controller, setpoints)
        elif epics_field == 'WfmUpdate-Cmd':
            return _functions.WfmUpdate(
                device_ids, pru_controller, setpoints)
        elif epics_field == 'WfmUpdateAuto-Sel':
            return _functions.WfmUpdateAutoSel(
                device_ids, pru_controller, setpoints)
        elif epics_field == 'WfmMonAcq-Sel':
            return _functions.WfmMonAcq(device_ids, pru_controller,
                                        setpoints)
        else:
            return _functions.BSMPFunctionNull()

    def controller(self, readers, writers, connections,
                   pru_controller, devices):
        """Return controller."""
        return _controller.StandardPSController(
            readers, writers, connections, pru_controller, devices)


class PSModelFBP_FOFB(PSModelFBP):
    """FBP_FOFB power supply model."""

    @property
    def name(self):
        """Model name."""
        return 'FBP_FOFB'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFBP

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFBP()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FBP


class PSModelFAC_DCDC(PSModelFBP):
    """FAC power supply model."""

    _variables = {
        'IntlkSoft-Mon': _psbsmp.ConstFAC_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFAC_DCDC.V_PS_HARD_INTERLOCKS,
        'WfmSyncPulseCount-Mon': _psbsmp.ConstFBP.V_COUNTER_SYNC_PULSE,
        'Current-RB': _psbsmp.ConstFAC_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _psbsmp.ConstFAC_DCDC.V_PS_REFERENCE,
        'Current-Mon': _psbsmp.ConstFAC_DCDC.V_I_LOAD_MEAN,
        'Current1-Mon': _psbsmp.ConstFAC_DCDC.V_I_LOAD1,
        'Current2-Mon': _psbsmp.ConstFAC_DCDC.V_I_LOAD2,
        'LoadVoltage-Mon': _psbsmp.ConstFAC_DCDC.V_V_LOAD,
        'InductorsTemperature-Mon': _psbsmp.ConstFAC_DCDC.V_TEMP_INDUCTORS,
        'IGBTSTemperature-Mon': _psbsmp.ConstFAC_DCDC.V_TEMP_IGBTS,
        'PWMDutyCycle-Mon': _psbsmp.ConstFAC_DCDC.V_DUTY_CYCLE,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_DCDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAC_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAC_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAC_DCDC


class PSModelFAC_2S_DCDC(PSModelFBP):
    """FAC_2S_DCDC power supply model."""

    _variables = {
        'Current-RB': _psbsmp.ConstFAC_2S_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _psbsmp.ConstFAC_2S_DCDC.V_PS_REFERENCE,
        'IntlkSoft-Mon': _psbsmp.ConstFAC_2S_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFAC_2S_DCDC.V_PS_HARD_INTERLOCKS,
        'WfmSyncPulseCount-Mon': _psbsmp.ConstFBP.V_COUNTER_SYNC_PULSE,
        'Current-Mon': _psbsmp.ConstFAC_2S_DCDC.V_I_LOAD_MEAN,
        'Current1-Mon': _psbsmp.ConstFAC_2S_DCDC.V_I_LOAD1,
        'Current2-Mon': _psbsmp.ConstFAC_2S_DCDC.V_I_LOAD2,
        'LoadVoltage-Mon': _psbsmp.ConstFAC_2S_DCDC.V_V_LOAD,
        'Module1Voltage-Mon': _psbsmp.ConstFAC_2S_DCDC.V_V_OUT_1,
        'Module2Voltage-Mon': _psbsmp.ConstFAC_2S_DCDC.V_V_OUT_2,
        'CapacitorBank1Voltage-Mon':
            _psbsmp.ConstFAC_2S_DCDC.V_V_CAPBANK_1,
        'CapacitorBank2Voltage-Mon':
            _psbsmp.ConstFAC_2S_DCDC.V_V_CAPBANK_2,
        'PWMDutyCycle1-Mon': _psbsmp.ConstFAC_2S_DCDC.V_DUTY_CYCLE_1,
        'PWMDutyCycle2-Mon': _psbsmp.ConstFAC_2S_DCDC.V_DUTY_CYCLE_2,
        'PWMDutyDiff-Mon': _psbsmp.ConstFAC_2S_DCDC.V_DUTY_DIFF,
        'IIB1InductorsTemperature-Mon':
            _psbsmp.ConstFAC_2S_DCDC.V_TEMP_INDUCTOR_IIB_1,
        'IIB1HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2S_DCDC.V_TEMP_HEATSINK_IIB_1,
        'IIB2InductorsTemperature-Mon':
            _psbsmp.ConstFAC_2S_DCDC.V_TEMP_INDUCTOR_IIB_2,
        'IIB2HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2S_DCDC.V_TEMP_HEATSINK_IIB_2,
        'IntlkIIB1-Mon': _psbsmp.ConstFAC_2S_DCDC.V_IIB_INTERLOCKS_1,
        'IntlkIIB2-Mon': _psbsmp.ConstFAC_2S_DCDC.V_IIB_INTERLOCKS_2,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2S_DCDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAC_2S_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAC_2S_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAC_2S_DCDC


class PSModelFAC_2P4S_DCDC(PSModelFAC_DCDC):
    """FAC_2P4S_DCDC power supply model (BO Dipoles)."""

    _variables = {
        'Current-RB': _psbsmp.ConstFAC_2P4S_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_PS_REFERENCE,
        'IntlkSoft-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_PS_HARD_INTERLOCKS,
        'WfmSyncPulseCount-Mon': _psbsmp.ConstFBP.V_COUNTER_SYNC_PULSE,
        'Current-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_I_LOAD_MEAN,
        'Current1-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_I_LOAD1,
        'Current2-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_I_LOAD2,
        'LoadVoltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_LOAD,
        'CapacitorBank1Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_1,
        'CapacitorBank2Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_2,
        'CapacitorBank3Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_3,
        'CapacitorBank4Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_4,
        'CapacitorBank5Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_5,
        'CapacitorBank6Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_6,
        'CapacitorBank7Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_7,
        'CapacitorBank8Voltage-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_V_CAPBANK_8,
        'Module1Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_1,
        'Module2Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_2,
        'Module3Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_3,
        'Module4Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_4,
        'Module5Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_5,
        'Module6Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_6,
        'Module7Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_7,
        'Module8Voltage-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_V_OUT_8,
        'PWMDutyCycle1-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_1,
        'PWMDutyCycle2-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_2,
        'PWMDutyCycle3-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_3,
        'PWMDutyCycle4-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_4,
        'PWMDutyCycle5-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_5,
        'PWMDutyCycle6-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_6,
        'PWMDutyCycle7-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_7,
        'PWMDutyCycle8-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_DUTY_CYCLE_8,
        'Arm1Current-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_I_ARM_1,
        'Arm2Current-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_I_ARM_2,
        'IIB1InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_1,
        'IIB1HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_1,
        'IIB2InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_2,
        'IIB2HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_2,
        'IIB3InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_3,
        'IIB3HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_3,
        'IIB4InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_4,
        'IIB4HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_4,
        'IIB5InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_5,
        'IIB5HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_5,
        'IIB6InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_6,
        'IIB6HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_6,
        'IIB7InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_7,
        'IIB7HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_7,
        'IIB8InductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_INDUCTOR_IIB_8,
        'IIB8HeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_DCDC.V_TEMP_HEATSINK_IIB_8,
        'IntlkIIB1-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_1,
        'IntlkIIB2-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_2,
        'IntlkIIB3-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_3,
        'IntlkIIB4-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_4,
        'IntlkIIB5-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_5,
        'IntlkIIB6-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_6,
        'IntlkIIB7-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_7,
        'IntlkIIB8-Mon': _psbsmp.ConstFAC_2P4S_DCDC.V_IIB_INTERLOCKS_8,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2P4S_DCDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAC_2P4S_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAC_2P4S_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAC_2P4S_DCDC


class PSModelFAP(PSModelFBP):
    """FAP power supply model."""

    _variables = {
        'IntlkSoft-Mon': _psbsmp.ConstFAP.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFAP.V_PS_HARD_INTERLOCKS,
        'WfmSyncPulseCount-Mon': _psbsmp.ConstFBP.V_COUNTER_SYNC_PULSE,
        'IntlkIIB-Mon': _psbsmp.ConstFAP.V_IIB_INTERLOCKS,
        'Current-RB': _psbsmp.ConstFAP.V_PS_SETPOINT,
        'CurrentRef-Mon': _psbsmp.ConstFAP.V_PS_REFERENCE,
        'Current-Mon': _psbsmp.ConstFAP.V_I_LOAD_MEAN,
        'Current1-Mon': _psbsmp.ConstFAP.V_I_LOAD1,
        'Current2-Mon': _psbsmp.ConstFAP.V_I_LOAD2,
        'IIBLeakCurrent-Mon': _psbsmp.ConstFAP.V_I_LEAKAGE_IIB,
        'IIBInductorTemperature-Mon': _psbsmp.ConstFAP.V_TEMP_INDUCTOR_IIB,
        'IIBHeatSinkTemperature-Mon': _psbsmp.ConstFAP.V_TEMP_HEATSINK_IIB,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAP'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAP

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAP()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAP


class PSModelFAP_4P(PSModelFBP):
    """FAP_4P power supply model."""

    _variables = {
        'IntlkSoft-Mon': _psbsmp.ConstFAP_4P.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFAP_4P.V_PS_HARD_INTERLOCKS,
        'WfmSyncPulseCount-Mon': _psbsmp.ConstFBP.V_COUNTER_SYNC_PULSE,
        'Intlk1IIB-Mon': _psbsmp.ConstFAP_4P.V_IIB_INTERLOCKS_1,
        'Intlk2IIB-Mon': _psbsmp.ConstFAP_4P.V_IIB_INTERLOCKS_2,
        'Intlk3IIB-Mon': _psbsmp.ConstFAP_4P.V_IIB_INTERLOCKS_3,
        'Intlk4IIB-Mon': _psbsmp.ConstFAP_4P.V_IIB_INTERLOCKS_4,
        'Current-RB': _psbsmp.ConstFAP_4P.V_PS_SETPOINT,
        'CurrentRef-Mon': _psbsmp.ConstFAP_4P.V_PS_REFERENCE,
        'Current-Mon': _psbsmp.ConstFAP_4P.V_I_LOAD_MEAN,
        'Current1-Mon': _psbsmp.ConstFAP_4P.V_I_LOAD1,
        'Current2-Mon': _psbsmp.ConstFAP_4P.V_I_LOAD2,
        'DCLink1Voltage-Mon': _psbsmp.ConstFAP_4P.V_V_DCLINK_1,
        'DCLink2Voltage-Mon': _psbsmp.ConstFAP_4P.V_V_DCLINK_1,
        'DCLink3Voltage-Mon': _psbsmp.ConstFAP_4P.V_V_DCLINK_3,
        'DCLink4Voltage-Mon': _psbsmp.ConstFAP_4P.V_V_DCLINK_4,
        'Mod1Current-Mon': _psbsmp.ConstFAP_4P.V_I_MOD_1,
        'Mod2Current-Mon': _psbsmp.ConstFAP_4P.V_I_MOD_2,
        'Mod3Current-Mon': _psbsmp.ConstFAP_4P.V_I_MOD_3,
        'Mod4Current-Mon': _psbsmp.ConstFAP_4P.V_I_MOD_4,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAP_4P'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAP_4P

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAP_4P()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAP_4P


class PSModelFAP_2P2S(PSModelFBP):
    """FAP_2P2S power supply model."""

    _variables = {
        'IntlkSoft-Mon':  _psbsmp.ConstFAP_2P2S.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon':  _psbsmp.ConstFAP_2P2S.V_PS_HARD_INTERLOCKS,
        'WfmSyncPulseCount-Mon': _psbsmp.ConstFBP.V_COUNTER_SYNC_PULSE,
        'Current-RB':  _psbsmp.ConstFAP_2P2S.V_PS_SETPOINT,
        'CurrentRef-Mon':  _psbsmp.ConstFAP_2P2S.V_PS_REFERENCE,
        'Current-Mon':  _psbsmp.ConstFAP_2P2S.V_I_LOAD_MEAN,
        'Current1-Mon': _psbsmp.ConstFAP_2P2S.V_I_LOAD1,
        'Current2-Mon': _psbsmp.ConstFAP_2P2S.V_I_LOAD2,
        'IIB1InductorTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_1,
        'IIB1HeatSinkTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_1,
        'IIB2InductorTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_2,
        'IIB2HeatSinkTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_2,
        'IIB3InductorTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_3,
        'IIB3HeatSinkTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_3,
        'IIB4InductorTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_INDUCTOR_IIB_4,
        'IIB4HeatSinkTemperature-Mon': _psbsmp.ConstFAP_2P2S.V_TEMP_HEATSINK_IIB_4,
        'Intlk1IIB-Mon': _psbsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_1,
        'Intlk2IIB-Mon': _psbsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_2,
        'Intlk3IIB-Mon': _psbsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_3,
        'Intlk4IIB-Mon': _psbsmp.ConstFAP_2P2S.V_IIB_INTERLOCKS_4,
        'Mod1Current-Mon': _psbsmp.ConstFAP_2P2S.V_I_MOD_1,
        'Mod2Current-Mon': _psbsmp.ConstFAP_2P2S.V_I_MOD_2,
        'Mod3Current-Mon': _psbsmp.ConstFAP_2P2S.V_I_MOD_3,
        'Mod4Current-Mon': _psbsmp.ConstFAP_2P2S.V_I_MOD_4,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAP_2P2S'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAP_2P2S

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAP_2P2S()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAP_2P2S


class PSModelCommercial(PSModelFAC_DCDC):
    """Commercial power supply model."""

    @property
    def name(self):
        """Model name."""
        return 'Commercial'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAC_DCDC

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAC_DCDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAC_DCDC


# --- ACDC ---


class PSModelFBP_DCLink(_PSModel):
    """FBP_DCLink model."""

    _variables = {
        'IntlkSoft-Mon': _psbsmp.ConstFBP_DCLink.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFBP_DCLink.V_PS_HARD_INTERLOCKS,
        'ModulesStatus-Mon': _psbsmp.ConstFBP_DCLink.V_MODULES_STATUS,
        'Voltage-RB': _psbsmp.ConstFBP_DCLink.V_PS_SETPOINT,
        'VoltageRef-Mon': _psbsmp.ConstFBP_DCLink.V_PS_REFERENCE,
        'Voltage-Mon': _psbsmp.ConstFBP_DCLink.V_V_OUT,
        'Voltage1-Mon': _psbsmp.ConstFBP_DCLink.V_V_OUT_1,
        'Voltage2-Mon': _psbsmp.ConstFBP_DCLink.V_V_OUT_2,
        'Voltage3-Mon': _psbsmp.ConstFBP_DCLink.V_V_OUT_3,
        'VoltageDig-Mon': _psbsmp.ConstFBP_DCLink.V_DIG_POT_TAP,
    }

    @property
    def name(self):
        """Model name."""
        return 'FBP_DCLink'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFBP_DCLink

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFBP_DCLink()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FBP_DCLink

    def function(self, device_ids, epics_field, pru_controller, setpoints):
        """Return function."""
        _c = _psbsmp.ConstFBP_DCLink
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


class PSModelFAC_2S_ACDC(_PSModel):
    """FAC_2S_ACDC model."""

    _variables = {
        'IntlkSoft-Mon': _psbsmp.ConstFAC_2S_ACDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFAC_2S_ACDC.V_PS_HARD_INTERLOCKS,
        'CapacitorBankVoltage-RB': _psbsmp.ConstFAC_2S_ACDC.V_PS_SETPOINT,
        'CapacitorBankVoltageRef-Mon': _psbsmp.ConstFAC_2S_ACDC.V_PS_REFERENCE,
        'CapacitorBankVoltage-Mon': _psbsmp.ConstFAC_2S_ACDC.V_V_CAPBANK,
        'RectifierVoltage-Mon': _psbsmp.ConstFAC_2S_ACDC.V_V_OUT_RECTIFIER,
        'RectifierCurrent-Mon': _psbsmp.ConstFAC_2S_ACDC.V_I_OUT_RECTIFIER,
        'HeatSinkTemperature-Mon': _psbsmp.ConstFAC_2S_ACDC.V_TEMP_HEATSINK,
        'InductorsTemperature-Mon': _psbsmp.ConstFAC_2S_ACDC.V_TEMP_INDUCTORS,
        'PWMDutyCycle-Mon': _psbsmp.ConstFAC_2S_ACDC.V_DUTY_CYCLE,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2S_ACDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAC_2S_ACDC

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAC_2S_ACDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAC_2S_ACDC

    def function(self, device_ids, epics_field, pru_controller, setpoints):
        """Return function."""
        _c = _psbsmp.ConstFAC_2S_ACDC
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


class PSModelFAC_2P4S_ACDC(PSModelFAC_2S_ACDC):
    """FAC_2P4S_ACDC model."""

    _variables = {
        'IntlkSoft-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_PS_HARD_INTERLOCKS,
        'CapacitorBankVoltage-RB': _psbsmp.ConstFAC_2P4S_ACDC.V_PS_SETPOINT,
        'CapacitorBankVoltageRef-Mon':
            _psbsmp.ConstFAC_2P4S_ACDC.V_PS_REFERENCE,
        'CapacitorBankVoltage-Mon':
            _psbsmp.ConstFAC_2P4S_ACDC.V_V_CAPACITOR_BANK,
        'RectifierVoltage-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_V_OUT_RECTIFIER,
        'RectifierCurrent-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_I_OUT_RECTIFIER,
        'HeatSinkTemperature-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_TEMP_HEATSINK,
        'InductorsTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_ACDC.V_TEMP_INDUCTORS,
        'PWMDutyCycle-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_DUTY_CYCLE,
        'IIBISInductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_ACDC.V_TEMP_INDUCTOR_IS_IIB,
        'IIBISHeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_ACDC.V_TEMP_HEATSINK_IS_IIB,
        'IIBCmdInductorTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_ACDC.V_TEMP_INDUCTOR_CMD_IIB,
        'IIBCmdHeatSinkTemperature-Mon':
            _psbsmp.ConstFAC_2P4S_ACDC.V_TEMP_HEATSINK_CMD_IIB,
        'IntlkIIBIS-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_IIB_INTERLOCKS_IS,
        'IntlkIIBCmd-Mon': _psbsmp.ConstFAC_2P4S_ACDC.V_IIB_INTERLOCKS_CMD,
    }

    @property
    def name(self):
        """Model name."""
        return 'FAC_2P4S_ACDC'

    @property
    def bsmp_constants(self):
        """Model BSMP constants."""
        return _psbsmp.ConstFAC_2P4S_ACDC

    @property
    def entities(self):
        """Model entities."""
        return _psbsmp.EntitiesFAC_2P4S_ACDC()

    @property
    def simulation_class(self):
        """Model simulation."""
        return _psbsmpsim.FAC_2P4S_ACDC


# --- Factory ---


class PSModelFactory:
    """PSModel Factory."""

    _psname_2_factory = {
        'FBP': PSModelFBP,
        'FBP_DCLink': PSModelFBP_DCLink,
        'FBP_FOFB': PSModelFBP,
        'FAC_DCDC': PSModelFAC_DCDC,
        'FAC_2S_DCDC': PSModelFAC_2S_DCDC,
        'FAC_2S_ACDC': PSModelFAC_2S_ACDC,
        'FAC_2P4S_DCDC': PSModelFAC_2P4S_DCDC,
        'FAC_2P4S_ACDC': PSModelFAC_2P4S_ACDC,
        'FAP': PSModelFAP,
        'FAP_2P2S': PSModelFAP_2P2S,
        'FAP_4P': PSModelFAP_4P,
        'Commercial': PSModelCommercial,
    }

    @staticmethod
    def create(psmodel):
        """Return PSModel object."""
        if psmodel in PSModelFactory._psname_2_factory:
            factory = PSModelFactory._psname_2_factory[psmodel]
            return factory()
        raise ValueError('PS Model "{}" not defined'.format(psmodel))
