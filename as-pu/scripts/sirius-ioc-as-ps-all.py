#!/usr/local/bin/python-sirius -u
"""AS PS Test IOC executable."""
from multiprocessing import Process

from as_ps import as_ps as ioc_module
from siriuspy.search import PSSearch


def read_bbbs():
    """Return all BBB names."""
    PSSearch._reload_bbb_2_psname_dict()
    return list(PSSearch._bbbname_2_psnames_dict.keys())


processes = []
bbbs = read_bbbs()
for i in range(len(bbbs)):
    bbblist = bbbs[i*5:i*5+5]
    if bbblist:
        processes.append(Process(target=ioc_module.run, args=(bbblist,)))
        processes[-1].daemon = True
        processes[-1].start()
    else:
        break

for p in processes:
    p.join()

# ioc_module.run()
