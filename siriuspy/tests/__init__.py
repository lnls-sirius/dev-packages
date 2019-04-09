"""Siriuspy unittest package."""

# make sure tests are run without access to sirius servers!
import os as _os
from . import mock_servweb

_os.environ['SIRIUS_URL_RBAC_AUTH'] = ''
_os.environ['SIRIUS_URL_RBAC'] = ''
_os.environ['SIRIUS_URL_NS'] = ''
_os.environ['SIRIUS_URL_CCDB'] = ''
_os.environ['SIRIUS_URL_CABLES'] = ''
_os.environ['SIRIUS_URL_CONSTS'] = ''
_os.environ['SIRIUS_URL_LOGBOOK'] = ''
_os.environ['SIRIUS_URL_CONFIGDB'] = ''
