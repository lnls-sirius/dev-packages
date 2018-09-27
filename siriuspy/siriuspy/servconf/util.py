"""ConfigService util module."""

from siriuspy.util import get_timestamp as _get_timestamp


def generate_default_config_name(config_type):
    """Generate a default configuration name using config_type."""
    name = _get_timestamp() + '_' + config_type
    return name
