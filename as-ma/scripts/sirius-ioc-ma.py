#!/usr/local/bin/python-sirius -u
"""Lauch Magnet IOCs."""
import sys
import re
from multiprocessing import Process

from as_ma import as_ma as ioc_module
from siriuspy.search import PSSearch

MAX_N_DEV = 4  # Max number of devices an IOC may handle

if len(sys.argv) == 1:
    sec, sub, dev = '.*', '.*', '.*'
elif len(sys.argv) == 2:
    sec, sub, dev = sys.argv[1], '.*', '.*'
elif len(sys.argv) == 3:
    sec, sub, dev = *sys.argv[1:3], '.*'
else:
    sec, sub, dev = sys.argv[1:]


def get_bbbmap(sec, sub, dev):
    """Return a dict mapping each BBB to a list of magnets."""
    si_bo_dipoles = re.compile('.*(SI|BO)-Fam:PS-B.*$')
    # Get section
    if sec == 'AS':
        section = '.*'
    else:
        section = sec
    # Get pslist based on section and dev pattern
    pslist = PSSearch.get_psnames(
            {'sec': section, 'sub': sub, 'dis': 'PS', 'dev': dev})
    bbbmap = {}
    # Iter pslist and build a dict mapping each BBB to a list of magnets
    for psname in pslist:
        # Get BBB name
        bbbname = PSSearch.conv_psname_2_bbbname(psname)
        if bbbname not in bbbmap:
            bbbmap[bbbname] = list()
        # Treat SI and BO dipole magnets special cases
        match = si_bo_dipoles.match(psname)
        if match:
            if match.groups()[0] == 'SI':
                maname = 'SI-Fam:MA-B1B2'
            else:
                maname = 'BO-Fam:MA-B'
        else:  # Just replace PS for MA
            maname = psname.replace('PS', 'MA')
        # Append magnet to BBB
        if maname not in bbbmap[bbbname]:
            bbbmap[bbbname].append(maname)

    # return {'SI-Glob:CO-BBB-1': ['SI-Fam:MA-B1B2']}
    return bbbmap


processes = list()

# Start IOC as processes for each MAX_N_DEV magnets
for bbb, pslist in get_bbbmap(sec, sub, dev).items():
    n_ps = len(pslist)
    n_dev = MAX_N_DEV
    p = 1 if n_ps % n_dev > 0 else 0
    r = int(n_ps / n_dev)
    for i in range(r + p):
        processes.append(
            Process(
                target=ioc_module.run, args=(pslist[i*n_dev:(i+1)*n_dev],)))
        processes[-1].daemon = True
        processes[-1].start()

for p in processes:
    p.join()
