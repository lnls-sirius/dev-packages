#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from as_ti_ll_simul import as_ti_ll_simul

parser = _argparse.ArgumentParser(description="Run Timing Simulation IOC.")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="Starts IOC in Debug Mode.")

args = parser.parse_args()
as_ti_ll_simul.run(debug=args.debug)
