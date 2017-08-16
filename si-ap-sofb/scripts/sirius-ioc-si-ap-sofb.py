#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from si_ap_sofb import si_ap_sofb

parser = _argparse.ArgumentParser(description="Run SI SOFB IOC.")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="Starts IOC in Debug Mode.")
args = parser.parse_args()
si_ap_sofb.run(debug=args.debug)
