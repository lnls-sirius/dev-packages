"""Module with connector classes.

This module implements connector classes responsible for communications with
magnet soft IOcs, ConfigDB service and orbit, tune and chromacity correction
IOCs.
"""

import time as _time
import epics as _epics
from siriuspy import envars as _envars
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


class ConnEpics:
    """Conector to handle Booster Epics communication."""

    def __init__(self, prefix, pvnames_sp, conv_sp_rb=None):
        """Initialize object."""
        self._prefix = prefix
        if conv_sp_rb is None:
            conv_sp_rb = (('-SP', '-RB'), ('-Sel', '-Sts'))
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        self._sp2rb = dict()
        for pvname_sp in pvnames_sp:
            pvname_sp = prefix + pvname_sp
            pvname_rb = pvname_sp
            for sp, rb in conv_sp_rb:
                pvname_rb = pvname_rb.replace(sp, rb)
            self._sp2rb[pvname_sp] = pvname_rb
            self._pvs_sp[pvname_sp] = _epics.PV(pvname_sp)
            self._pvs_rb[pvname_rb] = _epics.PV(pvname_rb)

    def connected(self):
        """Return if all pvs are connected."""
        for pv in self._pvs_sp.values():
            if not pv.connected:
                return False
        return True

    def set_pvs(self, pvnames_sp, setpoints, timeout):
        """Set pv (SP|Sel) to value and check correspondent (RB|Sts)."""
        if not self.connected:
            return False
        if not isinstance(pvnames_sp, (list, tuple)):
            pvnames_sp = (pvnames_sp,)
            setpoints = (setpoints,)

        for i in range(len(pvnames_sp)):
            self._pvs_sp[self._prefix + pvnames_sp[i]].value = setpoints[i]

        t0 = _time.time()
        while True:
            finished = True
            for i in range(len(pvnames_sp)):
                pvname_rb = self._sp2rb[self._prefix + pvnames_sp[i]]
                if self._pvs_rb[pvname_rb].value != setpoints[i]:
                    finished = False
                    break
            if finished or _time.time()-t0 > timeout:
                break
        return finished


class ConnMagnet(ConnEpics):
    """Magnet Connector Class."""

    def __init__(self, ramp_config):
        """Initialize object."""
        self._ramp_config = ramp_config
        pass


class ConnTiming(ConnEpics):
    """Timing Connector Class."""

    class Const:
        """PV names."""

        EVG_ContinuousEvt_Sel = 'AS-Glob:TI-EVG:ContinuousEvt-Sel'
        EVG_DevEnbl_Sel = 'AS-Glob:TI-EVG:DevEnbl-Sel'
        EVG_ACDiv_SP = 'AS-Glob:TI-EVG:ACDiv-SP'
        EVG_ACEnbl_Sel = 'AS-Glob:TI-EVG:ACEnbl-Sel'
        EVG_RFDiv_SP = 'AS-Glob:TI-EVG:RFDiv-SP'
        EVG_Evt01Mode_Sel = 'AS-Glob:TI-EVG:Evt01Mode-Sel'
        EVR1_DevEnbl_Sel = 'AS-Glob:TI-EVR-1:DevEnbl-Sel'
        EVR1_OTP08State_Sel = 'AS-Glob:TI-EVR-1:OTP08State-Sel'
        EVR1_OTP08Width_SP = 'AS-Glob:TI-EVR-1:OTP08Width-SP'
        EVR1_OTP08Evt_SP = 'AS-Glob:TI-EVR-1:OTP08Evt-SP'
        EVR1_OTP08Polarity_Sel = 'AS-Glob:TI-EVR-1:OTP08Polarity-Sel'
        EVR1_OTP08Pulses_SP = 'AS-Glob:TI-EVR-1:OTP08Pulses-SP'

        DEFAULT_SP_VALUES = {
            EVG_ContinuousEvt_Sel: 0,
            EVG_DevEnbl_Sel: 1,
            EVG_ACDiv_SP: 30,
            EVG_ACEnbl_Sel: 1,
            EVG_RFDiv_SP: 4,
            EVG_Evt01Mode_Sel: 'External',
            EVR1_DevEnbl_Sel: 1,
            EVR1_OTP08State_Sel: 1,
            EVR1_OTP08Width_SP: 7000,
            EVR1_OTP08Evt_SP: 1,
            EVR1_OTP08Polarity_Sel: 0,
            EVR1_OTP08Pulses_SP: 1}

    def __init__(self, ramp_config, prefix='',):
        """Initialize object."""
        pvnames_sp = tuple(ConnTiming.Const.DEFAULT_SP_VALUES.keys())
        super().__init__(prefix, pvnames_sp)
        self._ramp_config = ramp_config

    def configure_timing_modules_init(self):
        """Initialize timing."""
        pass

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
