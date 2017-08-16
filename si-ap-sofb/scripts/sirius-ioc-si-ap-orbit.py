#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from si_ap_orbit import si_ap_orbit

parser = _argparse.ArgumentParser(description="Run SI Orbit IOC.")
parser.add_argument('-n', '--noise', action='store_true', default=False,
                    help="Add Noise to orbit Measurements")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="Starts IOC in Debug Mode.")
args = parser.parse_args()
si_ap_orbit.run(add_noise=args.noise, debug=args.debug)
