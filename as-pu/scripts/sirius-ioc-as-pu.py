#!/usr/local/bin/python-sirius -u
"""BeagleBone Black IOCs Launcher."""
import sys
import os
from as_pu import as_pu as ioc_module


def print_help():
    """Print help."""
    name = os.path.basename(sys.argv[0])
    print('NAME')
    print('       {} - start beaglebone black IOC.'.format(name))
    print()
    print('SYNOPSIS')
    print('       {} [BBBNAME] []...'.format(name))
    print()
    print('DESCRIPTION')
    print('       Start execution of BeagleBone Black IOC.')
    print()
    print('       <no arguments>')
    print('               list all beaglebone black names and power supplies.')
    print()
    print('       --help')
    print('               print this help.')
    print()
    print('       --real')
    print('               creates real PRU and SerialComm objects, not '
          'simulated ones.')
    print()


def main():
    """Launch BBB IOC."""
    if len(sys.argv) == 1:
        pass
    else:
        args = [arg for arg in sys.argv[1:]]
        if '--real' in args:
            simulate = False
            args.remove('--real')
        elif '--help' in args:
            args.remove('--help')
            print_help()
        else:
            simulate = True

        if args:
            ioc_module.run(args, simulate=simulate)


if __name__ == "__main__":
    main()
