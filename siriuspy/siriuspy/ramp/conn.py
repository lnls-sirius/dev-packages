"""Module with connector classes.

This module implements connector classes responsible for communications with
magnet soft IOcs, ConfigDB service and orbit, tune and chromacity correction
IOCs.
"""

from siriuspy import envars as _envars
from siriuspy.epics.properties import \
    EpicsProperty as _EpicsProperty, \
    EpicsPropertiesList as _EpicsPropertiesList
from siriuspy.servconf.srvconfig import ConnConfigService as _ConnConfigService


class ConnConfig_BORamp(_ConnConfigService):
    """ConifgurationService for BO ramp configs."""

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_ramp', url=url)


class ConnConfig_BONormalized(_ConnConfigService):
    """ConifgurationService for BO normalized configs."""

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_normalized', url=url)


class ConnMagnet(_EpicsPropertiesList):
    """Magnet Connector Class."""

    def __init__(self, ramp_config):
        """Initialize object."""
        self._ramp_config = ramp_config
        pass


class ConnTiming(_EpicsPropertiesList):
    """Timing Connector Class."""

    class Const:
        """PV names."""

        EVG_ContinuousEvt = 'AS-Glob:TI-EVG:ContinuousEvt'
        EVG_DevEnbl = 'AS-Glob:TI-EVG:DevEnbl'
        EVG_ACEnbl = 'AS-Glob:TI-EVG:ACEnbl'
        EVG_Evt01Mode = 'AS-Glob:TI-EVG:Evt01Mode'
        EVR1_DevEnbl = 'AS-Glob:TI-EVR-1:DevEnbl'
        EVR1_OTP08State = 'AS-Glob:TI-EVR-1:OTP08State'
        EVR1_OTP08Polarity = 'AS-Glob:TI-EVR-1:OTP08Polarity'

        EVG_ACDiv = 'AS-Glob:TI-EVG:ACDiv'
        EVG_RFDiv = 'AS-Glob:TI-EVG:RFDiv'
        EVR1_OTP08Width = 'AS-Glob:TI-EVR-1:OTP08Width'
        EVR1_OTP08Evt = 'AS-Glob:TI-EVR-1:OTP08Evt'
        EVR1_OTP08Pulses = 'AS-Glob:TI-EVR-1:OTP08Pulses'

    def __init__(self, ramp_config, prefix=''):
        """Init."""
        self._define_properties(prefix)
        self._ramp_config = ramp_config

    def select_ramp(self, timeout):
        """Select ramp timing mode."""
        # reset and check
        status = self.reset_check(timeout)
        if not status:
            return status
        # set ramp
        c = ConnTiming.Const
        wfm_nrpoints = self._ramp_config.ramp_dipole_wfm_nrpoints
        setpoints = {
            c.EVG_Evt01Mode:  'Continuous',
            c.EVG_ContinuousEvt:  1,
            c.EVR1_OTP08Pulses:  wfm_nrpoints, }
        return self.set_setpoints_check(self, setpoints, timeout)

    def select_cycle(self, timeout):
        """Select cycle timing mode."""
        # reset and check
        status = self.reset_check(timeout)
        if not status:
            return status
        # set cycle
        c = ConnTiming.Const
        setpoints = {
            c.EVR1_OTP08Pulses:  1,
            c.EVG_Evt01Mode:  'External', }
        return self.set_setpoints_check(self, setpoints, timeout)

    def _define_properties(self, prefix):
        c = ConnTiming.Const
        p = prefix
        properties = (
            _EpicsProperty(c.EVG_ContinuousEvt, '-Sel', '-Sts', p, 0),
            _EpicsProperty(c.EVG_DevEnbl, '-Sel', '-Sts', p, 1),
            _EpicsProperty(c.EVG_ACEnbl, '-Sel', '-Sts', p, 1),
            _EpicsProperty(c.EVG_Evt01Mode, '-Sel', '-Sts', p, 'External'),
            _EpicsProperty(c.EVR1_DevEnbl, '-Sel', '-Sts', p, 1),
            _EpicsProperty(c.EVR1_OTP08State, '-Sel', '-Sts', p, 1),
            _EpicsProperty(c.EVR1_OTP08Polarity, '-Sel', '-Sts', p, 0),
            _EpicsProperty(c.EVG_ACDiv, '-SP', '-RB', p, 30),
            _EpicsProperty(c.EVG_RFDiv, '-SP', '-RB', p, 4),
            _EpicsProperty(c.EVR1_OTP08Width, '-SP', '-RB', p, 7000),
            _EpicsProperty(c.EVR1_OTP08Evt, '-SP', '-RB', p, 1),
            _EpicsProperty(c.EVR1_OTP08Pulses, '-SP', '-RB', p, 1),)
        super().__init__(properties)


# class ConnMagnet(_Conn):
#     """Magnet Connector Class."""
#
#     def __init__(self,
#                  use_vaca=False,
#                  vaca_prefix=None):
#         """Init method."""
#         self._use_vaca = use_vaca
#         self._vaca_prefix = vaca_prefix
#         self._magnets = {}
#
#     def wfm_send(self, maname, wfm_current):
#         """Send current waveform to magnet power supply."""
#         if maname not in self._magnets:
#             self._create_magnet_conn(maname)
#         magnet = self._magnets[maname]
#         if not magnet.connected:
#             raise Exception(
#                     'Not connected to power supply of {}!'.format(maname))
#         else:
#             magnet.wfmdata_sp = wfm_current
#
#     def wfm_recv(self, maname):
#         """Receive current waveform to magnet power supply."""
#         if maname not in self._magnets:
#             self._create_magnet_conn(maname)
#         magnet = self._magnets[maname]
#         if not magnet.connected:
#             raise Exception(
#                 'Not connected to power supply of {}!'.format(maname))
#         else:
#             wfm_current = magnet.wfmdata_rb
#             return wfm_current
#
#     def _create_magnet_conn(self, maname):
#         self._pses[maname] = _MagnetFactory(maname=maname,
#                                             use_vaca=self._use_vaca,
#                                             vaca_prefix=self._vaca_prefix,
#                                             lock=False,
#                                             )
#
#
# class ConnOrbit(_Conn):
#     """Connector class to interact with SOFT IOCs."""
#
#     pass
