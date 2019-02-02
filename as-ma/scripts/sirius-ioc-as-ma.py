#!/usr/local/bin/python-sirius -u
"""Power Supply Magnet IOC Launcher."""
import sys
import os
from siriuspy.search import PSSearch
from siriuspy.search import MASearch
from as_ma import as_ma as ioc_module


_manames = None
_bbbnames = None


def build_maname_list(devname_list):
    """Return list with manames fomr a device name list."""
    global _manames, _bbbnames
    # initialize _manames, if not done yet
    if _manames is None:
        _manames = MASearch.get_manames()
    manames = set()
    for devname in devname_list:
        if devname in _manames:
            manames.add(devname)
        else:
            # not a maname, so initialize _bbbnames, if not done yet
            if _bbbnames is None:
                _bbbnames = PSSearch.get_bbbnames()
            if devname in _bbbnames:
                mnames = MASearch.conv_bbbname_2_psmanames(devname)
                for maname in mnames:
                    manames.add(maname)
            else:
                print('MA device name "{}" not defined!'.format(devname))
                sys.exit()
    return list(manames)


def cmd_print_help():
    """Print help."""
    name = os.path.basename(sys.argv[0])
    print('NAME')
    print('       {} - start power supply magnet IOC'.format(name))
    print()
    print('SYNOPSIS')
    print('       {} [BBBNAME] []...'.format(name))
    print()
    print('DESCRIPTION')
    print('       Start execution of power supply magnet IOC')
    print()
    print('       BBBNAME can be either a beaglebone name or a list of magnets')
    print('')
    print('       --help | <no arguments>')
    print('               print this help.')
    print()
    print('       --list')
    print(('               list all beaglebones and corresponding '
           'MA power supply magnets'))
    print()
    print('       --dry-run')
    print('               process input without running IOC proccess.')
    print()


def cmd_list():
    """List all beaglebones."""
    print('Beaglebone list:')
    print()
    bbbnames = PSSearch.get_bbbnames()
    for bbbname in bbbnames:
        print('{:<25s} '.format(bbbname), end='')
        manames = MASearch.conv_bbbname_2_psmanames(bbbname)
        for maname in manames:
            print('{:<20s} '.format(maname), end='')
        print()


def main():
    """Launch BBB IOC."""
    if len(sys.argv) == 1:
        cmd_print_help()
    else:
        # process arguments
        dry_run = False
        args = [arg for arg in sys.argv[1:]]
        if '--help' in args:
            args.remove('--help')
            cmd_print_help()
        if '--list' in args:
            args.remove('--list')
            cmd_list()
        if '--dry-run' in args:
            args.remove('--dry-run')
            dry_run = True
        # run IOC
        if args:
            manames = build_maname_list(args)
            if manames:
                if not dry_run:
                    ioc_module.run(manames=manames)
                else:
                    print('Running MA IOC for: {}'.format(manames))


if __name__ == "__main__":
    main()
