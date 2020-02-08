"""Subpackage for the Archiver server."""

import siriuspy.envars as _envars
from .client import ClientArchiver


SERVER_URL = _envars.SRVURL_ARCHIVER
