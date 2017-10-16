"""Communications Module.

This module implements waveform communications with magnet soft IOcs.
"""


from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.factory import MagnetFactory as _MagnetFactory


class Comm:
    def __init__(self, use_vaca=False,
                       vaca_prefix=None):
        self._use_vaca = use_vaca
        self._vaca_prefix = vaca_prefix
        self._pses = {}

    def _create_pses(self, magnet):
        m = Magnet(magnet)
        self._pses[magnet] = _MagnetFactory(maname=m.maname,
                                            use_vaca=self._use_vaca,
                                            vaca_prefix=self._vaca_prefix,
                                            lock=False,
                                           )

    def wfm_send(self, magnet, wfm_current):
        """Send current waveform to magnet power supply."""
        if magnet not in self._pses:
            self._create_pses(magnet)
        pses = self._pses[magnet]
        if not pses.connected:
            raise Exception('Not connected to power supply of {}!'.format(magnet))
        else:
            pses.wfmdata_sp = wfm_current

    def wfm_recv(self, magnet):
        """Receive current waveform to magnet power supply."""
        if magnet not in self._pses:
            self._create_pses(magnet)
        pses = self._pses[magnet]
        if not pses.connected:
            raise Exception('Not connected to power supply of {}!'.format(magnet))
        else:
            wfm_current = pses.wfmdata_rb
            return wfm_current
