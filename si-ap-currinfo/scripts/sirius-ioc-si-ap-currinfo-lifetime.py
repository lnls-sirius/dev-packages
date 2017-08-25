#!/usr/local/bin/python-sirius -u
"""SI AP Current Lifetime IOC executable."""

from si_ap_currinfo import si_ap_currinfo as ioc_module
ioc_module.run('lifetime')
