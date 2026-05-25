"""Define properties of orbit interlock for the SIRIUS storage ring."""

import ast as _ast
from copy import deepcopy as _dcopy
from threading import Lock as _Lock

from siriuspy import clientweb as _web

_timeout = 1.0


class OrbIntlkSearch:
    """Contain properties of the triggers."""

    _limits = dict()
    _lock = _Lock()

    @classmethod
    def get_limits(cls):
        """Return a dictionary with high level events."""
        cls._init()
        return _dcopy(cls._limits)

    @classmethod
    def reset(cls):
        """Reset data."""
        cls._limits = dict()
        cls._init()

    @classmethod
    def _init(cls):
        """Initialize the Instance."""
        with cls._lock:
            if cls._limits:
                return
            if not _web.server_online():
                raise Exception('Could not connect with Consts Server!!')
            text = _web.orb_intlk_limits_read(timeout=_timeout)
            cls._limits = _ast.literal_eval(text)
