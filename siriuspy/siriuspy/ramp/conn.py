"""Module with connector classes.

This module implements waveform communications with magnet soft IOcs and
ConfigDB service.
"""


from siriuspy.factory import MagnetFactory as _MagnetFactory
from siriuspy import envars as _envars

class ConnMagnet:
    """Magnet Connector Class."""

    def __init__(self,
                 use_vaca=False,
                 vaca_prefix=None):
        """Init method."""
        self._use_vaca = use_vaca
        self._vaca_prefix = vaca_prefix
        self._magnets = {}

    def wfm_send(self, maname, wfm_current):
        """Send current waveform to magnet power supply."""
        if maname not in self._magnets:
            self._create_magnet_conn(maname)
        magnet = self._magnets[maname]
        if not magnet.connected:
            raise Exception(
                    'Not connected to power supply of {}!'.format(maname))
        else:
            magnet.wfmdata_sp = wfm_current

    def wfm_recv(self, maname):
        """Receive current waveform to magnet power supply."""
        if maname not in self._magnets:
            self._create_magnet_conn(maname)
        magnet = self._magnets[maname]
        if not magnet.connected:
            raise Exception(
                'Not connected to power supply of {}!'.format(maname))
        else:
            wfm_current = magnet.wfmdata_rb
            return wfm_current

    def _create_magnet_conn(self, maname):
        self._pses[maname] = _MagnetFactory(maname=maname,
                                            use_vaca=self._use_vaca,
                                            vaca_prefix=self._vaca_prefix,
                                            lock=False,
                                            )


class ConnConfigDB:
    """Config DB connector class."""

    def __init__(self, url=_envars.server_url_configdb):
