#!/usr/local/bin/python-sirius -u
"""SI AP Current Accumulated Charge IOC executable."""

from si_ap_currinfo import si_ap_currinfo as ioc_module
ioc_module.run('charge')
