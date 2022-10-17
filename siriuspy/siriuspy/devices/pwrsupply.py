"""Power Supply Devices."""

import numpy as _np

from .. import util as _util

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import PSSearch as _PSSearch
from ..pwrsupply.csdev import Const as _Const
from ..pwrsupply.psctrl.pscstatus import PSCStatus as _PSCStatus

from .device import Device as _Device


class _PSDev(_Device):
    """Base Power Supply Device."""

    PWRSTATE = _PSCStatus.PWRSTATE

    _default_timeout = 0.5  # [s]
    _properties_common = (
        'PwrState-Sel', 'PwrState-Sts',
    )
    _properties_linac = (
        'Current-SP', 'Current-RB', 'Current-Mon',
    )
    _properties_magps = (
        'Current-SP', 'Current-RB', 'Current-Mon', 'CurrentRef-Mon',
        'OpMode-Sel', 'OpMode-Sts',
        'WfmUpdateAuto-Sel', 'WfmUpdateAuto-Sts',
        'CycleType-Sel', 'CycleType-Sts',
        'CycleNrCycles-SP', 'CycleNrCycles-RB',
        'CycleFreq-SP', 'CycleFreq-RB',
        'CycleAmpl-SP', 'CycleAmpl-RB',
        'CycleOffset-SP', 'CycleOffset-RB',
        'CycleAuxParam-SP', 'CycleAuxParam-RB',
        'CycleEnbl-Mon',
    )
    _properties_fc = (
        'AlarmsAmp-Mon', 'OpMode-Sel', 'OpMode-Sts',
        'CurrLoopKp-RB', 'CurrLoopKp-SP', 'CurrLoopTi-RB', 'CurrLoopTi-SP',
        'CurrLoopMode-Sts', 'CurrLoopMode-Sel',
        'CurrGain-RB', 'CurrGain-SP', 'CurrOffset-RB', 'CurrOffset-SP',
        'Current-RB', 'Current-SP', 'Current-Mon', 'CurrentRef-Mon',
        'TestLimA-RB', 'TestLimA-SP', 'TestLimB-RB', 'TestLimB-SP',
        'TestWavePeriod-RB', 'TestWavePeriod-SP',
        'Voltage-RB', 'Voltage-SP', 'Voltage-Mon',
        'VoltGain-RB', 'VoltGain-SP', 'VoltOffset-RB', 'VoltOffset-SP',
        'InvRespMatRow-SP', 'InvRespMatRow-RB',
        'FOFBAccGain-SP', 'FOFBAccGain-RB',
        'FOFBAccFreeze-Sel', 'FOFBAccFreeze-Sts',
        'FOFBAccClear-Cmd',
        'FOFBAccSatMax-SP', 'FOFBAccSatMax-RB',
        'FOFBAccSatMin-SP', 'FOFBAccSatMin-RB',
    )
    _properties_pulsed = (
        'Voltage-SP', 'Voltage-RB', 'Voltage-Mon',
        'Pulse-Sel', 'Pulse-Sts')
    _properties_pulsed_sept = (
        'Intlk1-Mon', 'Intlk2-Mon', 'Intlk3-Mon', 'Intlk4-Mon',
        'Intlk5-Mon', 'Intlk6-Mon', 'Intlk7-Mon',
    )
    _properties_pulsed_kckr = _properties_pulsed_sept + ('Intlk8-Mon', )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in _PSSearch.get_psnames():
            raise NotImplementedError(devname)

        # power supply type and magnetic function
        (self._pstype, self._psmodel, self._magfunc,
         self._strength_propty, self._strength_units,
         self._is_linac, self._is_pulsed, self._is_fc,
         self._is_magps) = _PSDev.get_device_type(devname)

        # set attributes
        (self._strength_sp_propty,
         self._strength_rb_propty,
         self._strength_mon_propty,
         properties) = self._set_attributes_properties()

        # call base class constructor
        super().__init__(devname, properties=properties)

    @property
    def pstype(self):
        """Return type of magnet(s) excited by power supply device."""
        return self._pstype

    @property
    def psmodel(self):
        """Return power supply model of the device."""
        return self._psmodel

    @property
    def magfunc(self):
        """Return function of magnet excited by power supply devices."""
        return self._magfunc

    @property
    def is_linac(self):
        """Return True if device is a Linac magnet power supply."""
        return self._is_linac

    @property
    def is_pulsed(self):
        """Return True if device is a pulsed magnet power supply."""
        return self._is_pulsed

    @property
    def is_fc(self):
        """Return True if device is a Sirius fast corrector power supply"""
        return self._is_fc

    @property
    def is_magps(self):
        """Return True if device is a Sirius magnet power supply."""
        return self._is_pulsed

    @property
    def strength_property(self):
        """Return Strength name."""
        return self._strength_propty

    @property
    def strength_units(self):
        """Return Strength units."""
        return self._strength_units

    @property
    def strength(self):
        """Return Strength RB."""
        return self[self._strength_rb_propty]

    @strength.setter
    def strength(self, value):
        """Set Strength SP."""
        self[self._strength_sp_propty] = value

    @property
    def strengthref_mon(self):
        """Return Strength Ref-Mon."""
        return self[self._strength_propty + 'Ref-Mon']

    @property
    def strength_mon(self):
        """Return Strength Mon."""
        return self[self._strength_mon_propty]

    @property
    def pwrstate(self):
        """."""
        return self['PwrState-Sts']

    @pwrstate.setter
    def pwrstate(self, value):
        """."""
        self['PwrState-Sel'] = value

    def cmd_turn_on(self, timeout=_default_timeout):
        """."""
        self.pwrstate = self.PWRSTATE.On
        return self._wait('PwrState-Sts', self.PWRSTATE.On, timeout=timeout)

    def cmd_turn_off(self, timeout=_default_timeout):
        """."""
        self.pwrstate = self.PWRSTATE.Off
        return self._wait('PwrState-Sts', self.PWRSTATE.Off, timeout=timeout)

    @staticmethod
    def get_device_type(devname):
        """."""
        pstype = _PSSearch.conv_psname_2_pstype(devname)
        psmodel = _PSSearch.conv_psname_2_psmodel(devname)
        magfunc = _PSSearch.conv_psname_2_magfunc(devname)
        strength_propty = _util.get_strength_label(magfunc)
        strength_units = _util.get_strength_units(magfunc, pstype)
        is_linac = devname.sec.endswith('LI')
        is_pulsed = devname.dis == 'PU'
        is_fc = devname.dev == 'FCH' or devname.dev == 'FCV'
        is_magps = not is_linac and not is_pulsed and not is_fc
        return (pstype, psmodel, magfunc,
                strength_propty, strength_units,
                is_linac, is_pulsed, is_fc, is_magps)

    # --- private methods ---

    def _set_attributes_properties(self):

        properties = _PSDev._properties_common
        if self._is_linac:
            properties += _PSDev._properties_linac
        elif self._is_pulsed:
            properties += _PSDev._properties_pulsed
            if self._psmodel == 'FP_KCKR':
                properties += _PSDev._properties_pulsed_kckr
            else:
                properties += _PSDev._properties_pulsed_sept
        elif self._is_fc:
            properties += _PSDev._properties_fc
        else:
            properties += _PSDev._properties_magps

        # strength properties
        strength_sp_propty = self._strength_propty + '-SP'
        strength_rb_propty = self._strength_propty + '-RB'
        strength_mon_propty = self._strength_propty + '-Mon'
        properties += (
            strength_sp_propty,
            strength_rb_propty,
            strength_mon_propty,
        )
        if not self._is_linac and not self._is_pulsed:
            strengthref_mon_propty = self._strength_propty + 'Ref-Mon'
            properties += (strengthref_mon_propty, )

        ret = (
            strength_sp_propty, strength_rb_propty, strength_mon_propty,
            properties)

        return ret


class PowerSupply(_PSDev):
    """Power Supply Device."""

    OPMODE_SEL = _PSCStatus.OPMODE
    OPMODE_STS = _PSCStatus.STATES
    CYCLETYPE = _PSCStatus.CYCLETYPE
    WFMUPDATEAUTO = _Const.DsblEnbl

    class DEVICES:
        """Devices names."""

    @property
    def current(self):
        """."""
        return self['Current-RB']

    @current.setter
    def current(self, value):
        self['Current-SP'] = value

    @property
    def current_mon(self):
        """."""
        return self['Current-Mon']

    @property
    def currentref_mon(self):
        """."""
        return self['CurrentRef-Mon']

    @property
    def opmode(self):
        """."""
        return self['OpMode-Sts']

    @opmode.setter
    def opmode(self, value):
        self._enum_setter(
            'OpMode-Sel', value, self.OPMODE_SEL)

    @property
    def opmode_str(self):
        """."""
        return self.OPMODE_STS._fields[self['OpMode-Sts']]

    def wait_cycle_to_finish(self, timeout=10):
        """."""
        return self._wait('CycleEnbl-Mon', 0, timeout)

    @property
    def cycle_enabled(self):
        """."""
        return bool(self['CycleEnbl-Mon'])

    @property
    def cycle_type(self):
        """."""
        return self['CycleType-Sts']

    @cycle_type.setter
    def cycle_type(self, value):
        self._enum_setter(
            'CycleType-Sel', value, self.CYCLETYPE)

    @property
    def cycle_type_str(self):
        """."""
        return self.CYCLETYPE._fields[self['CycleType-Sts']]

    @property
    def cycle_num_cycles(self):
        """Return the number of cycles of the cycling curve."""
        return self['CycleNrCycles-RB']

    @cycle_num_cycles.setter
    def cycle_num_cycles(self, value):
        """Return the number of cycles of the cycling curve."""
        self['CycleNrCycles-SP'] = value

    @property
    def cycle_freq(self):
        """Frequency of the cycling curve [Hz]."""
        return self['CycleFreq-RB']

    @cycle_freq.setter
    def cycle_freq(self, value):
        """Frequency of the cycling curve [Hz]."""
        self['CycleFreq-SP'] = value

    @property
    def cycle_period(self):
        """Period of the cycling curve [s]."""
        freq = self['CycleFreq-RB']
        return 1 / freq if freq != 0 else float('nan')

    @cycle_period.setter
    def cycle_period(self, value):
        """Period of the cycling curve [s]."""
        if value == 0:
            raise ValueError('Cannot set zero for cycle period.')
        self['CycleFreq-SP'] = 1 / value

    @property
    def cycle_ampl(self):
        """Return the current amplitude of the cycling curve [A]."""
        return self['CycleAmpl-RB']

    @cycle_ampl.setter
    def cycle_ampl(self, value):
        """Return the current amplitude of the cycling curve [A]."""
        self['CycleAmpl-SP'] = value

    @property
    def cycle_offset(self):
        """Return the current offset of the cycling curve [A]."""
        return self['CycleOffset-RB']

    @cycle_offset.setter
    def cycle_offset(self, value):
        """Return the current offset of the cycling curve [A]."""
        self['CycleOffset-SP'] = value

    @property
    def cycle_aux_param(self):
        """Meaning of each index is presented below.

        for Sine and Square:
         - AuxParams[0] --> initial phase [°]
         - AuxParams[1] --> final phase [°]
         - AuxParams[2] --> not used
         - AuxParams[3] --> not used

        for DampedSine and DampedSquaredSine:
         - AuxParams[0] --> initial phase [°]
         - AuxParams[1] --> final phase [°]
         - AuxParams[2] --> damping time [s]
         - AuxParams[3] --> not used

        for Trapezoidal:
         - AuxParams[0] --> rampup time [s]
         - AuxParams[1] --> plateau time [s]
         - AuxParams[2] --> rampdown time [s]
         - AuxParams[3] --> not used
        """
        value = self['CycleAuxParam-RB']
        if value is not None:
            return value.copy()
        return None

    @cycle_aux_param.setter
    def cycle_aux_param(self, value):
        self['CycleAuxParam-SP'] = value

    @property
    def cycle_duration(self):
        """Total duration of the cycling process [s]."""
        if self.cycle_freq != 0:
            return self.cycle_num_cycles / self.cycle_freq
        return float('nan')

    @property
    def cycle_rampup_time(self):
        """Rampup time for Trapezoidal signals [s]."""
        return self.cycle_aux_param[0]

    @cycle_rampup_time.setter
    def cycle_rampup_time(self, value):
        """Set Rampup time for Trapezoidal signals [s]."""
        var = self.cycle_aux_param
        var[0] = value
        self.cycle_aux_param = var

    @property
    def cycle_theta_begin(self):
        """Return initial phase for Sine or Damped(Squared)Sine [°]."""
        return self.cycle_aux_param[0]

    @cycle_theta_begin.setter
    def cycle_theta_begin(self, value):
        """Set Initial phase for Sine or Damped(Squared)Sine [°]."""
        var = self.cycle_aux_param
        var[0] = value
        self.cycle_aux_param = var

    @property
    def cycle_rampdown_time(self):
        """Rampdown time for Trapezoidal signals [s]."""
        return self.cycle_aux_param[2]

    @cycle_rampdown_time.setter
    def cycle_rampdown_time(self, value):
        """Set Rampdown time for Trapezoidal signals [s]."""
        var = self.cycle_aux_param
        var[2] = value
        self.cycle_aux_param = var

    @property
    def cycle_theta_end(self):
        """Return final phase for Sine or Damped(Squared)Sine [°]."""
        return self.cycle_aux_param[1]

    @cycle_theta_end.setter
    def cycle_theta_end(self, value):
        """Set Final phase for Sine or Damped(Squared)Sine [°]."""
        var = self.cycle_aux_param
        var[1] = value
        self.cycle_aux_param = var

    @property
    def cycle_plateau_time(self):
        """Plateau time for Trapezoidal signals [s]."""
        return self.cycle_aux_param[1]

    @cycle_plateau_time.setter
    def cycle_plateau_time(self, value):
        """Set plateau time for Trapezoidal signals [s]."""
        var = self.cycle_aux_param
        var[1] = value
        self.cycle_aux_param = var

    @property
    def cycle_decay_time(self):
        """Decay time constant for Damped(Squared)Sine signals [s]."""
        return self.cycle_aux_param[2]

    @cycle_decay_time.setter
    def cycle_decay_time(self, value):
        """Set Decay time constant for Damped(Squared)Sine [s]."""
        var = self.cycle_aux_param
        var[2] = value
        self.cycle_aux_param = var

    @property
    def wfm_update_auto(self):
        """Waveform auto update."""
        return self['WfmUpdateAuto-Sts']

    @property
    def wfm_update_auto_str(self):
        """Waveform auto update."""
        return self.WFMUPDATEAUTO._fields[self['WfmUpdateAuto-Sts']]

    @wfm_update_auto.setter
    def wfm_update_auto(self, value):
        """Set waveform auto update."""
        self._enum_setter(
            'WfmUpdateAuto-Sel', value, self.WFMUPDATEAUTO)

    def cmd_slowref(self, timeout=_PSDev._default_timeout):
        """."""
        self['OpMode-Sel'] = self.OPMODE_SEL.SlowRef
        return self._wait(
            'OpMode-Sts', self.OPMODE_STS.SlowRef, timeout=timeout)

    def cmd_slowrefsync(self, timeout=_PSDev._default_timeout):
        """."""
        self['OpMode-Sel'] = self.OPMODE_SEL.SlowRefSync
        return self._wait(
            'OpMode-Sts', self.OPMODE_STS.SlowRefSync, timeout=timeout)

    def cmd_cycle(self, timeout=_PSDev._default_timeout):
        """."""
        self['OpMode-Sel'] = self.OPMODE_SEL.Cycle
        return self._wait(
            'OpMode-Sts', self.OPMODE_STS.Cycle, timeout=timeout)


class PowerSupplyPU(_PSDev):
    """Pulsed Power Supply Device."""

    PULSTATE = _PSCStatus.PWRSTATE
    DEF_TIMEOUT = 10

    class DEVICES:
        """Devices names."""

        TB_INJ_SEPT = 'TB-04:PU-InjSept'
        BO_INJ_KCKR = 'BO-01D:PU-InjKckr'
        BO_EJE_KCKR = 'BO-48D:PU-EjeKckr'
        TS_EJE_SEPTF = 'TS-01:PU-EjeSeptF'
        TS_EJE_SEPTG = 'TS-01:PU-EjeSeptG'
        TS_INJ_SEPTG_1 = 'TS-04:PU-InjSeptG-1'
        TS_INJ_SEPTG_2 = 'TS-04:PU-InjSeptG-2'
        TS_INJ_SEPTF = 'TS-04:PU-InjSeptF'
        SI_INJ_DPKCKR = 'SI-01SA:PU-InjDpKckr'
        SI_INJ_NLKCKR = 'SI-01SA:PU-InjNLKckr'
        SI_PING_H = 'SI-01SA:PU-PingH'
        SI_PING_V = 'SI-19C4:PU-PingV'
        ALL = (
            TB_INJ_SEPT,
            BO_INJ_KCKR, BO_EJE_KCKR,
            TS_EJE_SEPTF, TS_EJE_SEPTG,
            TS_INJ_SEPTG_1, TS_INJ_SEPTG_2,
            TS_INJ_SEPTF,
            SI_INJ_DPKCKR, SI_INJ_NLKCKR,
            SI_PING_H, SI_PING_V,
        )

    _properties_timing = ('Delay-SP', 'Delay-RB')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in PowerSupplyPU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname)

        # create timing device
        self._dev_timing = self._create_timing_device()

    @property
    def voltage(self):
        """."""
        return self['Voltage-RB']

    @voltage.setter
    def voltage(self, value):
        self['Voltage-SP'] = value

    @property
    def voltage_mon(self):
        """."""
        return self['Voltage-Mon']

    @property
    def delay(self):
        """."""
        return self._dev_timing['Delay-RB']

    @delay.setter
    def delay(self, value):
        """."""
        self._dev_timing['Delay-SP'] = value

    @property
    def pulse(self):
        """."""
        return self['Pulse-Sts']

    @pulse.setter
    def pulse(self, value):
        """."""
        self['Pulse-Sel'] = value

    def cmd_turn_on_pulse(self, timeout=DEF_TIMEOUT):
        """."""
        self.pulse = self.PULSTATE.On
        return self._wait('Pulse-Sts', value=self.PULSTATE.On, timeout=timeout)

    def cmd_turn_off_pulse(self, timeout=DEF_TIMEOUT):
        """."""
        self.pulse = self.PULSTATE.Off
        return self._wait(
            'Pulse-Sts', value=self.PULSTATE.Off, timeout=timeout)

    @property
    def properties(self):
        """Return device properties."""
        return self._properties + self._dev_timing.properties

    @property
    def pvnames(self):
        """Return device PV names."""
        return set(list(super().pvnames) +
                   list(self._dev_timing.pvnames))

    @property
    def interlock_ok(self):
        """Return whether all interlocks are in Ok state."""
        intlks = [p for p in self._properties if 'Intlk' in p]
        is_ok = True
        for ilk in intlks:
            is_ok &= self[ilk] == 1
        return is_ok

    @property
    def connected(self):
        """Return PVs connection status."""
        if not super().connected:
            return False
        return self._dev_timing.connected

    @property
    def disconnected_pvnames(self):
        """Return list of disconnected device PVs."""
        return set(list(super().disconnected_pvnames) +
                   list(self._dev_timing.disconnected_pvnames))

    def update(self):
        """Update device properties."""
        super().update()
        self._dev_timing.update()

    def pv_object(self, propty):
        """Return PV object for a given device property."""
        if propty in self._pvs:
            return super().pv_object(propty)
        return self._dev_timing.pv_object(propty)

    def pv_attribute_values(self, attribute):
        """Return property-value dict of a given attribute for all PVs."""
        attributes = super().pv_attribute_values(attribute)
        attributes_ti = self._dev_timing.pv_attribute_values(attribute)
        attributes.update(attributes_ti)
        return attributes

    def __getitem__(self, propty):
        """Return value of property."""
        if propty in self._pvs:
            return super().__getitem__(propty)
        return self._dev_timing[propty]

    def __setitem__(self, propty, value):
        """Set value of property."""
        if propty in self._pvs:
            super().__setitem__(propty, value)
        else:
            self._dev_timing[propty] = value

    # --- private methods ---

    def _create_timing_device(self):
        """."""
        devname = self._devname.substitute(dis='TI')
        device = _Device(devname, PowerSupplyPU._properties_timing)
        return device


class PowerSupplyFC(_PSDev):
    """Fast Correctors Power Supply Device."""

    OPMODE_SEL = _Const.OpModeFOFBSel
    OPMODE_STS = _Const.OpModeFOFBSts

    class DEVICES:
        """Devices names."""

    @property
    def opmode(self):
        """OpMode."""
        return self['OpMode-Sts']

    @opmode.setter
    def opmode(self, value):
        self._enum_setter('OpMode-Sel', value, self.OPMODE_SEL)

    @property
    def current(self):
        """Current setpoint."""
        return self['Current-RB']

    @current.setter
    def current(self, value):
        self['Current-SP'] = value

    @property
    def current_mon(self):
        """Implemented current."""
        return self['Current-Mon']

    @property
    def currentref_mon(self):
        """Current reference."""
        return self['CurrentRef-Mon']

    @property
    def curr_gain(self):
        """Current gain for A<->raw unit conversion."""
        return self['CurrGain-RB']

    @curr_gain.setter
    def curr_gain(self, value):
        self['CurrGain-SP'] = value

    @property
    def curr_offset(self):
        """Current offset for A<->raw unit conversion."""
        return self['CurrOffset-RB']

    @curr_offset.setter
    def curr_offset(self, value):
        self['CurrOffset-SP'] = value

    @property
    def voltage(self):
        """."""
        return self['Voltage-RB']

    @voltage.setter
    def voltage(self, value):
        """."""
        self['Voltage-SP'] = value

    @property
    def voltage_mon(self):
        """."""
        return self['Voltage-Mon']

    @property
    def volt_gain(self):
        """."""
        return self['VoltGain-RB']

    @volt_gain.setter
    def volt_gain(self, value):
        """."""
        self['VoltGain-SP'] = value

    @property
    def volt_offset(self):
        """."""
        return self['VoltOffset-RB']

    @volt_offset.setter
    def volt_offset(self, value):
        """."""
        self['VoltOffset-SP'] = value

    @property
    def currloop_kp(self):
        """Current control loop Kp parameter."""
        return self['CurrLoopKp-RB']

    @currloop_kp.setter
    def currloop_kp(self, value):
        self['CurrLoopKp-SP'] = value

    @property
    def currloop_ti(self):
        """Current control loop Ti parameter."""
        return self['CurrLoopTi-RB']

    @currloop_ti.setter
    def currloop_ti(self, value):
        self['CurrLoopTi-SP'] = value

    @property
    def currloop_mode(self):
        """Current control loop mode."""
        return self['CurrLoopMode-Sts']

    @currloop_mode.setter
    def currloop_mode(self, value):
        self['CurrLoopMode-Sel'] = value

    @property
    def alarms_amp(self):
        """."""
        return self['AlarmsAmp-Mon']

    def cmd_opmode_manual(self, timeout=_PSDev._default_timeout):
        """Set opmode to manual."""
        return self._set_opmode(mode=self.OPMODE_SEL.manual, timeout=timeout)

    def cmd_opmode_fofb(self, timeout=_PSDev._default_timeout):
        """Set opmode to fofb."""
        return self._set_opmode(mode=self.OPMODE_SEL.fofb, timeout=timeout)

    def _set_opmode(self, mode, timeout):
        self['OpMode-Sel'] = mode
        return self._wait('OpMode-Sts', mode, timeout=timeout)

    @property
    def invrespmat_row(self):
        """Correction coefficient value."""
        return self['InvRespMatRow-RB']

    @invrespmat_row.setter
    def invrespmat_row(self, value):
        self['InvRespMatRow-SP'] = _np.array(value, dtype=float)

    @property
    def fofbacc_gain(self):
        """FOFB accumulator gain."""
        return self['FOFBAccGain-RB']

    @fofbacc_gain.setter
    def fofbacc_gain(self, value):
        self['FOFBAccGain-SP'] = value

    @property
    def fofbacc_freeze(self):
        """FOFB accumulator freeze state."""
        return self['FOFBAccFreeze-Sts']

    @fofbacc_freeze.setter
    def fofbacc_freeze(self, value):
        self['FOFBAccFreeze-Sel'] = value

    @property
    def fofbacc_satmax(self):
        """FOFB accumulator maximum saturation."""
        return self['FOFBAccSatMax-RB']

    @fofbacc_satmax.setter
    def fofbacc_satmax(self, value):
        self['FOFBAccSatMax-SP'] = value

    @property
    def fofbacc_satmin(self):
        """FOFB accumulator minimum saturation."""
        return self['FOFBAccSatMin-RB']

    @fofbacc_satmin.setter
    def fofbacc_satmin(self, value):
        self['FOFBAccSatMin-SP'] = value

    def cmd_fofbacc_clear(self):
        """Command to clear FOFB accumulator."""
        self['FOFBAccClear-Cmd'] = 1
