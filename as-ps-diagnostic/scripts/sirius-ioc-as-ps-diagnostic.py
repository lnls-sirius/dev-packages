#!/usr/local/bin/python-sirius -u
import argparse
from as_ps_diagnostic import as_ps_diagnostic


parser = argparse.ArgumentParser()
parser.add_argument(
    'section',
    help='Regexp for the accelerator (TB, BO, TS, SI).')
parser.add_argument(
    'sub_section',
    help='Regexp for the the sub_section (Fam, 01, 01U, ...).')
parser.add_argument(
    'device',
    help='Regexp for the device (Cv, CH, QD1, SF, B1B1-1, ...).')


if __name__ == '__main__':
    args = parser.parse_args()
    as_ps_diagnostic.run(args.section, args.sub_section, args.device, False)

