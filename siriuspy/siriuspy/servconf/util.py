"""ConfigService util module."""

import time as _time
import datetime as _datetime
import re as _re


def get_timestamp(now=None):
    """."""
    if now is None:
        now = _time.time()
    return _datetime.datetime.fromtimestamp(now).strftime('%y%m%d-%H%M%S')


def generate_config_name(name=None):
    """Generate a configuration name using current imestamp."""
    if name is None:
        name = ''
    name = name.strip()
    tsf = _re.compile('^\d\d\d\d\d\d-\d\d\d\d\d\d')
    if tsf.match(name):
        new_name = get_timestamp() + name[13:]
    else:
        if name:
            new_name = get_timestamp() + ' ' + name
        else:
            new_name = get_timestamp()
    return new_name
