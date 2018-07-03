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


_prefix = _envars.vaca_prefix


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
        self._define_properties(prefix, connection_callback, callback)

    # --- timing mode selection commands ---

    def wait_EVRs(self):
        """Return only after EVRs are done generating their pulse trains."""
        # NOTE: there is no timing PV that be monitored for this.
        # current implementation just waits for maximum ramp duration...
        _time.sleep(0.5)

    def cmd_init(self, timeout):
        """Initialize timing properties."""
        setpoints = self.default
        return self.set_setpoints_check(self, setpoints, timeout)

    def cmd_select_stop(self, timeout):
        """Stop pulsing timing."""
        c = ConnTiming.Const
        setpoints = self.default
        setpoints.update(
            {c.EVG_Evt01Mode: c.MODE_DISABLE,
             c.EVG_ContinuousEvt: c.STATE_DISBL, }
        )
        return self.set_setpoints_check(self, setpoints, timeout)

    def cmd_select_ramp(self, timeout):
        """Select ramp timing mode."""
        if self._ramp_config is None:
            return False
        c = ConnTiming.Const
        setpoints = self.default
        wfm_nrpoints = self._ramp_config.ramp_dipole_wfm_nrpoints
        setpoints.update(
            {c.EVG_Evt01Mode: c.MODE_CONTINUOUS,
             c.EVG_ContinuousEvt: c.STATE_ENBL,
             c.EVR1_OTP08Pulses: wfm_nrpoints, }
        )
        return self.set_setpoints_check(self, setpoints, timeout)

    def cmd_select_cycle(self, timeout):
        """Select cycle timing mode."""
        c = ConnTiming.Const
        setpoints = self.default
        setpoints.update(
            {c.EVG_Evt01Mode: c.MODE_EXTERNAL,
             c.EVR1_OTP08Pulses: 1, }
        )
        return self.set_setpoints_check(self, setpoints, timeout)

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
        super().__init__(properties)


class ConnMagnets(_EpicsPropsList):
    """Magnets connector class."""

    def __init__(self, ramp_config=None, prefix=_prefix,
                 connection_callback=None, callback=None):
        """Init."""
        self._ramp_config = ramp_config
        self._get_manames()
        self._define_properties(prefix, connection_callback, callback)

    @property
    def manames(self):
        """Return manames."""
        return self._manames

    # --- power supplies commands ---

    def cmd_pwrstate_on(self, timeout):
        """Turn all power supplies on."""
        return self._command('PwrState', _PSConst.PwrState.On, timeout)

    def cmd_pwrstate_off(self, timeout):
        """Turn all power supplies off."""
        return self._command('PwrState', _PSConst.PwrState.Off, timeout)

    def cmd_opmode_slowref(self, timeout):
        """Select SlowRef opmode for all power supplies."""
        return self._command('OpMode', _PSConst.OpMode.SlowRef, timeout)

    def cmd_opmode_cycle(self, timeout):
        """Select Cycle opmode for all power supplies."""
        return self._command('OpMode', _PSConst.OpMode.Cycle, timeout)

    def cmd_opmode_rmpwfm(self, timeout):
        """Select RmpWfm opmode for all power supplies."""
        return self._command('OpMode', _PSConst.OpMode.RmpWfm, timeout)

    def cmd_wfmdata(self, timeout):
        """Set wfmdata of all powersupplies."""
        if self._ramp_config is None:
            return False
        setpoints = dict()
        for maname in self.manames:
            # get value (wfmdata)
            wf = self._ramp_config.waveform_get(maname)
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

    # --- private methods ---

    def _get_manames(self):
        cs = _ConfigService()
        tpl = cs.get_config_type_template('bo_normalized')
        self._manames = sorted(tpl.keys())

    def _define_properties(self, prefix, connection_callback, callback):
        p = prefix
        props = []
        for maname in self._manames:
            props.append(
                _EpicsProperty(maname + ':PwrState', '-Sel', '-Sts', p,
                               connection_callback=connection_callback,
                               callback=callback))
            props.append(
                _EpicsProperty(maname + ':OpMode', '-Sel', '-Sts', p,
                               connection_callback=connection_callback,
                               callback=callback))
            props.append(
                _EpicsProperty(maname + ':WfmData', '-SP', '-RB', p,
                               connection_callback=connection_callback,
                               callback=callback))
        super().__init__(props)

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
