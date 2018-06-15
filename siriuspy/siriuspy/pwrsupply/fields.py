"""Define fields that map episc fields to bsmp entity ids.

These classes implement a common interface that exposes the `read` method.
"""
import re as _re

from siriuspy.pwrsupply import bsmp as _bsmp
from PRUserial485 import ConstSyncMode as _SYNC_MODE
from siriuspy.pwrsupply.status import PSCStatus as _PSCStatus


# class VariableFactory:
#     """Create a variable object."""
#
#     @staticmethod
#     def get(ps_model, device_id, epics_field, pru_controller):
#         """Factory."""
#         # Common variables
#         _c = _bsmp.ConstBSMP
#         if epics_field == 'PwrState-Sts':
#             return PwrState(
#                 Variable(pru_controller, device_id, _c.V_PS_STATUS))
#         elif epics_field == 'OpMode-Sts':
#             return OpMode(Variable(pru_controller, device_id, _c.V_PS_STATUS))
#         elif epics_field == 'CtrlMode-Mon':
#             return CtrlMode(
#                 Variable(pru_controller, device_id, _c.V_PS_STATUS))
#         elif epics_field == 'OpenLoop-Mon':
#             return OpenLoop(
#                 Variable(pru_controller, device_id, _c.V_PS_STATUS))
#         elif epics_field == 'Current-RB':
#             return Variable(pru_controller, device_id, _c.V_PS_SETPOINT)
#         elif epics_field == 'CurrentRef-Mon':
#             return Variable(pru_controller, device_id, _c.V_PS_REFERENCE)
#         elif epics_field == 'Version-Cte':
#             return Version(
#                 Variable(pru_controller, device_id, _c.V_FIRMWARE_VERSION))
#         elif epics_field == 'CycleEnbl-Mon':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_ENABLE)
#         elif epics_field == 'CycleType-Sts':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_TYPE)
#         elif epics_field == 'CycleNrCycles-RB':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_NUM_CYCLES)
#         elif epics_field == 'CycleIndex-Mon':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_N)
#         elif epics_field == 'CycleFreq-RB':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_FREQ)
#         elif epics_field == 'CycleAmpl-RB':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_AMPLITUDE)
#         elif epics_field == 'CycleOffset-RB':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_OFFSET)
#         elif epics_field == 'CycleAuxParam-RB':
#             return Variable(pru_controller, device_id, _c.V_SIGGEN_AUX_PARAM)
#         # Specific variables
#         if ps_model == 'FBP':
#             _c = _bsmp.ConstFBP
#             if epics_field == 'IntlkSoft-Mon':
#                 return Variable(
#                     pru_controller, device_id, _c.V_PS_SOFT_INTERLOCKS)
#             elif epics_field == 'IntlkHard-Mon':
#                 return Variable(
#                     pru_controller, device_id, _c.V_PS_HARD_INTERLOCKS)
#             elif epics_field == 'Current-Mon':
#                 return Variable(pru_controller, device_id, _c.V_I_LOAD)
#         elif ps_model == 'FAC':
#             _c = _bsmp.ConstFAC
#             if epics_field == 'IntlkSoft-Mon':
#                 return Variable(
#                     pru_controller, device_id, _c.V_PS_SOFT_INTERLOCKS)
#             elif epics_field == 'IntlkHard-Mon':
#                 return Variable(
#                     pru_controller, device_id, _c.V_PS_HARD_INTERLOCKS)
#             elif epics_field == 'Current-Mon':
#                 return Variable(pru_controller, device_id, _c.V_I_LOAD)
#             elif epics_field == 'Current2-Mon':
#                 # TODO constant for other FAC and other PS models
#                 return Variable(pru_controller, device_id, 28)
#         elif ps_model == 'FBP_DCLINK':
#             _c = _bsmp.ConstFBP_DCLINK
#             if epics_field == 'ModulesStatus-Mon':
#                 return Variable(pru_controller, device_id, _c.V_DIGITAL_INPUTS)
#             elif epics_field == 'Voltage-Mon':
#                 return Variable(pru_controller, device_id, _c.V_V_OUT)
#             elif epics_field == 'Voltage1-Mon':
#                 return Variable(pru_controller, device_id, _c.V_V_OUT_1)
#             elif epics_field == 'Voltage2-Mon':
#                 return Variable(pru_controller, device_id, _c.V_V_OUT_2)
#             elif epics_field == 'Voltage3-Mon':
#                 return Variable(pru_controller, device_id, _c.V_V_OUT_3)
#             elif epics_field == 'DigPotTap-RB':
#                 return Variable(pru_controller, device_id, _c.V_DIG_POT_TAP)
#
#         # PRU related variables
#         if epics_field == 'WfmData-RB':
#             return PRUCurve(pru_controller, device_id)
#         elif epics_field == 'WfmIndex-Mon':
#                 return Constant(0)
#         elif epics_field == 'PRUSyncMode-Mon':
#             return PRUSyncMode(pru_controller)
#         elif epics_field == 'PRUBlockIndex-Mon':
#             return PRUProperty(pru_controller, 'pru_curve_block')
#         elif epics_field == 'PRUSyncPulseCount-Mon':
#             return PRUProperty(pru_controller, 'pru_sync_pulse_count')
#         elif epics_field == 'PRUCtrlQueueSize-Mon':
#             return PRUProperty(pru_controller, 'queue_length')
#
#         raise ValueError('{} not defined'.format(epics_field))


class VariableFactory:
    """Create a variable object."""

    _vars_common = {
        'CycleEnbl-Mon':  _bsmp.ConstBSMP.V_SIGGEN_ENABLE,
        'CycleType-Sts':  _bsmp.ConstBSMP.V_SIGGEN_TYPE,
        'CycleNrCycles-RB':  _bsmp.ConstBSMP.V_SIGGEN_NUM_CYCLES,
        'CycleIndex-Mon':  _bsmp.ConstBSMP.V_SIGGEN_N,
        'CycleFreq-RB':  _bsmp.ConstBSMP.V_SIGGEN_FREQ,
        'CycleAmpl-RB':  _bsmp.ConstBSMP.V_SIGGEN_AMPLITUDE,
        'CycleOffset-RB':  _bsmp.ConstBSMP.V_SIGGEN_OFFSET,
        'CycleAuxParam-RB':  _bsmp.ConstBSMP.V_SIGGEN_AUX_PARAM,
    }

    _vars_FBP = {
        'IntlkSoft-Mon':  _bsmp.ConstFBP.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon':  _bsmp.ConstFBP.V_PS_HARD_INTERLOCKS,
        'Current-RB':  _bsmp.ConstFBP.V_PS_SETPOINT,
        'CurrentRef-Mon':  _bsmp.ConstFBP.V_PS_REFERENCE,
        'Current-Mon':  _bsmp.ConstFBP.V_I_LOAD,
    }

    _vars_FBP_DCLink = {
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

    _vars_FAC = {
        'IntlkSoft-Mon': _bsmp.ConstFAC_DCDC.V_PS_SOFT_INTERLOCKS,
        'IntlkHard-Mon': _bsmp.ConstFAC_DCDC.V_PS_HARD_INTERLOCKS,
        'Current-RB': _bsmp.ConstFAC_DCDC.V_PS_SETPOINT,
        'CurrentRef-Mon': _bsmp.ConstFAC_DCDC.V_PS_REFERENCE,
        'Current-Mon': _bsmp.ConstFAC_DCDC.V_I_LOAD1,
        'Current2-Mon': _bsmp.ConstFAC_DCDC.V_I_LOAD2,
    }

    @staticmethod
    def get(psmodel, device_id, epics_field, pru_controller):
        """Factory."""
        # ---  common variables
        v = VariableFactory._get_common(device_id, epics_field, pru_controller)
        if v is not None:
            return v
        if psmodel == 'FBP':
            v = VariableFactory._get_FBP(device_id, epics_field,
                                         pru_controller)
        elif psmodel == 'FBP_DCLink':
            v = VariableFactory._get_FBP_DCLink(device_id, epics_field,
                                                pru_controller)
        elif psmodel in ('FAC_DCDC'):
            v = VariableFactory._get_FAC(device_id, epics_field,
                                         pru_controller)
        else:
            raise NotImplementedError('Fields not implemented for ' + psmodel)
        if v is not None:
            return v
        else:
            raise ValueError('{} not defined'.format(epics_field))

    @staticmethod
    def _get_common(device_id, epics_field, pru_controller):
        _c = _bsmp.ConstBSMP
        if epics_field in VariableFactory._vars_common:
            var_id = VariableFactory._vars_common[epics_field]
            return Variable(pru_controller, device_id, var_id)
        elif epics_field == 'PwrState-Sts':
            return PwrState(
                Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'OpMode-Sts':
            return OpMode(Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'CtrlMode-Mon':
            return CtrlMode(
                Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'CtrlLoop-Sts':
            return CtrlLoop(
                Variable(pru_controller, device_id, _c.V_PS_STATUS))
        elif epics_field == 'Version-Cte':
            return Version(
                Variable(pru_controller, device_id, _c.V_FIRMWARE_VERSION))
        # PRU related variables
        elif epics_field == 'WfmData-RB':
            return PRUCurve(pru_controller, device_id)
        elif epics_field == 'WfmIndex-Mon':
                return Constant(0)
        elif epics_field == 'PRUSyncMode-Mon':
            return PRUSyncMode(pru_controller)
        elif epics_field == 'PRUBlockIndex-Mon':
            return PRUProperty(pru_controller, 'pru_curve_block')
        elif epics_field == 'PRUSyncPulseCount-Mon':
            return PRUProperty(pru_controller, 'pru_sync_pulse_count')
        elif epics_field == 'PRUCtrlQueueSize-Mon':
            return PRUProperty(pru_controller, 'queue_length')
        return None

    @staticmethod
    def _get_FBP(device_id, epics_field, pru_controller):
        if epics_field in VariableFactory._vars_FBP:
            var_id = VariableFactory._vars_FBP[epics_field]
            return Variable(pru_controller, device_id, var_id)
        return None

    @staticmethod
    def _get_FBP_DCLink(device_id, epics_field, pru_controller):
        if epics_field in VariableFactory._vars_FBP_DCLink:
            var_id = VariableFactory._vars_FBP_DCLink[epics_field]
            return Variable(pru_controller, device_id, var_id)
        return None

    @staticmethod
    def _get_FAC(device_id, epics_field, pru_controller):
        if epics_field in VariableFactory._vars_FAC:
            var_id = VariableFactory._vars_FAC[epics_field]
            return Variable(pru_controller, device_id, var_id)
        return None


class Variable:
    """Readable variable."""

    def __init__(self, pru_controller, device_id, bsmp_id):
        """Init properties."""
        self.pru_controller = pru_controller
        self.device_id = device_id
        self.bsmp_id = bsmp_id

    def read(self):
        """Read variable from pru controller."""
        return self.pru_controller.read_variables(self.device_id, self.bsmp_id)


class PRUCurve:
    """PRU Curve read."""

    def __init__(self, pru_controller, device_id):
        """Init properties."""
        self.pru_controller = pru_controller
        self.device_id = device_id

    def read(self):
        """Read curve."""
        return self.pru_controller.pru_curve_read(self.device_id)


class PRUProperty:
    """Read a PRU property."""

    def __init__(self, pru_controller, property):
        """Get pru controller and property name."""
        self.pru_controller = pru_controller
        self.property = property

    def read(self):
        """Read pru property."""
        return getattr(self.pru_controller, self.property)


class PRUSyncMode:
    """Return sync mode."""

    _sync_mode = {
        _SYNC_MODE.BRDCST: 1,
        _SYNC_MODE.RMPEND: 2,
        _SYNC_MODE.MIGEND: 3}

    def __init__(self, pru_controller):
        """Init."""
        self.sync_status = PRUProperty(pru_controller, 'pru_sync_status')
        self.sync_mode = PRUProperty(pru_controller, 'pru_sync_mode')

    def read(self):
        """Read."""
        if not self.sync_status.read():
            return 0
        else:
            return PRUSyncMode._sync_mode[self.sync_mode.read()]


class PwrState:
    """Variable decorator."""

    def __init__(self, variable):
        """Set variable."""
        self.variable = variable
        self.psc_status = _PSCStatus()

    def read(self):
        """Decorate read."""
        value = self.variable.read()
        if value is None:
            return value
        self.psc_status.ps_status = value
        return self.psc_status.ioc_pwrstate


class OpMode:
    """Variable decorator."""

    def __init__(self, variable):
        """Set variable."""
        self.variable = variable
        self.psc_status = _PSCStatus()

    def read(self):
        """Decorate read."""
        value = self.variable.read()
        if value is None:
            return value
        self.psc_status.ps_status = value
        return self.psc_status.ioc_opmode


class CtrlMode:
    """Variable decorator."""

    def __init__(self, variable):
        """Set variable."""
        self.variable = variable
        self.psc_status = _PSCStatus()

    def read(self):
        """Decorate read."""
        value = self.variable.read()
        if value is None:
            return value
        self.psc_status.ps_status = value
        return self.psc_status.interface


class CtrlLoop:
    """Variable decorator."""

    def __init__(self, variable):
        """Set variable."""
        self.variable = variable
        self.psc_status = _PSCStatus()

    def read(self):
        """Decorate read."""
        value = self.variable.read()
        if value is None:
            return value
        self.psc_status.ps_status = value
        return self.psc_status.open_loop


class Version:
    """Version variable."""

    def __init__(self, variable):
        """Set variable."""
        self.variable = variable

    def read(self):
        """Decorate read."""
        value = self.variable.read()
        version = ''.join([c.decode() for c in value])
        try:
            value, _ = version.split('\x00', 0)
        except ValueError:
            value = version
        return value


class Constant:
    """Constant."""

    _constant_regexp = _re.compile('^.*-Cte$')

    def __init__(self, value):
        """Constant value."""
        self.value = value

    def read(self):
        """Return value."""
        return self.value

    @staticmethod
    def match(field):
        """Check if field is a constant."""
        return Constant._constant_regexp.match(field)


class Setpoint:
    """Setpoint."""

    _setpoint_regexp = _re.compile('^.*-(SP|Sel|Cmd)$')

    def __init__(self, epics_field, epics_database):
        """Init."""
        self.field = epics_field
        self.value = epics_database['value']
        self.database = epics_database
        if '-Cmd' in epics_field:
            self.is_cmd = True
        else:
            self.is_cmd = False
        self.type = epics_database['type']
        if 'count' in epics_database:
            self.count = epics_database['count']
        else:
            self.count = None
        if self.type == 'enum' and 'enums' in epics_database:
            self.enums = epics_database['enums']
        else:
            self.enums = None
        self.value = epics_database['value']
        if self.type in ('int', 'float'):
            if 'hihi' in epics_database:
                self.high = epics_database['hihi']
            else:
                self.high = None
            if 'lolo' in epics_database:
                self.low = epics_database['lolo']
            else:
                self.low = None
        else:
            self.low = None
            self.high = None

    def apply(self, value):
        """Apply setpoint value."""
        if self._check(value):
            if self.is_cmd:
                self.value += 1
            else:
                self.value = value
            return True
        return False

    def read(self):
        """Read setpoint value."""
        return self.value

    def _check(self, value):
        """Check value."""
        if self.is_cmd:
            if value > 0:
                return True
        elif self.type in ('int', 'float'):
            if self.low is None and self.high is None:
                return True
            if value is not None and (value > self.low and value < self.high):
                return True
        elif self.type == 'enum':
            if value in tuple(range(len(self.enums))):
                return True
        return False

    @staticmethod
    def match(field):
        """Check if field is a setpoint."""
        return Setpoint._setpoint_regexp.match(field)


class Setpoints:
    """Setpoints."""

    def __init__(self, setpoints):
        self._setpoints = setpoints

    def apply(self, value):
        for setpoint in self._setpoints:
            if not setpoint.apply(value):
                return False

        return True
