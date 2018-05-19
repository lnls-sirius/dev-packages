"""Module with connector classes.

This module implements connector classes responsible for communications with
magnet soft IOcs, ConfigDB service and orbit, tune and chromacity correction
IOCs.
"""

from http import HTTPStatus as _HTTPStatus
from siriuspy import envars as _envars
from siriuspy.ramp.exceptions import RampCouldNotConnect as _RampCouldNotConn
from siriuspy.ramp.exceptions import RampConfigNotFound as _RampConfigNotFound
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriuspy.servconf.conf_types import check_value as _check_value


class _ConnConfigService(_ConfigService):
    """Syntactic sugar ramp class for ConfigService."""

    def __init__(self, config_type, url=_envars.server_url_configdb):
        """Contructor."""
        if config_type not in ('bo_ramp', 'bo_normalized'):
            raise ValueError('Invalid configuration type!')
        self._config_type = config_type
        self._conn = _ConfigService(url=url)

    def config_get(self, name):
        """Get configuration by its name."""
        return self._conn.get_config(self._config_type, name)

    def config_insert(self, name, value):
        """Insert a new configuration."""
        return self._conn.insert_config(self._config_type, name, value)

    def config_find(self,
                    name=None,
                    begin=None,
                    end=None,
                    discarded=False):
        """Return configurations."""
        return self._conn.find_configs(config_type=self._config_type,
                                       name=name, begin=begin, end=end,
                                       discarded=discarded)

    def config_find_nr(self,
                       name=None,
                       begin=None,
                       end=None,
                       discarded=False):
        """Return nr of configurations."""
        return self._conn.find_nr_configs(config_type=self._config_type,
                                          name=name, begin=begin, end=end,
                                          discarded=discarded)

    def config_update(self, obj_dict):
        """Update existing configuration."""
        return self._conn.update_config(obj_dict)

    def check_value(self, value):
        """Return True or False depending whether value matches config type."""
        return _check_value(self._config_type, value)

    def get_config_type_template(self):
        """Return template dictionary of config type."""
        return self._conn.get_config_type_template(self._config_type)

    def response_check(self, r):
        """Check response."""
        if r['code'] == _HTTPStatus.NOT_FOUND:
            raise _RampConfigNotFound(r['message'])
        elif r['code'] != _HTTPStatus.OK:
            print(r)
            raise _RampCouldNotConn(r['message'])


class ConnConfig_BORamp(_ConnConfigService):
    """ConifgurationService for BO ramp configs."""

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_ramp', url=url)


class ConnConfig_BONormalized(_ConnConfigService):
    """ConifgurationService for BO normalized configs."""

    # _template_value = \
    #     _ConnConfigService.get_config_type_template('bo_normalized')

    def __init__(self, url=_envars.server_url_configdb):
        """Constructor."""
        _ConnConfigService.__init__(self, config_type='bo_normalized', url=url)


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
#
#
# class ConnTune(_Conn):
#     """Connector class to interact with TuneCorr IOCs."""
#
#     pass
#
#
# class ConnChrom(_Conn):
#     """Connector class to interact with ChromCorr IOCs."""
#
#     pass
