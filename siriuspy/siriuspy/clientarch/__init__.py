"""Subpackage for the Archiver server."""

import siriuspy.envars as _envars
from .client import ClientArchiver
from .pvarch import PV, PVDetails, PVData


SERVER_URL = _envars.SRVURL_ARCHIVER
