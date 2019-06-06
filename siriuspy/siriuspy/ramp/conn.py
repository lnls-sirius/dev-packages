"""Module with connector classes.

This module implements connector classes responsible for communications with
magnet soft IOcs, ConfigDB service and orbit IOCs.
"""

from siriuspy import envars as _envars
from siriuspy.epics.properties import EpicsProperty as _EpicsProperty
from siriuspy.epics.properties import EpicsPropertiesList as _EpicsPropsList
from siriuspy.csdevice import util as _cutil
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.timesys import Const as _TIConst, \
    get_hl_trigger_database as _get_trig_db
from siriuspy.csdevice.orbitcorr import SOFBRings as _SOFBRings
from siriuspy.servconf.srvconfig import ConnConfigService as _ConnConfigService
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.timesys.ll_classes import get_evg_name as _get_evg_name
from siriuspy.ramp import util as _rutil


_prefix = _envars.vaca_prefix
_PWRSTATE_ON_DELAY = 1.4
_PWRSTATE_OFF_DELAY = 0.8
_TIMEOUT_DFLT = 1.4


class ConnConfig_BORamp(_ConnConfigService):
    """ConfigurationService connector class for BO ramp configs."""

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_ramp',
                                    url=url)


class ConnConfig_BONormalized(_ConnConfigService):
    """ConfigurationService connector for BO normalized configs."""

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_normalized', url=url)


class ConnTiming(_EpicsPropsList):
    """Timing connector class."""

    class Const(_cutil.Const):
        """Properties names."""

        # EVG PVs
        EVG = _get_evg_name()
        EVG_DevEnbl = EVG + ':DevEnbl-Sel'
        EVG_ContinuousEvt = EVG + ':ContinuousEvt-Sel'
        EVG_InjectionEvt = EVG + ':InjectionEvt-Sel'

        # Event prefixes
        EvtLinac = EVG + ':Linac'
        EvtInjBO = EVG + ':InjBO'
        EvtRmpBO = EVG + ':RmpBO'
        EvtInjSI = EVG + ':InjSI'

        # Trigger prefixes
        TrgMags = 'BO-Glob:TI-Mags'
        TrgCorrs = 'BO-Glob:TI-Corrs'
        TrgLLRFRmp = 'BO-Glob:TI-LLRF-Rmp'
        TrgEGunSglBun = 'LI-01:TI-EGun-SglBun'
        TrgEGunMultBun = 'LI-01:TI-EGun-MultBun'
        TrgEjeKckr = 'BO-48D:TI-EjeKckr'

        # Linac Egun mode properties
        LinacEgun_SglBun_State = 'egun:pulseps:singleselstatus'
        LinacEgun_MultBun_State = 'egun:pulseps:multiselstatus'

        # Interlock PV
        Intlk = 'LA-RFH01RACK2:TI-EVR:Intlk-Mon'

    # Add events properties to Const
    evt_propties = ['Mode-Sel', 'DelayType-Sel', 'Delay-SP']
    for attr in ['EvtLinac', 'EvtInjBO', 'EvtRmpBO', 'EvtInjSI']:
        for p in evt_propties:
            evt_pfx = getattr(Const, attr)
            new_attr = attr+'_'+p.replace('-'+p.split('-')[-1], '')
            setattr(Const, new_attr, evt_pfx+p)

    # Add trigger properties to Const
    trg_propties = ['State-Sel', 'Polarity-Sel', 'Src-Sel', 'NrPulses-SP',
                    'Duration-SP', 'Delay-SP', 'Status-Mon']
    for attr in ['TrgMags', 'TrgCorrs', 'TrgLLRFRmp',
                 'TrgEGunSglBun', 'TrgEGunMultBun', 'TrgEjeKckr']:
        for p in trg_propties:
            trg_pfx = getattr(Const, attr)
            new_attr = attr+'_'+p.replace('-'+p.split('-')[-1], '')
            setattr(Const, new_attr, trg_pfx+':'+p)
    Const.TrgLLRFRmp_RFDelayType = Const.TrgLLRFRmp + ':RFDelayType-Sel'

    def __init__(self, ramp_config=None, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        self._ramp_config = ramp_config
        properties = self._define_properties(prefix, connection_callback,
                                             callback)
        super().__init__(properties)

    def get_ramp_config(self, ramp_config):
        """Receive BoosterRamp configuration."""
        self._ramp_config = ramp_config

    # --- timing setup commands ---

    def cmd_setup(self, timeout=_TIMEOUT_DFLT):
        """Setup TI subsystem to ramp."""
        sp = self.ramp_basicsetup.copy()
        for ppty in sp:
            if 'Status-Mon' in ppty:
                sp.pop(ppty)
        return self.set_setpoints_check(sp, timeout)

    def cmd_config_ramp(self, timeout=_TIMEOUT_DFLT):
        """Apply ramp_config values to TI subsystem."""
        if not self._ramp_config:
            return

        sp = dict()
        c = ConnTiming.Const
        sp[c.TrgMags_Duration] = self._ramp_config.ps_ramp_duration
        sp[c.TrgCorrs_Duration] = self._ramp_config.ps_ramp_duration
        sp[c.TrgMags_NrPulses] = self._ramp_config.ps_ramp_wfm_nrpoints
        sp[c.TrgCorrs_NrPulses] = self._ramp_config.ps_ramp_wfm_nrpoints
        sp[c.TrgMags_Delay] = self._ramp_config.ti_params_ps_ramp_delay
        sp[c.TrgCorrs_Delay] = self._ramp_config.ti_params_ps_ramp_delay
        sp[c.TrgLLRFRmp_Delay] = self._ramp_config.ti_params_rf_ramp_delay

        # Event delays
        sp[c.EvtRmpBO_Delay] = 0
        [linac_dly, injbo_dly, injsi_dly] = self.calc_evts_delay()
        sp[c.EvtLinac_Delay] = linac_dly
        sp[c.EvtInjBO_Delay] = injbo_dly
        sp[c.EvtInjSI_Delay] = injsi_dly

        return self.set_setpoints_check(sp, timeout)

    def cmd_start_ramp(self, timeout=_TIMEOUT_DFLT):
        """Start EVG continuous events."""
        sp = {ConnTiming.Const.EVG_ContinuousEvt: _TIConst.DsblEnbl.Enbl}
        return self.set_setpoints_check(sp, timeout)

    def cmd_stop_ramp(self, timeout=_TIMEOUT_DFLT):
        """Stop EVG continuous events."""
        sp = {ConnTiming.Const.EVG_ContinuousEvt: _TIConst.DsblEnbl.Dsbl}
        return self.set_setpoints_check(sp, timeout)

    def cmd_start_injection(self, timeout=_TIMEOUT_DFLT):
        """Start EVG injection events."""
        sp = {ConnTiming.Const.EVG_InjectionEvt: _TIConst.DsblEnbl.Enbl}
        return self.set_setpoints_check(sp, timeout)

    def cmd_stop_injection(self, timeout=_TIMEOUT_DFLT):
        """Stop EVG injection events."""
        sp = {ConnTiming.Const.EVG_InjectionEvt: _TIConst.DsblEnbl.Dsbl}
        return self.set_setpoints_check(sp, timeout)

    # --- timing mode check ---

    def check_intlk(self):
        """Check if interlock is reset."""
        return self._check(ConnTiming.Const.Intlk, 0)

    def check_setup_ramp(self):
        """Check if ramp basic setup is implemented."""
        return self._check(self.ramp_basicsetup)

    def check_ramping(self):
        """Check if continuous events are enabled."""
        rb = {ConnTiming.Const.EVG_ContinuousEvt: _TIConst.DsblEnbl.Enbl}
        return self._check(rb)

    def check_injecting(self):
        """Check if injection events are enabled."""
        rb = {ConnTiming.Const.EVG_InjectionEvt: _TIConst.DsblEnbl.Enbl}
        return self._check(rb)

    # --- helper methods ---

    def calc_evts_delay(self):
        """Calculate event delays."""
        if not self._ramp_config:
            return False
        if not self.connected:
            return False

        c = ConnTiming.Const
        injection_time = self._ramp_config.ti_params_injection_time
        egun_dly = self.get_readback(c.TrgEGunSglBun_Delay) \
            if self.get_readback(c.LinacEgun_SglBun_State) \
            else self.get_readback(c.TrgEGunMultBun_Delay)
        linac_dly = injection_time - egun_dly

        curr_linac_dly = self.get_readback(c.EvtLinac_Delay)
        delta_dly = linac_dly - curr_linac_dly
        curr_injbo_dly = self.get_readback(c.EvtInjBO_Delay)
        injbo_dly = curr_injbo_dly + delta_dly

        ejection_time = self._ramp_config.ti_params_ejection_time
        ejekckr_dly = self.get_readback(c.TrgEjeKckr_Delay)
        injsi_dly = ejection_time - ejekckr_dly

        return [linac_dly, injbo_dly, injsi_dly]

    # --- private methods ---

    def _define_properties(self, prefix, connection_callback, callback):
        c = ConnTiming.Const

        mags_db = _get_trig_db(c.TrgMags)
        corrs_db = _get_trig_db(c.TrgCorrs)
        llrf_db = _get_trig_db(c.TrgLLRFRmp)

        self.ramp_basicsetup = {
            # EVG
            c.EVG_DevEnbl: _TIConst.DsblEnbl.Enbl,
            # Linac Event
            c.EvtLinac_Mode: _TIConst.EvtModes.Injection,
            c.EvtLinac_DelayType: _TIConst.EvtDlyTyp.Incr,
            # InjBO Event
            c.EvtInjBO_Mode: _TIConst.EvtModes.Injection,
            c.EvtInjBO_DelayType: _TIConst.EvtDlyTyp.Incr,
            # RmpBO Event
            c.EvtRmpBO_Mode: _TIConst.EvtModes.Continuous,
            c.EvtRmpBO_DelayType: _TIConst.EvtDlyTyp.Incr,
            # InjSI Event
            c.EvtInjSI_Mode: _TIConst.EvtModes.Injection,
            c.EvtInjSI_DelayType: _TIConst.EvtDlyTyp.Incr,
            # Mags trigger
            c.TrgMags_State: _TIConst.DsblEnbl.Enbl,
            c.TrgMags_Polarity: _TIConst.TrigPol.Inverse,
            c.TrgMags_Src: mags_db['Src-Sel']['enums'].index('RmpBO'),
            c.TrgMags_Status: 0,
            # Corrs trigger
            c.TrgCorrs_State: _TIConst.DsblEnbl.Enbl,
            c.TrgCorrs_Polarity: _TIConst.TrigPol.Inverse,
            c.TrgCorrs_Src: corrs_db['Src-Sel']['enums'].index('RmpBO'),
            c.TrgCorrs_Status: 0,
            # LLRFRmp trigger
            c.TrgLLRFRmp_State: _TIConst.DsblEnbl.Enbl,
            c.TrgLLRFRmp_Polarity: _TIConst.TrigPol.Inverse,
            c.TrgLLRFRmp_Src: llrf_db['Src-Sel']['enums'].index('RmpBO'),
            c.TrgLLRFRmp_NrPulses: 1,
            c.TrgLLRFRmp_Duration: 0.016,
            c.TrgLLRFRmp_RFDelayType: _TIConst.TrigDlyTyp.Manual,
            c.TrgLLRFRmp_Status: 0}

        self.ramp_configsetup = {
            # Event delays
            c.EvtLinac_Delay: 0,          # [us]
            c.EvtInjBO_Delay: 0,          # [us]
            c.EvtRmpBO_Delay: 0,          # [us]
            c.EvtInjSI_Delay: 0,          # [us]
            # Mags trigger
            c.TrgMags_NrPulses: 3920,
            c.TrgMags_Duration: 490000,   # [us]
            c.TrgMags_Delay: 0,           # [us]
            # Corrs trigger
            c.TrgCorrs_NrPulses: 3920,
            c.TrgCorrs_Duration: 490000,  # [us]
            c.TrgCorrs_Delay: 0,          # [us]
            # LLRFRmp trigger
            c.TrgLLRFRmp_Delay: 0}        # [us]

        self._evgcontrol_propties = {
            c.EVG_ContinuousEvt: _TIConst.DsblEnbl.Dsbl,
            c.EVG_InjectionEvt: _TIConst.DsblEnbl.Dsbl}

        self._reading_propties = {
            # EGun trigger delays
            c.TrgEGunSglBun_Delay: 0,     # [us]
            c.TrgEGunMultBun_Delay: 0,    # [us]
            # EjeKckr trigger delay
            c.TrgEjeKckr_Delay: 0,        # [us]
            # LinacEgun Mode
            c.LinacEgun_SglBun_State: 0,
            c.LinacEgun_MultBun_State: 0,
            # Intlk
            c.Intlk: 0}

        propty2defaultvalue = self.ramp_basicsetup.copy()
        propty2defaultvalue.update(self.ramp_configsetup)
        propty2defaultvalue.update(self._evgcontrol_propties)
        propty2defaultvalue.update(self._reading_propties)

        properties = list()
        for propty, default_value in propty2defaultvalue.items():
            properties.append(
                _EpicsProperty(propty, prefix, default_value,
                               connection_callback=connection_callback,
                               callback=callback))
        return properties

    def _check(self, readbacks):
        for name, value in readbacks.items():
            if not self.get_readback(name) == value:
                return False
        return True


class ConnMagnets(_EpicsPropsList):
    """Magnets connector class."""

    def __init__(self, ramp_config=None, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        self._ramp_config = ramp_config
        self._get_manames()
        properties = self._define_properties(prefix, connection_callback,
                                             callback)
        super().__init__(properties)

    @property
    def manames(self):
        """Return manames."""
        return self._manames

    def get_ramp_config(self, ramp_config):
        """Receive BoosterRamp configuration."""
        self._ramp_config = ramp_config

    # --- power supplies commands ---

    def cmd_pwrstate_on(self, timeout=_PWRSTATE_ON_DELAY):
        """Turn all power supplies on."""
        return self._command('PwrState-Sel', _PSConst.PwrStateSel.On, timeout)

    def cmd_pwrstate_off(self, timeout=_PWRSTATE_OFF_DELAY):
        """Turn all power supplies off."""
        return self._command('PwrState-Sel', _PSConst.PwrStateSel.Off, timeout)

    def cmd_opmode_slowref(self, timeout=_TIMEOUT_DFLT):
        """Select SlowRef opmode for all power supplies."""
        return self._command('OpMode-Sel', _PSConst.OpMode.SlowRef, timeout)

    def cmd_opmode_cycle(self, timeout=_TIMEOUT_DFLT):
        """Select Cycle opmode for all power supplies."""
        return self._command('OpMode-Sel', _PSConst.OpMode.Cycle, timeout)

    def cmd_opmode_rmpwfm(self, timeout=_TIMEOUT_DFLT):
        """Select RmpWfm opmode for all power supplies."""
        return self._command('OpMode-Sel', _PSConst.OpMode.RmpWfm, timeout)

    def cmd_wfmdata(self, timeout=_TIMEOUT_DFLT):
        """Set wfmdata of all powersupplies."""
        if self._ramp_config is None:
            return False
        setpoints = dict()
        for maname in self.manames:
            # get value (wfmdata)
            wf = self._ramp_config.ps_waveform_get(maname)
            value = wf.currents
            name = maname + ':WfmData-SP'
            setpoints[name] = value
        return self.set_setpoints_check(setpoints, timeout)

    # --- power supplies checks ---

    def check_pwrstate_on(self):
        """Check pwrstates of all power supplies are On."""
        return self._check('PwrState-Sel', _PSConst.PwrStateSts.On)

    def check_opmode_slowref(self):
        """Check opmodes of all power supplies ar SlowRef."""
        return self._check('OpMode-Sel', _PSConst.OpMode.SlowRef)

    def check_opmode_cycle(self):
        """Check opmodes of all power supplies ar Cycle."""
        return self._check('OpMode-Sel', _PSConst.OpMode.Cycle)

    def check_opmode_rmpwfm(self):
        """Check opmodes of all power supplies ar RmpWfm."""
        return self._check('OpMode-Sel', _PSConst.OpMode.RmpWfm)

    def check_intlksoft(self):
        """Check if software interlocks are reset."""
        return self._check('IntlkSoft-Mon', 0)

    def check_intlkhard(self):
        """Check if hardware interlocks are reset."""
        return self._check('IntlkHard-Mon', 0)

    # --- private methods ---

    def _get_manames(self):
        self._manames = _MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})

    def _define_properties(self, prefix, connection_callback, callback):
        p = prefix
        properties = []
        for maname in self._manames:
            properties.append(
                _EpicsProperty(maname + ':PwrState-Sel', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':OpMode-Sel', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':WfmData-SP', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':IntlkSoft-Mon', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':IntlkHard-Mon', p,
                               connection_callback=connection_callback,
                               callback=callback))
        return properties

    def _command(self, prop, value, timeout):
        """Exec command for all power supplies."""
        setpoints = dict()
        for maname in self.manames:
            name = maname + ':' + prop
            setpoints[name] = value
        return self.set_setpoints_check(setpoints, timeout)

    def _check(self, prop, value):
        """Check a prop of all power supplies for a value."""
        for maname in self.manames:
            name = maname + ':' + prop
            if not self.get_readback(name) == value:
                return False
        return True


class ConnRF(_EpicsPropsList):
    """RF connector class."""

    class Const(_cutil.Const):
        """Properties names."""

        DevName = 'BO-05D:RF-LLRF'
        Rmp_Enbl = DevName + ':RmpEnbl-Sel'
        Rmp_Ts1 = DevName + ':RmpTs1-SP'
        Rmp_Ts2 = DevName + ':RmpTs2-SP'
        Rmp_Ts3 = DevName + ':RmpTs3-SP'
        Rmp_Ts4 = DevName + ':RmpTs4-SP'
        Rmp_IncTs = DevName + ':RmpIncTs-SP'
        Rmp_VoltBot = DevName + ':RmpVoltBot-SP'
        Rmp_VoltTop = DevName + ':RmpVoltTop-SP'
        Rmp_PhsBot = DevName + ':RmpPhsBot-SP'
        Rmp_PhsTop = DevName + ':RmpPhsTop-SP'
        Rmp_Intlk = DevName + ':Intlk-Mon'
        Rmp_RmpReady = DevName + ':RmpReady-Mon'

    def __init__(self, ramp_config=None, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        self._ramp_config = ramp_config
        properties = self._define_properties(prefix, connection_callback,
                                             callback)
        super().__init__(properties)

    def get_ramp_config(self, ramp_config):
        """Receive BoosterRamp configuration."""
        self._ramp_config = ramp_config

    # --- RF commands ---

    def cmd_ramping_enable(self, timeout=_TIMEOUT_DFLT):
        """Turn RF ramping enable."""
        sp = {ConnRF.Const.Rmp_Enbl: ConnRF.Const.DsblEnbl.Enbl}
        return self.set_setpoints_check(sp, timeout)

    def cmd_ramping_disable(self, timeout=_TIMEOUT_DFLT):
        """Turn RF ramping disable."""
        sp = {ConnRF.Const.Rmp_Enbl: ConnRF.Const.STATE_DISBL}
        return self.set_setpoints_check(sp, timeout)

    def cmd_config_ramp(self, timeout=_TIMEOUT_DFLT):
        """Apply ramp_config values to RF subsystem."""
        sp = dict()
        c = ConnRF.Const
        sp[c.Rmp_Ts1] = self._ramp_config.rf_ramp_bottom_duration
        sp[c.Rmp_Ts2] = self._ramp_config.rf_ramp_rampup_duration
        sp[c.Rmp_Ts3] = self._ramp_config.rf_ramp_top_duration
        sp[c.Rmp_Ts4] = self._ramp_config.rf_ramp_rampdown_duration
        sp[c.Rmp_IncTs] = self._ramp_config.rf_ramp_rampinc_duration
        sp[c.Rmp_VoltBot] = self._ramp_config.rf_ramp_bottom_voltage
        sp[c.Rmp_VoltTop] = self._ramp_config.rf_ramp_top_voltage
        sp[c.Rmp_PhsBot] = self._ramp_config.rf_ramp_bottom_phase
        sp[c.Rmp_PhsTop] = self._ramp_config.rf_ramp_top_phase
        return self.set_setpoints_check(sp, timeout)

    # --- RF checks ---

    def check_ramping_enable(self):
        """Check ramping enable."""
        rb = {ConnRF.Const.Rmp_Enbl: ConnRF.Const.DsblEnbl.Enbl}
        return self._check(rb)

    def check_config_ramp(self):
        """Check if configured to ramp."""
        rb = dict()
        rb[ConnRF.Const.Rmp_Ts1] = self._ramp_config.rf_ramp_bottom_duration
        rb[ConnRF.Const.Rmp_Ts2] = self._ramp_config.rf_ramp_rampup_duration
        rb[ConnRF.Const.Rmp_Ts3] = self._ramp_config.rf_ramp_top_duration
        rb[ConnRF.Const.Rmp_Ts4] = self._ramp_config.rf_ramp_rampdown_duration
        rb[ConnRF.Const.Rmp_IncTs] = self._ramp_config.rf_ramp_rampinc_duration
        rb[ConnRF.Const.Rmp_VoltBot] = self._ramp_config.rf_ramp_bottom_voltage
        rb[ConnRF.Const.Rmp_VoltTop] = self._ramp_config.rf_ramp_top_voltage
        rb[ConnRF.Const.Rmp_PhsBot] = self._ramp_config.rf_ramp_bottom_phase
        rb[ConnRF.Const.Rmp_PhsTop] = self._ramp_config.rf_ramp_top_phase
        return self._check(rb)

    def check_intlk(self):
        """Check if hardware interlocks are reset."""
        return self._check({ConnRF.Const.Rmp_Intlk: 0})

    def check_rmpready(self):
        """Check if ramp increase was concluded."""
        return self._check({ConnRF.Const.Rmp_RmpReady: 1})

    # --- private methods ---

    def _define_properties(self, prefix, connection_callback, callback):
        c = ConnRF.Const
        propty2defaultvalue = {
            c.Rmp_Enbl: ConnRF.Const.DsblEnbl.Enbl,
            c.Rmp_Ts1: _rutil.DEFAULT_RF_RAMP_BOTTOM_DURATION,
            c.Rmp_Ts2: _rutil.DEFAULT_RF_RAMP_RAMPUP_DURATION,
            c.Rmp_Ts3: _rutil.DEFAULT_RF_RAMP_TOP_DURATION,
            c.Rmp_Ts4: _rutil.DEFAULT_RF_RAMP_RAMPDOWN_DURATION,
            c.Rmp_IncTs: _rutil.DEFAULT_RF_RAMP_RAMPINC_DURATION,
            c.Rmp_VoltBot: _rutil.DEFAULT_RF_RAMP_BOTTOM_VOLTAGE,
            c.Rmp_VoltTop: _rutil.DEFAULT_RF_RAMP_TOP_VOLTAGE,
            c.Rmp_PhsBot: _rutil.DEFAULT_RF_RAMP_BOTTOM_PHASE,
            c.Rmp_PhsTop: _rutil.DEFAULT_RF_RAMP_TOP_PHASE,
            c.Rmp_Intlk: None,
            c.Rmp_RmpReady: None}

        properties = list()
        for propty, default_value in propty2defaultvalue.items():
            properties.append(
                _EpicsProperty(propty, prefix, default_value,
                               connection_callback=connection_callback,
                               callback=callback))
        return properties

    def _check(self, readbacks):
        for name, value in readbacks.items():
            if value is None:
                continue
            if not self.get_readback(name) == value:
                return False
        return True


class ConnSOFB(_EpicsPropsList):
    """SOFB connector class."""

    IOC_Prefix = 'BO-Glob:AP-SOFB'

    def __init__(self, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        properties = self._define_properties(prefix, connection_callback,
                                             callback)
        super().__init__(properties)

    def get_deltakicks(self):
        """Get CH and CV delta kicks calculated by SOFB."""
        bo_sofb_db = _SOFBRings(acc='BO')
        rb = self.readbacks
        ch_dkicks = rb[ConnSOFB.IOC_Prefix + ':DeltaKickCH']
        ch_names = bo_sofb_db.CH_NAMES

        cv_dkicks = rb[ConnSOFB.IOC_Prefix + ':DeltaKickCV']
        cv_names = bo_sofb_db.CV_NAMES

        corrs2dkicks_dict = dict()
        for idx in range(len(ch_names)):
            corrs2dkicks_dict[ch_names[idx]] = ch_dkicks[idx]
        for idx in range(len(cv_names)):
            corrs2dkicks_dict[cv_names[idx]] = cv_dkicks[idx]
        return corrs2dkicks_dict

    def _define_properties(self, prefix, connection_callback, callback):
        properties = list()
        for ppty in ['DeltaKickCH-Mon', 'DeltaKickCV-Mon']:
            properties.append(
                _EpicsProperty(ConnSOFB.IOC_Prefix + ':' + ppty, prefix,
                               connection_callback=connection_callback,
                               callback=callback))
        return properties
