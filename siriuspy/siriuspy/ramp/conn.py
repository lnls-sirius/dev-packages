"""Module with connector classes.

This module implements connector classes responsible for communications with
magnet soft IOcs, ConfigDB service and orbit IOCs.
"""

import time as _time

from siriuspy import envars as _envars
from siriuspy.epics.properties import EpicsProperty as _EpicsProperty
from siriuspy.epics.properties import EpicsPropertiesList as _EpicsPropsList
from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriuspy.servconf.srvconfig import ConnConfigService as _ConnConfigService
from siriuspy.ramp import util as _rutil
from siriuspy.csdevice.orbitcorr import get_consts as _get_SOFB_consts
from siriuspy.search.ma_search import MASearch as _MASearch


_prefix = _envars.vaca_prefix
_PWRSTATE_ON_DELAY = 1.4
_PWRSTATE_OFF_DELAY = 0.8
_TIMEOUT_DFLT = 0.5


class ConnConfig_BORamp(_ConnConfigService):
    """ConfigurationService connector class for BO ramp configs."""

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_ramp', url=url)


class ConnConfig_BONormalized(_ConnConfigService):
    """ConfigurationService connector for BO normalized configs."""

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_normalized', url=url)


class ConnTiming(_EpicsPropsList):
    """Timing connector class."""

    class Const:
        """Properties names."""

        EVG_ContinuousEvt = 'AS-Glob:TI-EVG:ContinuousEvt'
        EVG_ACDiv = 'AS-Glob:TI-EVG:ACDiv'
        EVG_DevEnbl = 'AS-Glob:TI-EVG:DevEnbl'
        EVG_ACEnbl = 'AS-Glob:TI-EVG:ACEnbl'
        EVG_Evt01Mode = 'AS-Glob:TI-EVG:Evt01Mode'
        EVG_RFDiv = 'AS-Glob:TI-EVG:RFDiv'

        EVG_Evt01ExtTrig = 'AS-Glob:TI-EVG:Evt01ExtTrig'

        EVR1_DevEnbl = 'AS-Glob:TI-EVR-1:DevEnbl'
        EVR1_OTP08State = 'AS-Glob:TI-EVR-1:OTP08State'
        EVR1_OTP08Polarity = 'AS-Glob:TI-EVR-1:OTP08Polarity'
        EVR1_OTP08Width = 'AS-Glob:TI-EVR-1:OTP08Width'
        EVR1_OTP08Evt = 'AS-Glob:TI-EVR-1:OTP08Evt'
        EVR1_OTP08Pulses = 'AS-Glob:TI-EVR-1:OTP08Pulses'

        # Evt01Modes
        MODE_DISABLE = 0
        MODE_CONTINUOUS = 1
        MODE_INJECTION = 2
        MODE_EXTERNAL = 3

        # State Enbl|Dsbl
        STATE_DISBL = 0
        STATE_ENBL = 1

        # Polarity
        STATE_NORMAL = 0
        STATE_INVERSE = 1

    def __init__(self, ramp_config=None, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        self._ramp_config = ramp_config
        properties = self._define_properties(prefix, connection_callback,
                                             callback)
        super().__init__(properties)

    # --- timing mode selection commands ---

    def wait_EVRs(self):
        """Return only after EVRs are done generating their pulse trains."""
        # NOTE: there is no timing PV that be monitored for this.
        # current implementation just waits for maximum ramp duration...
        _time.sleep(0.5)

    def cmd_init(self, timeout=_TIMEOUT_DFLT):
        """Initialize timing properties."""
        c = ConnTiming.Const
        setpoints = self.default
        order = [c.EVG_ContinuousEvt, c.EVG_DevEnbl, c.EVG_ACDiv, c.EVG_ACEnbl,
                 c.EVG_RFDiv, c.EVG_Evt01Mode, c.EVR1_DevEnbl,
                 c.EVR1_OTP08State, c.EVR1_OTP08Width, c.EVR1_OTP08Evt,
                 c.EVR1_OTP08Polarity, c.EVR1_OTP08Pulses]
        return self.set_setpoints_check(setpoints, timeout, order)

    def cmd_select_stop(self, timeout=_TIMEOUT_DFLT):
        """Stop pulsing timing."""
        c = ConnTiming.Const
        setpoints = {c.EVG_Evt01Mode: c.MODE_DISABLE,
                     c.EVG_ContinuousEvt: c.STATE_DISBL}
        order = [c.EVG_Evt01Mode, c.EVG_ContinuousEvt]
        return self.set_setpoints_check(setpoints, timeout, order)

    def cmd_select_ramp(self, timeout=_TIMEOUT_DFLT):
        """Select ramp timing mode."""
        if self._ramp_config is None:
            return False
        c = ConnTiming.Const
        wfm_nrpoints = self._ramp_config.ps_ramp_wfm_nrpoints
        setpoints = self.default
        setpoints.update(
            {c.EVR1_OTP08Pulses: wfm_nrpoints,
             c.EVG_Evt01Mode: c.MODE_CONTINUOUS,
             c.EVG_ContinuousEvt: c.STATE_ENBL}
        )
        order = [c.EVG_DevEnbl, c.EVG_ACDiv, c.EVG_ACEnbl, c.EVG_RFDiv,
                 c.EVR1_DevEnbl, c.EVR1_OTP08State, c.EVR1_OTP08Width,
                 c.EVR1_OTP08Evt, c.EVR1_OTP08Polarity,
                 c.EVR1_OTP08Pulses, c.EVG_Evt01Mode, c.EVG_ContinuousEvt]
        return self.set_setpoints_check(setpoints, timeout, order)

    def cmd_select_cycle(self, timeout=_TIMEOUT_DFLT):
        """Select cycle timing mode."""
        c = ConnTiming.Const
        setpoints = self.default
        setpoints.update({c.EVG_Evt01Mode: c.MODE_EXTERNAL,
                          c.EVR1_OTP08Pulses: 1})
        order = [c.EVG_ContinuousEvt, c.EVG_DevEnbl, c.EVG_ACDiv, c.EVG_ACEnbl,
                 c.EVG_RFDiv, c.EVR1_DevEnbl, c.EVR1_OTP08State,
                 c.EVR1_OTP08Width, c.EVR1_OTP08Evt, c.EVR1_OTP08Polarity,
                 c.EVR1_OTP08Pulses, c.EVG_Evt01Mode]
        return self.set_setpoints_check(setpoints, timeout, order)

    def cmd_pulse(self, timeout=_TIMEOUT_DFLT):
        """Pulse timing."""
        c = ConnTiming.Const
        setpoints = {c.EVG_Evt01ExtTrig: 1}
        return self.set_setpoints_check(setpoints, timeout)

    # --- timing mode checks ---

    def check_ramp(self):
        """Check if in ramp state."""
        c = ConnTiming.Const
        wfm_nrpoints = self._ramp_config.ps_ramp_wfm_nrpoints
        readbacks = dict()
        readbacks[c.EVG_Evt01Mode] = c.MODE_CONTINUOUS
        readbacks[c.EVG_ContinuousEvt] = c.STATE_ENBL
        readbacks[c.EVR1_OTP08Pulses] = wfm_nrpoints
        return self._check(readbacks)

    def check_cycle(self):
        """Check if in cycle state."""
        c = ConnTiming.Const
        readbacks = dict()
        readbacks[c.EVG_Evt01Mode] = c.MODE_EXTERNAL
        readbacks[c.EVR1_OTP08Pulses] = 1
        return self._check(readbacks)

    # --- private methods ---

    def _define_properties(self, prefix, connection_callback, callback):
        c = ConnTiming.Const
        p = prefix
        properties = (
            _EpicsProperty(c.EVG_ContinuousEvt, '-Sel', '-Sts', p,
                           c.STATE_DISBL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVG_DevEnbl, '-Sel', '-Sts', p, c.STATE_ENBL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVG_ACEnbl, '-Sel', '-Sts', p, c.STATE_ENBL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVG_Evt01Mode, '-Sel', '-Sts', p,
                           c.MODE_EXTERNAL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVG_Evt01ExtTrig, '-Cmd', '-Cmd', p, None,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVR1_DevEnbl, '-Sel', '-Sts', p, c.STATE_ENBL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVR1_OTP08State, '-Sel', '-Sts', p, c.STATE_ENBL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVR1_OTP08Polarity, '-Sel', '-Sts',
                           p, c.STATE_NORMAL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVG_ACDiv, '-SP', '-RB', p, 30,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVG_RFDiv, '-SP', '-RB', p, 4,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVR1_OTP08Width, '-SP', '-RB', p, 7000,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVR1_OTP08Evt, '-SP', '-RB', p, 1,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.EVR1_OTP08Pulses, '-SP', '-RB', p, _MAX_WFMSIZE,
                           connection_callback=connection_callback,
                           callback=callback),)
        return properties

    def _check(self, readbacks):
        rb = self.default
        rb.update(readbacks)
        for name, value in rb.items():
            if value is None:
                continue
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

    # --- power supplies commands ---

    def cmd_pwrstate_on(self, timeout=_PWRSTATE_ON_DELAY):
        """Turn all power supplies on."""
        return self._command('PwrState', _PSConst.PwrState.On, timeout)

    def cmd_pwrstate_off(self, timeout=_PWRSTATE_OFF_DELAY):
        """Turn all power supplies off."""
        return self._command('PwrState', _PSConst.PwrState.Off, timeout)

    def cmd_opmode_slowref(self, timeout=_TIMEOUT_DFLT):
        """Select SlowRef opmode for all power supplies."""
        return self._command('OpMode', _PSConst.OpMode.SlowRef, timeout)

    def cmd_opmode_cycle(self, timeout=_TIMEOUT_DFLT):
        """Select Cycle opmode for all power supplies."""
        return self._command('OpMode', _PSConst.OpMode.Cycle, timeout)

    def cmd_opmode_rmpwfm(self, timeout=_TIMEOUT_DFLT):
        """Select RmpWfm opmode for all power supplies."""
        return self._command('OpMode', _PSConst.OpMode.RmpWfm, timeout)

    def cmd_wfmdata(self, timeout=_TIMEOUT_DFLT):
        """Set wfmdata of all powersupplies."""
        if self._ramp_config is None:
            return False
        setpoints = dict()
        for maname in self.manames:
            # get value (wfmdata)
            wf = self._ramp_config.ps_waveform_get(maname)
            value = wf.currents
            name = maname + ':' + 'WfmData'
            setpoints[name] = value
        return self.set_setpoints_check(setpoints, timeout)

    # --- power supplies checks ---

    def check_pwrstate_on(self):
        """Check pwrstates of all power supplies are On."""
        return self._check('PwrState', _PSConst.PwrState.On)

    def check_opmode_slowref(self):
        """Check opmodes of all power supplies ar SlowRef."""
        return self._check('OpMode', _PSConst.OpMode.SlowRef)

    def check_opmode_cycle(self):
        """Check opmodes of all power supplies ar Cycle."""
        return self._check('OpMode', _PSConst.OpMode.Cycle)

    def check_opmode_rmpwfm(self):
        """Check opmodes of all power supplies ar RmpWfm."""
        return self._check('OpMode', _PSConst.OpMode.RmpWfm)

    def check_intlksoft(self):
        """Check if software interlocks are reset."""
        return self._check('IntlkSoft', 0)

    def check_intlkhard(self):
        """Check if hardware interlocks are reset."""
        return self._check('IntlkHard', 0)

    def check_rmpready(self):
        """Check if ramp increase was concluded."""
        return self._check('RmpReady', 1)

    # --- private methods ---

    def _get_manames(self):
        self._manames = _MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})

    def _define_properties(self, prefix, connection_callback, callback):
        p = prefix
        properties = []
        for maname in self._manames:
            properties.append(
                _EpicsProperty(maname + ':PwrState', '-Sel', '-Sts', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':OpMode', '-Sel', '-Sts', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':WfmData', '-SP', '-RB', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':IntlkSoft', '-Mon', '-Mon', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':IntlkHard', '-Mon', '-Mon', p,
                               connection_callback=connection_callback,
                               callback=callback))
            properties.append(
                _EpicsProperty(maname + ':RmpReady', '-Mon', '-Mon', p,
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

    class Const:
        """Properties names."""

        DevName = 'BO-05D:RF-LLRF'
        Rmp_Enbl = DevName + ':RmpEnbl'
        Rmp_Ts1 = DevName + ':RmpTs1'
        Rmp_Ts2 = DevName + ':RmpTs2'
        Rmp_Ts3 = DevName + ':RmpTs3'
        Rmp_Ts4 = DevName + ':RmpTs4'
        Rmp_IncTs = DevName + ':RmpIncTs'
        Rmp_VoltBot = DevName + ':RmpVoltBot'
        Rmp_VoltTop = DevName + ':RmpVoltTop'
        Rmp_PhsBot = DevName + ':RmpPhsBot'
        Rmp_PhsTop = DevName + ':RmpPhsTop'
        Rmp_Intlk = DevName + ':Intlk'
        Rmp_RmpReady = DevName + ':RmpReady'

        # State Enbl|Dsbl
        STATE_DISBL = 0
        STATE_ENBL = 1

    def __init__(self, ramp_config=None, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        self._ramp_config = ramp_config
        properties = self._define_properties(prefix, connection_callback,
                                             callback)
        super().__init__(properties)

    # --- RF commands ---

    def cmd_ramping_enable(self, timeout=_TIMEOUT_DFLT):
        """Turn RF ramping enable."""
        sp = {ConnRF.Const.Rmp_Enbl: ConnRF.Const.STATE_ENBL}
        return self.set_setpoints_check(sp, timeout)

    def cmd_ramping_disable(self, timeout=_TIMEOUT_DFLT):
        """Turn RF ramping disable."""
        sp = {ConnRF.Const.Rmp_Enbl: ConnRF.Const.STATE_DISBL}
        return self.set_setpoints_check(sp, timeout)

    def cmd_config_ramp(self, timeout=_TIMEOUT_DFLT):
        """Configure RF to ramping."""
        sp = dict()
        sp[ConnRF.Const.Rmp_Ts1] = self._ramp_config.rf_ramp_bottom_duration
        sp[ConnRF.Const.Rmp_Ts2] = self._ramp_config.rf_ramp_rampup_duration
        sp[ConnRF.Const.Rmp_Ts3] = self._ramp_config.rf_ramp_top_duration
        sp[ConnRF.Const.Rmp_Ts4] = self._ramp_config.rf_ramp_rampdown_duration
        sp[ConnRF.Const.Rmp_IncTs] = self._ramp_config.rf_ramp_rampinc_duration
        sp[ConnRF.Const.Rmp_VoltBot] = self._ramp_config.rf_ramp_bottom_voltage
        sp[ConnRF.Const.Rmp_VoltTop] = self._ramp_config.rf_ramp_top_voltage
        sp[ConnRF.Const.Rmp_PhsBot] = self._ramp_config.rf_ramp_bottom_phase
        sp[ConnRF.Const.Rmp_PhsTop] = self._ramp_config.rf_ramp_top_phase
        return self.set_setpoints_check(sp, timeout)

    # --- RF checks ---

    def check_ramping_enable(self):
        """Check ramping enable."""
        rb = {ConnRF.Const.Rmp_Enbl: ConnRF.Const.STATE_ENBL}
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
        properties = (
            _EpicsProperty(c.Rmp_Enbl, '-Sel', '-Sts', prefix,
                           ConnRF.Const.STATE_ENBL,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_Ts1, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_BOTTOM_DURATION,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_Ts2, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_RAMPUP_DURATION,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_Ts3, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_TOP_DURATION,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_Ts4, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_RAMPDOWN_DURATION,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_IncTs, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_RAMPINC_DURATION,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_VoltBot, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_BOTTOM_VOLTAGE,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_VoltTop, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_TOP_VOLTAGE,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_PhsBot, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_BOTTOM_PHASE,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_PhsTop, '-SP', '-RB', prefix,
                           _rutil.DEFAULT_RF_RAMP_TOP_PHASE,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_Intlk, '-Mon', '-Mon', prefix,
                           connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(c.Rmp_RmpReady, '-Mon', '-Mon', prefix,
                           connection_callback=connection_callback,
                           callback=callback)
            )
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

    def __init__(self, ramp_config=None, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        self._ramp_config = ramp_config
        properties = self._define_properties(prefix, connection_callback,
                                             callback)
        super().__init__(properties)

    def get_kicks(self):
        """Get CH and CV kicks calculated by SOFB."""
        rb = self.readbacks
        cv_kicks = rb[ConnSOFB.IOC_Prefix + ':KicksCV']
        cv_names = _get_SOFB_consts.cv_names

        ch_kicks = rb[ConnSOFB.IOC_Prefix + ':KicksCH']
        ch_names = _get_SOFB_consts.ch_names

        corrs2kicks_dict = dict()
        for idx in range(len(cv_names)):
            corrs2kicks_dict[cv_names[idx]] = cv_kicks[idx]
        for idx in range(len(ch_names)):
            corrs2kicks_dict[ch_names[idx]] = ch_kicks[idx]
        return corrs2kicks_dict

    def _define_properties(self, prefix, connection_callback, callback):
        properties = (
            _EpicsProperty(ConnSOFB.IOC_Prefix + ':KicksCH', '-Mon', '-Mon',
                           prefix, connection_callback=connection_callback,
                           callback=callback),
            _EpicsProperty(ConnSOFB.IOC_Prefix + ':KicksCV', '-Mon', '-Mon',
                           prefix, connection_callback=connection_callback,
                           callback=callback),
            )
        return properties
