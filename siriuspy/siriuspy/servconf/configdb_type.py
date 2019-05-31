"""Configurations connection classes."""

from .configdb_client import ConfigDBClient as _ConfigDBClient


class ConfigDBType(_ConfigDBClient):
    """Syntactic sugar class for ConfigService."""

    def __init__(self, config_type, url=None):
        """Contructor."""
        self._config_type = config_type
        super().__init__(url=url)

    @property
    def config_type(self):
        """Type of configuration."""
        return self._config_type

    def find_configs(self,
                     name=None,
                     begin=None,
                     end=None,
                     discarded=False):
        """Find configurations matching search criteria.

        Parameters
        ----------
            discarded : True | False (default) | None
            If True, return only discarded configurations, if False, return
            only configurations in use. If None, return all configurations
            matching the other criteria.

        """
        return super().find_configs(
            self._config_type, name=name, begin=begin, end=end,
            discarded=discarded)

    def get_config_value(self, name, discarded=False):
        """Mark a valid configuration as discarded."""
        return super().get_config_value(
            self._config_type, name, discarded=discarded)

    def get_config_info(self, name, discarded=False):
        """Mark a valid configuration as discarded."""
        return super().get_config_info(
            self._config_type, name, discarded=discarded)

    def rename_config(self, oldname, newname):
        """Rename configuration in database."""
        return super().rename_config(self._config_type, oldname, newname)

    def insert_config(self, name, value):
        """Insert configuration into database."""
        return super().insert_config(self._config_type, name, value)

    def delete_config(self, name):
        """Mark a valid configuration as discarded."""
        return super().delete_config(self._config_type, name)

    def retrieve_config(self, name):
        """Mark a discarded configuration as valid."""
        return super().retrieve_config(self._config_type, name)

    def get_value_template(self):
        """Return value of a configuration type."""
        return super().get_value_template(self._config_type)

    def check_valid_value(self, value):
        """Check whether values data corresponds to a configuration type."""
        return super().check_valid_value(self._config_type, value)
