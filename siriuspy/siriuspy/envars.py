"""Set important variables for the proper work of the package."""
import os as _os


# --- folders ---

folder_root = _os.environ.get(
    'ROOT_GROUP',   default='/home/fac_files')
folder_epics_base = _os.environ.get(
    'EPICS_BASE',    default='/opt/epics/base')
folder_lnls_sirius = _os.environ.get(
    'LNLS_SIRIUS',  default=_os.path.join(folder_root, 'lnls-sirius'))
folder_lnls_fac = _os.environ.get(
    'LNLS_FAC',     default=_os.path.join(folder_root, 'lnls-fac'))
folder_lnls_ima = _os.environ.get(
    'LNLS_IMA',     default=_os.path.join(folder_root, 'lnls-ima'))
folder_fac_code = _os.path.join(
    folder_root, 'lnls-fac')
folder_fac_data = _os.path.join(
    folder_root, 'data')
folder_lnls_sirius_csslnls = _os.path.join(
    folder_lnls_sirius, 'org.csstudio.product')
folder_lnls_sirius_discs = _os.path.join(
    folder_lnls_sirius, 'discs-management')
folder_lnls_sirius_csconstants = _os.path.join(
    folder_lnls_sirius, 'control-system-constants')
folder_lnls_sirius_dev_packages = _os.path.join(
    folder_lnls_sirius, 'dev-packages')
folder_lnls_sirius_hla = _os.path.join(
    folder_lnls_sirius, 'hla')

# --- support applications IPs/URLs ---

server_url_rbac_auth = _os.environ.get(
    'SIRIUS_URL_RBAC_AUTH', default='https://sirius-rbac-auth.lnls.br')
server_url_rbac = _os.environ.get(
    'SIRIUS_URL_RBAC',      default='https://rbac:8445')
server_url_ns = _os.environ.get(
    'SIRIUS_URL_NS',        default='http://naming-service-wildfly:8089/names')
server_url_ccdb = _os.environ.get(
    'SIRIUS_URL_CCDB',      default='http://ccdb:8083')
server_url_cables = _os.environ.get(
    'SIRIUS_URL_CABLES',    default='http://cables:8086')
server_url_consts = _os.environ.get(
    'SIRIUS_URL_CONSTS',    default='http://sirius-consts.lnls.br')
server_url_logbook = _os.environ.get(
    'SIRIUS_URL_LOGBOOK',   default='http://sirius-logbook.lnls.br')
server_url_configdb = _os.environ.get(
    'SIRIUS_URL_CONFIGDB',  default='http://sirius-configdb.lnls.br:8085')

vaca_prefix = _os.environ.get('VACA_PREFIX',   default='')

# --- repositories ---

org_folders = {
    'lnls-fac': folder_lnls_fac,
    'lnls-ima': folder_lnls_ima,
    'lnls-sirius': folder_lnls_sirius,
}

repo_names = {

    'lnls-fac': ['apsuite',
                 'tools',
                 'collective_effects',
                 'job_manager',
                 'pyaccel',
                 'trackcpp',
                 'fieldmaptrack',
                 'lnls',
                 # 'sands-adaptation',
                 'tracy_sirius',
                 'mathphys',
                 'scripts',
                 'va',
                 'MatlabMiddleLayer',
                 'pymodels'],

    'lnls-ima': ['bo-correctors',
                 'bo-sextupoles',
                 'tb-dipoles',
                 'bo-dipoles',
                 'si-dipoles-b1',
                 'si-quadrupoles-q14',
                 'bo-quadrupoles-qd',
                 'si-dipoles-b2',
                 'si-quadrupoles-q20',
                 'bo-quadrupoles-qf',
                 'si-fast-correctors',
                 'si-sextupoles-s15'],

    'lnls-sirius': ['control-system-constants',
                    'discs-management',
                    'epics-dev',
                    'org.csstudio.product',
                    'dev-packages',
                    'machine-applications',
                    'hla',
                    'pydm'],

}
