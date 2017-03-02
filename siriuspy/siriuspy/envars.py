import os as _os


# --- folders ---

folder_root = _os.environ.get('ROOT_GROUP', '/home/fac_files')

folder_epics_base = _os.environ.get('EPICS_DIR', default='/usr/local/epics')

folder_lnls_sirius = _os.environ.get('LNLS_SIRIUS', _os.path.join(folder_root, 'lnls-sirius'))
folder_lnls_fac = _os.environ.get('LNLS_FAC', _os.path.join(folder_root, 'lnls-fac'))
folder_lnls_ima = _os.environ.get('LNLS_IMA', _os.path.join(folder_root, 'lnls-ima'))

folder_fac_code = _os.path.join(folder_root, 'lnls-fac')
folder_fac_data = _os.path.join(folder_root, 'data')

folder_lnls_sirius_csslnls = _os.path.join(folder_lnls_sirius, 'org.csstudio.product')
folder_lnls_sirius_discs = _os.path.join(folder_lnls_sirius, 'discs-management')
folder_lnls_sirius_csconstants = _os.path.join(folder_lnls_sirius, 'control-system-constants')
folder_lnls_sirius_dev_packages = _os.path.join(folder_lnls_sirius, 'dev-packages')
folder_lnls_sirius_hla = _os.path.join(folder_lnls_sirius, 'hla')


# --- support applications IPs/URLs ---

server_url_rbac = _os.environ.get('SIRIUS_URL_RBAC', 'https://10.0.7.55:8445')
server_url_ns = _os.environ.get('SIRIUS_URL_NS', 'http://10.0.7.55:8080/names')
server_url_ccdb = _os.environ.get('SIRIUS_URL_CCDB', 'http://10.0.7.55:8083')
server_url_cables = _os.environ.get('SIRIUS_URL_CABLES', 'http://10.0.7.55:8086')
server_url_web = _os.environ.get('SIRIUS_URL_WEB', 'http://10.0.7.55')
