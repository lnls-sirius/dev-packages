#!/usr/local/bin/python-sirius -u
"""Power Supply Magnet IOC Launcher."""
import sys
import os
from as_ma import as_ma as ioc_module
from siriuspy.search import PSSearch
from siriuspy.search import MASearch


def print_help():
    """Print help."""
    name = os.path.basename(sys.argv[0])
    print('NAME')
    print('       {} - start power supply magnet IOC.'.format(name))
    print()
    print('SYNOPSIS')
    print('       {} [BBBNAME] []...'.format(name))
    print()
    print('DESCRIPTION')
    print('       Start execution of power supply magnet IOC.')
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


def get_manames(bbbname):
    """Return list of manames for a list of bbbnames."""
    manames = set()
    psnames = PSSearch.conv_bbbname_2_psnames(bbbname)
    for psname in psnames:
        maname = MASearch.conv_psname_2_maname_pwrsupply(psname[0])
        if maname is None:
            continue
        manames.add(maname)
    return list(manames)


def main():
    """Launch BBB IOC."""
    bbb_dict = PSSearch.get_bbbname_dict()
    bbbnames = sorted(bbb_dict.keys())

    if len(sys.argv) == 1:
        print_help()
        print('List of beaglebone black names:')
        print()
        bbbnames = PSSearch.get_bbbnames()
        for bbbname in bbbnames:
            print('{:<20s} '.format(bbbname), end='')
            manames = get_manames(bbbname)
            for maname in manames:
                print('{:<16s} '.format(maname), end='')
            print()
    else:
        args = [arg for arg in sys.argv[1:]]
        if '--help' in args:
            args.remove('--help')
            print_help()
        if args:
            manames = set()
            for arg in args:
                manames |= set(get_manames(bbbname=arg))
            ioc_module.run(manames=list(manames))


if __name__ == "__main__":
    main()
