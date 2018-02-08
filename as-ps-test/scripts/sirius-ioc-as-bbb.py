#!/usr/local/bin/python-sirius -u
"""BeagleBone Black IOC executable."""
import sys
import os
from as_ps_test import as_ps_test as ioc_module
from siriuspy.search import PSSearch


def print_help():
    """Print help."""
    name = os.path.basename(sys.argv[0])
    print('NAME')
    print('       {} - start beaglebone black IOC.'.format(name))
    print()
    print('SYNOPSIS')
    print('       {} [BBBNAME]...'.format(name))
    print()
    print('DESCRIPTION')
    print('       Start execution of BeagleBone Black IOC.')
    print()
    print('       <no arguments>')
    print('               list all beablebone black names and power supplies.')
    print()


bbb_dict = PSSearch.get_bbbname_dict()
bbbnames = sorted(bbb_dict.keys())
if len(sys.argv) == 1:
    print_help()
    print('List of beaglebone black names:')
    print()
    for i in range(len(bbbnames)):
        bbbname = bbbnames[i]
        print('{:<20s} '.format(bbbname), end='')
        psnames = bbb_dict[bbbname]
        for psname in psnames:
            print('{:<16s} '.format(psname), end='')
        print()
else:
    ioc_module.run((sys.argv[1],))
