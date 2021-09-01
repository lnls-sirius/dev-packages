#!/usr/bin/env python-sirius

"""Test reconstrction factories."""

import json

from siriuspy.search import PSSearch, MASearch
from siriuspy.clientconfigdb import ConfigDBDocument
from siriuspy.ramp.ramp import BoosterRamp
from siriuspy.ramp.magnet import get_magnet


PSNAMES = PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})

R_ORIG = BoosterRamp('testing')
R_ORIG.load()


def run():
    ntimes = sorted(R_ORIG.ps_normalized_configs_times)

    nconf = dict()
    for nct in ntimes:
        strt = '{:.3f}'.format(nct)
        nconf[strt] = dict()
        nconf[strt]['label'] = R_ORIG[nct]['label']
        for psn in PSNAMES:
            mag = get_magnet(MASearch.conv_psname_2_psmaname(psn))
            if psn in ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2'):
                energy = R_ORIG.ps_waveform_interp_energy(nct)
                curr = mag.conv_strength_2_current(energy)
                nconf[strt][psn] = curr
            else:
                energy = R_ORIG.ps_waveform_interp_energy(nct)
                strg = R_ORIG[nct][psn]
                curr = mag.conv_strength_2_current(
                    strg, strengths_dipole=energy)
                nconf[strt][psn] = curr
        # print(nct)
        # for k, v in nconf[strt].items():
        #     print(k, v)

    json.dump(nconf, open("nconf_currents.txt", 'w'))


if __name__ == "__main__":
    run()
