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


class _ConnConfigService:
    """Syntactic sugar ramp class for ConfigService."""

    def __init__(self, config_type, url=_envars.server_url_configdb):
        """Contructor."""
        if config_type not in ('bo_ramp', 'bo_normalized'):
            raise ValueError('Invalid configuration type!')
        self._config_type = config_type
        self._srvconf = _ConfigService(url=url)

    def config_get(self, name):
        """Get configuration by its name."""
        r = self._srvconf.get_config(self._config_type, name)
        return _ConnConfigService._process_return(r)

    def config_insert(self, name, value):
        """Insert a new configuration."""
        r = self._srvconf.insert_config(self._config_type, name, value)
        return _ConnConfigService._process_return(r)

    def config_find(self,
                    name=None,
                    begin=None,
                    end=None,
                    discarded=False):
        """Return configurations."""
        r = self._srvconf.find_configs(config_type=self._config_type,
                                       name=name, begin=begin, end=end,
                                       discarded=discarded)
        return _ConnConfigService._process_return(r)

    def config_find_nr(self,
                       name=None,
                       begin=None,
                       end=None,
                       discarded=False):
        """Return nr of configurations."""
        r = self._srvconf.find_nr_configs(config_type=self._config_type,
                                          name=name, begin=begin, end=end,
                                          discarded=discarded)
        return _ConnConfigService._process_return(r)

    def config_update(self, metadata, configuration):
        """Update existing configuration."""
        config = dict(metadata)
        config.update({'value': configuration})
        r = self._srvconf.update_config(config)
        return _ConnConfigService._process_return(r)

    def config_delete(self, metadata):
        """Mark a configuration as discarded."""
        r = self._srvconf.delete_config(metadata)
        return _ConnConfigService._process_return(r)

    def check_value(self, value):
        """Return True or False depending whether value matches config type."""
        return _check_value(self._config_type, value)

    def get_config_type_template(self):
        """Return template dictionary of config type."""
        return self._srvconf.get_config_type_template(self._config_type)

    @staticmethod
    def _response_check(r):
        """Check response."""
        if r['code'] == _HTTPStatus.NOT_FOUND:
            raise _RampConfigNotFound(r['message'])
        elif r['code'] != _HTTPStatus.OK:
            raise _RampCouldNotConn(r['message'])

    @staticmethod
    def _process_return(r):
        _ConnConfigService._response_check(r)
        # print(r)
        if 'result' in r:
            metadata = r['result']
            configuration = None
            if isinstance(metadata, dict):
                metadata = dict(metadata)  # copy
                configuration = dict(metadata['value'])
                del metadata['value']
            return configuration, metadata


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
