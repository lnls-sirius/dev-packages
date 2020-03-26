"""Subpackage for the Archiver server."""

from ..envars import SRVURL_ARCHIVER as SERVER_URL

from .client import ClientArchiver
from .pvarch import PV, PVDetails, PVData


del client, pvarch
