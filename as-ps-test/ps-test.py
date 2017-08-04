#!/usr/local/bin/python-sirius -u
"""AS PS Test IOC executable."""

import sys
import ps_test as ioc_module

ioc_name = 'AS-MA'
ioc_description = '       AS-PS Test Soft IOC'
(_, ioc_database), = ioc_module._main.App.pvs_database.items()
ioc_version = ioc_module._main._pvs._COMMIT_HASH
ioc_prefix = ioc_module._main._pvs._PREFIX

if sys.argv[-1] == 'print_banner':
    ioc_module._util.print_ioc_banner(
        ioc_name=ioc_name,
        db=ioc_database,
        description=ioc_description,
        version=ioc_version,
        prefix=ioc_prefix)
else:
    ioc_module.run()
