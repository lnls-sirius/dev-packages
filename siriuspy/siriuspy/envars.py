"""Set important variables for the proper work of the package."""
import os as _os


# --- directories ---

DIR_ROOT = _os.environ.get(
    'ROOT_GROUP', default='/home')
DIR_EPICS_BASE = _os.environ.get(
    'EPICS_BASE', default='/usr/lib/epics')

DIR_SIRIUS = _os.environ.get(
    'LNLS_SIRIUS', default=_os.path.join(DIR_ROOT, 'sirius'))
DIR_FACS = _os.environ.get(
    'LNLS_FAC', default=_os.path.join(DIR_ROOT, 'facs'))
DIR_IMAS = _os.environ.get(
    'LNLS_IMA', default=_os.path.join(DIR_ROOT, 'imas'))

DIR_SIRIUS_CODE = _os.environ.get(
    'LNLS_SIRIUS', default=_os.path.join(DIR_ROOT, DIR_SIRIUS, 'repos'))
DIR_FACS_CODE = _os.path.join(
    DIR_ROOT, DIR_FACS, 'repos')

DIR_SIRIUS_CODE_CSCNSTS = _os.path.join(
    DIR_SIRIUS_CODE, 'control-system-constants')
DIR_SIRIUS_CODE_SIRIUSPY = _os.path.join(
    DIR_SIRIUS_CODE, 'dev-packages')
DIR_SIRIUS_CODE_HLA = _os.path.join(
    DIR_SIRIUS, 'hla')


# --- support applications IPs/URLs ---

SRVURL_RBACAUTH = _os.environ.get(
    'SIRIUS_URL_RBAC_AUTH', default='https://sirius-rbac-auth.lnls.br')
SRVURL_RBAC = _os.environ.get(
    'SIRIUS_URL_RBAC', default='https://rbac:8445')
SRVURL_NS = _os.environ.get(
    'SIRIUS_URL_NS', default='http://naming-service-wildfly:8089/names')
SRVURL_CCDB = _os.environ.get(
    'SIRIUS_URL_CCDB', default='http://ccdb:8083')
SRVURL_CABLES = _os.environ.get(
    'SIRIUS_URL_CABLES', default='http://cables:8086')
SRVURL_CSCONSTS = _os.environ.get(
    'SIRIUS_URL_CONSTS',
    default='http://10.128.255.4/control-system-constants')
SRVURL_CSCONSTS_2 = _os.environ.get(
    'SIRIUS_URL_CONSTS_2',
    default='http://10.128.255.3/control-system-constants')
SRVURL_LOGBOOK = _os.environ.get(
    'SIRIUS_URL_LOGBOOK',
    default='http://10.0.38.42/Olog')
SRVURL_CONFIGDB = _os.environ.get(
    'SIRIUS_URL_CONFIGDB',
    default='http://10.128.255.4/config-db')
SRVURL_CONFIGDB_2 = _os.environ.get(
    'SIRIUS_URL_CONFIGDB_2',
    default='http://10.128.255.3/config-db')
SRVURL_ARCHIVER = _os.environ.get(
    'SIRIUS_URL_ARCHIVER',
    default='https://10.0.38.42')


VACA_PREFIX = _os.environ.get('VACA_PREFIX', default='')
