"""Injection control IOC device."""

import numpy as _np

from ..clientarch import Time
from ..injctrl.csdev import Const as _Const

from .device import Device as _Device


class InjCtrl(_Device):
    """Injection Control IOC device."""

    OffOn = _Const.OffOn
    InjMode = _Const.InjMode
    InjType = _Const.InjType
    InjTypeMon = _Const.InjTypeMon
    PUMode = _Const.PUMode
    PUModeMon = _Const.PUModeMon
    TopUpSts = _Const.TopUpSts
    BiasFBModelTypes = _Const.BiasFBModelTypes
    IdleRun = _Const.IdleRunning

    PROPERTIES_DEFAULT = (
        'Mode-Sel', 'Mode-Sts',
        'Type-Sel', 'Type-Sts', 'Type-Mon', 'TypeCmdSts-Mon',
        'SglBunBiasVolt-SP', 'SglBunBiasVolt-RB',
        'MultBunBiasVolt-SP', 'MultBunBiasVolt-RB',
        'BiasVoltCmdSts-Mon',
        'FilaOpCurr-SP', 'FilaOpCurr-RB', 'FilaOpCurrCmdSts-Mon',
        'HVOpVolt-SP', 'HVOpVolt-RB', 'HVOpVoltCmdSts-Mon',
        'PUMode-Sel', 'PUMode-Sts', 'PUMode-Mon', 'PUModeCmdSts-Mon',
        'PUModeDeltaPosAng-SP', 'PUModeDeltaPosAng-RB',
        'PUModeDpKckrDlyRef-SP', 'PUModeDpKckrDlyRef-RB',
        'PUModeDpKckrKick-SP', 'PUModeDpKckrKick-RB',
        'TargetCurrent-SP', 'TargetCurrent-RB',
        'BucketListStart-SP', 'BucketListStart-RB',
        'BucketListStop-SP', 'BucketListStop-RB',
        'BucketListStep-SP', 'BucketListStep-RB',
        'TopUpState-Sel', 'TopUpState-Sts',
        'TopUpPeriod-SP', 'TopUpPeriod-RB',
        'TopUpHeadStartTime-SP', 'TopUpHeadStartTime-RB',
        'TopUpNextInj-Mon',
        'TopUpNrPulses-SP', 'TopUpNrPulses-RB',
        'InjSysTurnOn-Cmd', 'InjSysTurnOff-Cmd',
        'InjSysCmdDone-Mon', 'InjSysCmdSts-Mon',
        'InjSysTurnOnOrder-SP', 'InjSysTurnOnOrder-RB',
        'InjSysTurnOffOrder-SP', 'InjSysTurnOffOrder-RB',
        'RFKillBeam-Cmd', 'RFKillBeam-Mon',
        'DiagStatus-Mon', 'InjStatus-Mon',
        #  ----- bias feedback -----
        'BiasFBLoopState-Sel', 'BiasFBLoopState-Sts',
        'BiasFBMinVoltage-SP', 'BiasFBMinVoltage-RB',
        'BiasFBMaxVoltage-SP', 'BiasFBMaxVoltage-RB',
        'BiasFBModelType-Sel', 'BiasFBModelType-Sts',
        'BiasFBModelMaxNrPts-SP', 'BiasFBModelMaxNrPts-RB',
        'BiasFBModelNrPts-Mon',
        'BiasFBModelAutoFitParams-Sel', 'BiasFBModelAutoFitParams-Sts',
        'BiasFBModelAutoFitEveryNrPts-SP', 'BiasFBModelAutoFitEveryNrPts-RB',
        'BiasFBModelNrPtsAfterFit-Mon', 'BiasFBModelFitParamsNow-Cmd',
        'BiasFBModelUpdateData-Sel', 'BiasFBModelUpdateData-Sts',
        'BiasFBModelDataBias-SP', 'BiasFBModelDataBias-RB',
        'BiasFBModelDataBias-Mon',
        'BiasFBModelDataInjCurr-SP', 'BiasFBModelDataInjCurr-RB',
        'BiasFBModelDataInjCurr-Mon',
        'BiasFBLinModAngCoeff-SP', 'BiasFBLinModAngCoeff-RB',
        'BiasFBLinModAngCoeff-Mon',
        'BiasFBLinModOffCoeff-SP', 'BiasFBLinModOffCoeff-RB',
        'BiasFBLinModOffCoeff-Mon',
        'BiasFBLinModInferenceInjCurr-Mon', 'BiasFBLinModInferenceBias-Mon',
        'BiasFBLinModPredBias-Mon', 'BiasFBLinModPredInjCurrAvg-Mon',
        'BiasFBGPModNoiseStd-SP', 'BiasFBGPModNoiseStd-RB',
        'BiasFBGPModNoiseStd-Mon',
        'BiasFBGPModKernStd-SP', 'BiasFBGPModKernStd-RB',
        'BiasFBGPModKernStd-Mon',
        'BiasFBGPModKernLenScl-SP', 'BiasFBGPModKernLenScl-RB',
        'BiasFBGPModKernLenScl-Mon',
        'BiasFBGPModInferenceInjCurr-Mon', 'BiasFBGPModInferenceBias-Mon',
        'BiasFBGPModPredBias-Mon', 'BiasFBGPModPredInjCurrAvg-Mon',
        'BiasFBGPModPredInjCurrStd-Mon',
        )

    class DEVICES:
        """Devices names."""

        AS = 'AS-Glob:AP-InjCtrl'
        ALL = (AS, )

    def __init__(self, devname=None, props2init='all'):
        """Init."""
        if devname is None:
            devname = InjCtrl.DEVICES.AS
        if devname not in InjCtrl.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    # ----- general injection properties -----

    @property
    def injmode(self):
        """Injection mode (Decay or TopUp or Accum)."""
        return self['Mode-Sts']

    @injmode.setter
    def injmode(self, value):
        self._enum_setter('Mode-Sel', value, self.InjMode)

    @property
    def injmode_str(self):
        """Injection mode string (Decay or TopUp or Accum)."""
        return self.InjMode._fields[self['Mode-Sts']]

    def wait_injmode(self, injmode, timeout=None):
        """Wait Mode-Sts to reach `injmode` value."""
        if isinstance(injmode, str):
            injmode = self.InjMode._fields.index(injmode)
        return self._wait('Mode-Sts', injmode, timeout=timeout)

    @property
    def injtype(self):
        """Injection type (SingleBunch or MultiBunch)."""
        return self['Type-Sts']

    @injtype.setter
    def injtype(self, value):
        self._enum_setter('Type-Sel', value, self.InjType)

    @property
    def injtype_str(self):
        """Injection type string (SingleBunch or MultiBunch)."""
        return self.InjType._fields[self['Type-Sts']]

    @property
    def injtype_mon(self):
        """Injection type (SingleBunch, MultiBunch or Undefined)."""
        return self['Type-Mon']

    @property
    def injtype_cmd_status(self):
        """Injection type command status (Idle or Running)."""
        return self['TypeCmdSts-Mon']

    def wait_injtype_cmd_finish(self, timeout=None):
        """Wait TypeCmdSts-Mon to reach `Idle` value."""
        return self._wait(
            'TypeCmdSts-Mon', self.IdleRun.Idle, timeout=timeout)

    @property
    def bias_volt_sglbun(self):
        """Bias voltage for single bunch injection type."""
        return self['SglBunBiasVolt-RB']

    @bias_volt_sglbun.setter
    def bias_volt_sglbun(self, value):
        self['SglBunBiasVolt-SP'] = value

    @property
    def bias_volt_multbun(self):
        """Bias voltage for multi bunch injection type."""
        return self['MultBunBiasVolt-RB']

    @bias_volt_multbun.setter
    def bias_volt_multbun(self, value):
        self['MultBunBiasVolt-SP'] = value

    @property
    def bias_volt_cmd_status(self):
        """Bias voltage command status (Idle or Running)."""
        return self['BiasVoltCmdSts-Mon']

    def wait_bias_volt_cmd_finish(self, timeout=None):
        """Wait BiasVoltCmdSts-Mon to reach `Idle` value."""
        return self._wait(
            'BiasVoltCmdSts-Mon', self.IdleRun.Idle, timeout=timeout)

    @property
    def filacurr_opvalue(self):
        """EGun filament operation current value."""
        return self['FilaOpCurr-RB']

    @filacurr_opvalue.setter
    def filacurr_opvalue(self, value):
        self['FilaOpCurr-SP'] = value

    @property
    def filacurr_cmd_status(self):
        """EGun filament current setpoint command status (Idle or Running)."""
        return self['FilaOpCurrCmdSts-Mon']

    def wait_filacurr_cmd_finish(self, timeout=None):
        """Wait FilaOpCurrCmdSts-Mon to reach `Idle` value."""
        return self._wait(
            'FilaOpCurrCmdSts-Mon', self.IdleRun.Idle, timeout=timeout)

    @property
    def hvolt_opvalue(self):
        """EGun high voltage operation value."""
        return self['HVOpVolt-RB']

    @hvolt_opvalue.setter
    def hvolt_opvalue(self, value):
        self['HVOpVolt-SP'] = value

    @property
    def hvolt_cmd_status(self):
        """EGun high voltage setpoint command status (Idle or Running)."""
        return self['HVOpVoltCmdSts-Mon']

    def wait_hvolt_cmd_finish(self, timeout=None):
        """Wait HVOpVoltCmdSts-Mon to reach `Idle` value."""
        return self._wait(
            'HVOpVoltCmdSts-Mon', self.IdleRun.Idle, timeout=timeout)

    @property
    def pumode_delta_posang(self):
        """."""
        return self['PUModeDeltaPosAng-RB']

    @pumode_delta_posang.setter
    def pumode_delta_posang(self, value):
        self['PUModeDeltaPosAng-SP'] = value

    @property
    def pumode_dpkckr_dlyref(self):
        """."""
        return self['PuModeDpKckrDlyRef-RB']

    @pumode_dpkckr_dlyref.setter
    def pumode_dpkckr_dlyref(self, value):
        self['PUModeDpKckrDlyRef-SP'] = value

    @property
    def pumode_dpkckr_kick(self):
        """."""
        return self['PUModeDpKckrKick-RB']

    @pumode_dpkckr_kick.setter
    def pumode_dpkckr_kick(self, value):
        self['PUModeDpKckrKick-SP'] = value

    @property
    def pumode(self):
        """PU mode (Accumulation, Optimization or OnAxis)."""
        return self['PUMode-Sts']

    @pumode.setter
    def pumode(self, value):
        self._enum_setter('PUMode-Sel', value, self.PUMode)

    @property
    def pumode_str(self):
        """PU mode string (Accumulation, Optimization or OnAxis)."""
        return self.PUMode._fields[self['PUMode-Sts']]

    @property
    def pumode_mon(self):
        """PU mode (Accumulation, Optimization, OnAxis or Undefined)."""
        return self['PUMode-Mon']

    @property
    def pumode_cmd_status(self):
        """PU mode command status (Idle or Running)."""
        return self['PUModeCmdSts-Mon']

    def wait_pumode_cmd_finish(self, timeout=None):
        """Wait PUModeCmdSts-Mon to reach `Idle` value."""
        return self._wait(
            'PUModeCmdSts-Mon', self.IdleRun.Idle, timeout=timeout)

    def cmd_change_pumode_to_onaxis(self, timeout=10):
        """Change PUMode to On-Axis injection."""
        self.pumode = self.PUMode.OnAxis
        return self._wait('PUMode-Mon', self.PUModeMon.OnAxis, timeout=timeout)

    def cmd_change_pumode_to_accumulation(self, timeout=10):
        """Change PUMode to accumulation."""
        self.pumode = self.PUMode.Accumulation
        return self._wait(
            'PUMode-Mon', self.PUModeMon.Accumulation, timeout=timeout)

    def cmd_change_pumode_to_optimization(self, timeout=10):
        """Change PUMode to optimization."""
        self.pumode = self.PUMode.Optimization
        return self._wait(
            'PUMode-Mon', self.PUModeMon.Optimization, timeout=timeout)

    @property
    def target_current(self):
        """Target current value."""
        return self['TargetCurrent-RB']

    @target_current.setter
    def target_current(self, value):
        self['TargetCurrent-SP'] = value

    @property
    def bucketlist_start(self):
        """Bucket list start value."""
        return self['BucketListStart-RB']

    @bucketlist_start.setter
    def bucketlist_start(self, value):
        self['BucketListStart-SP'] = value

    @property
    def bucketlist_step(self):
        """Bucket list step value."""
        return self['BucketListStep-RB']

    @bucketlist_step.setter
    def bucketlist_step(self, value):
        self['BucketListStep-SP'] = value

    @property
    def bucketlist_stop(self):
        """Bucket list stop value."""
        return self['BucketListStop-RB']

    @bucketlist_stop.setter
    def bucketlist_stop(self, value):
        self['BucketListStop-SP'] = value

    # ----- injection mode properties -----

    @property
    def topup_state(self):
        """Top-up state (Off, Waiting, TurningOn, Injecting or TurningOff)."""
        return self['TopUpState-Sts']

    @topup_state.setter
    def topup_state(self, value):
        self._enum_setter('TopUpState-Sel', value, self.OffOn)

    @property
    def topup_state_str(self):
        """Top-up state (Off, Waiting, TurningOn, Injecting or TurningOff)."""
        return self.TopUpSts._fields[self['TopUpState-Sts']]

    @property
    def topup_period(self):
        """Top-up period [min]."""
        return self['TopUpPeriod-RB']

    @topup_period.setter
    def topup_period(self, value):
        self['TopUpPeriod-SP'] = value

    @property
    def topup_headstarttime(self):
        """Top-up head start time [s]."""
        return self['TopUpHeadStartTime-RB']

    @topup_headstarttime.setter
    def topup_headstarttime(self, value):
        self['TopUpHeadStartTime-SP'] = value

    @property
    def topup_nrpulses(self):
        """Top-up number of pulses [s]."""
        return self['TopUpNrPulses-RB']

    @topup_nrpulses.setter
    def topup_nrpulses(self, value):
        self['TopUpNrPulses-SP'] = value

    @property
    def topup_nextinj_timestamp(self):
        """Next topup scheduled injection [s]."""
        return self['TopUpNextInj-Mon']

    @property
    def topup_nextinj_time(self):
        """Next topup scheduled injection Time object."""
        return Time.fromtimestamp(self['TopUpNextInj-Mon'])

    # ----- bias feedback properties -----

    @property
    def biasfb_loop_state(self):
        """Bias FB loop state."""
        return self['BiasFBLoopState-Sts']

    @biasfb_loop_state.setter
    def biasfb_loop_state(self, value):
        self._enum_setter('BiasFBLoopState-Sel', value, self.OffOn)

    @property
    def biasfb_voltage_min(self):
        """Bias FB minimum voltage [V]."""
        return self['BiasFBMinVoltage-RB']

    @biasfb_voltage_min.setter
    def biasfb_voltage_min(self, value):
        self['BiasFBMinVoltage-SP'] = value

    @property
    def biasfb_voltage_max(self):
        """Bias FB maximum voltage [V]."""
        return self['BiasFBMaxVoltage-RB']

    @biasfb_voltage_max.setter
    def biasfb_voltage_max(self, value):
        self['BiasFBMaxVoltage-SP'] = value

    @property
    def biasfb_model_type(self):
        """Bias FB model type."""
        return self['BiasFBModelType-Sts']

    @biasfb_model_type.setter
    def biasfb_model_type(self, value):
        self._enum_setter('BiasFBModelType-Sel', value, self.BiasFBModelTypes)

    @property
    def biasfb_model_maxnrpts(self):
        """Bias FB model maximum number of points [#]."""
        return self['BiasFBModelMaxNrPts-RB']

    @biasfb_model_maxnrpts.setter
    def biasfb_model_maxnrpts(self, value):
        self['BiasFBModelMaxNrPts-SP'] = value

    @property
    def biasfb_model_nrpts(self):
        """Bias FB model number of points [#]."""
        return self['BiasFBModelNrPts-Mon']

    @property
    def biasfb_model_autofit_enbl(self):
        """Bias FB auto fit enable status."""
        return self['BiasFBModelAutoFitParams-Sts']

    @biasfb_model_autofit_enbl.setter
    def biasfb_model_autofit_enbl(self, value):
        self._enum_setter('BiasFBModelAutoFitParams-Sel', value, self.OffOn)

    @property
    def biasfb_model_autofit_rate(self):
        """Bias FB model auto fit rate [#]."""
        return self['BiasFBModelAutoFitEveryNrPts-RB']

    @biasfb_model_autofit_rate.setter
    def biasfb_model_autofit_rate(self, value):
        self['BiasFBModelAutoFitEveryNrPts-SP'] = value

    @property
    def biasfb_model_nrpts_after_fit(self):
        """Bias FB model number of points after last fit [#]."""
        return self['BiasFBModelNrPtsAfterFit-Mon']

    def cmd_biasfb_model_fitnow(self):
        """Fit Bias FB model."""
        self['BiasFBModelFitParamsNow-Cmd'] = 1
        return True

    @property
    def biasfb_model_updatedata(self):
        """Bias FB auto fit enable status."""
        return self['BiasFBModelUpdateData-Sts']

    @biasfb_model_updatedata.setter
    def biasfb_model_updatedata(self, value):
        self._enum_setter('BiasFBModelUpdateData-Sel', value, self.OffOn)

    @property
    def biasfb_model_data_bias(self):
        """Bias FB model data bias setpoint [V]."""
        return self['BiasFBModelDataBias-RB']

    @biasfb_model_data_bias.setter
    def biasfb_model_data_bias(self, value):
        self['BiasFBModelDataBias-SP'] = _np.array(value, dtype=float)

    @property
    def biasfb_model_data_bias_mon(self):
        """Bias FB implemented model data bias [V]."""
        return self['BiasFBModelDataBias-Mon']

    @property
    def biasfb_model_data_injcurr(self):
        """Bias FB model data injected current setpoint [mA]."""
        return self['BiasFBModelDataInjCurr-RB']

    @biasfb_model_data_injcurr.setter
    def biasfb_model_data_injcurr(self, value):
        self['BiasFBModelDataInjCurr-SP'] = _np.array(value, dtype=float)

    @property
    def biasfb_model_data_injcurr_mon(self):
        """Bias FB implemented model data injected current [mA]."""
        return self['BiasFBModelDataInjCurr-Mon']

    @property
    def biasfb_linmodel_angcoeff(self):
        """Bias FB linear model angular coefficient."""
        return self['BiasFBLinModAngCoeff-RB']

    @biasfb_linmodel_angcoeff.setter
    def biasfb_linmodel_angcoeff(self, value):
        self['BiasFBLinModAngCoeff-SP'] = value

    @property
    def biasfb_linmodel_angcoeff_mon(self):
        """Bias FB implemented linear model angular coefficient."""
        return self['BiasFBLinModAngCoeff-Mon']

    @property
    def biasfb_linmodel_offcoeff(self):
        """Bias FB linear model offset coefficient."""
        return self['BiasFBLinModOffCoeff-RB']

    @biasfb_linmodel_offcoeff.setter
    def biasfb_linmodel_offcoeff(self, value):
        self['BiasFBLinModOffCoeff-SP'] = value

    @property
    def biasfb_linmodel_offcoeff_mon(self):
        """Bias FB implemented linear model offset coefficient."""
        return self['BiasFBLinModOffCoeff-Mon']

    @property
    def biasfb_linmodel_infer_injcurr(self):
        """Injected current for bias FB linear model inference."""
        return self['BiasFBLinModInferenceInjCurr-Mon']

    @property
    def biasfb_linmodel_infer_bias(self):
        """Bias for bias FB linear model inference."""
        return self['BiasFBLinModInferenceBias-Mon']

    @property
    def biasfb_linmodel_predct_injcurr(self):
        """Injected current for bias FB linear model prediction."""
        return self['BiasFBLinModPredInjCurrAvg-Mon']

    @property
    def biasfb_linmodel_predct_bias(self):
        """Bias for bias FB linear model prediction."""
        return self['BiasFBLinModPredBias-Mon']

    @property
    def biasfb_gpmodel_likehd_std(self):
        """Bias FB GP model likelihood standard deviation."""
        return self['BiasFBGPModNoiseStd-RB']

    @biasfb_gpmodel_likehd_std.setter
    def biasfb_gpmodel_likehd_std(self, value):
        self['BiasFBGPModNoiseStd-SP'] = value

    @property
    def biasfb_gpmodel_likehd_std_mon(self):
        """Bias FB implemented GP model likelihood standard deviation."""
        return self['BiasFBGPModNoiseStd-Mon']

    @property
    def biasfb_gpmodel_kern_std(self):
        """Bias FB GP model kernel standard deviation."""
        return self['BiasFBGPModKernStd-RB']

    @biasfb_gpmodel_kern_std.setter
    def biasfb_gpmodel_kern_std(self, value):
        self['BiasFBGPModKernStd-SP'] = value

    @property
    def biasfb_gpmodel_kern_std_mon(self):
        """Bias FB implemented GP model kernel standard deviation."""
        return self['BiasFBGPModKernStd-Mon']

    @property
    def biasfb_gpmodel_kern_leng(self):
        """Bias FB GP model kernel length scale."""
        return self['BiasFBGPModKernLenScl-RB']

    @biasfb_gpmodel_kern_leng.setter
    def biasfb_gpmodel_kern_leng(self, value):
        self['BiasFBGPModKernLenScl-SP'] = value

    @property
    def biasfb_gpmodel_kern_leng_mon(self):
        """Bias FB implemented GP model kernel length scale."""
        return self['BiasFBGPModKernLenScl-Mon']

    @property
    def biasfb_gpmodel_infer_injcurr(self):
        """Injected current for bias FB GP model inference."""
        return self['BiasFBGPModInferenceInjCurr-Mon']

    @property
    def biasfb_gpmodel_infer_bias(self):
        """Bias for bias FB GB model inference."""
        return self['BiasFBGPModInferenceBias-Mon']

    @property
    def biasfb_gpmodel_predct_injcurr_avg(self):
        """Injected current for bias FB GB model prediction."""
        return self['BiasFBGPModPredInjCurrAvg-Mon']

    @property
    def biasfb_gpmodel_predct_injcurr_std(self):
        """Injected current for bias FB GB model prediction."""
        return self['BiasFBGPModPredInjCurrStd-Mon']

    @property
    def biasfb_gpmodel_predct_bias(self):
        """Bias for bias FB GB model prediction."""
        return self['BiasFBGPModPredBias-Mon']

    # ----- injection system properties -----

    def cmd_injsys_turn_on(self):
        """Injection system turn on command."""
        self['InjSysTurnOn-Cmd'] = 1
        return True

    @property
    def injsys_turn_on_order(self):
        """Injection system turn on command order.

        Return
        ------
        str
            A string of a list with the reference of the handlers,
            in the order that they are executed in turn on command.
            Default value: 'bo_rf,as_pu,bo_ps,li_rf'.
        """
        return self['InjSysTurnOnOrder-RB']

    @injsys_turn_on_order.setter
    def injsys_turn_on_order(self, value):
        self['InjSysTurnOnOrder-SP'] = value

    def cmd_injsys_turn_off(self):
        """Injection system turn off command."""
        self['InjSysTurnOff-Cmd'] = 1
        return True

    @property
    def injsys_turn_off_order(self):
        """Injection system turn on command order.

        Return
        ------
        str
            A string of a list with the reference of the handlers,
            in the order that they are executed in turn off command.
            Default value: 'bo_rf,li_rf,as_pu,bo_ps'.
        """
        return self['InjSysTurnOffOrder-RB']

    @injsys_turn_off_order.setter
    def injsys_turn_off_order(self, value):
        self['InjSysTurnOffOrder-SP'] = value

    @property
    def injsys_cmd_status(self):
        """Injection system command status (Idle or Running)."""
        return self['InjSysCmdSts-Mon']

    def wait_injsys_cmd_finish(self, timeout=None):
        """Wait InjSysCmdSts-Mon to reach `Idle` value."""
        return self._wait(
            'InjSysCmdSts-Mon', self.IdleRun.Idle, timeout=timeout)

    def check_injsys_cmd_completed(self):
        """Check whether InjSys command completed succesfully."""
        done = self['InjSysCmdDone-Mon']
        order = self['InjSysTurnOffOrder-RB']
        if None in [done, order]:
            return False
        done = set(done.split(','))
        order = set(order.split(','))
        return done == order

    # ----- kill beam properties -----

    def cmd_rfkillbeam(self):
        """RF Kill Beam command."""
        self['RFKillBeam-Cmd'] = 1
        return True

    @property
    def rfkillbeam_cmd_status(self):
        """Kill beam command status (Idle or Kill)."""
        return self['RFKillBeam-Mon']

    def wait_rfkillbeam_cmd_finish(self, timeout=None):
        """Wait RFKillBeam-Mon to reach `Idle` value."""
        return self._wait(
            'RFKillBeam-Mon', self.IdleRun.Idle, timeout=timeout)

    # ----- diagnostics properties -----

    @property
    def diag_status(self):
        """Diagnostics status."""
        return self['DiagStatus-Mon']

    @property
    def inj_status(self):
        """Injection status."""
        return self['InjStatus-Mon']
