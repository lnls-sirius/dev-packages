
from siriuspy.epics import PV
from siriuspy.search import IOCSearch

pvs = dict()
for ioc in IOCSearch.get_iocs():
    prefs = IOCSearch.conv_ioc_2_prefixes(ioc)
    if '-ap-' in ioc:
        parts = ioc.split('-')
        for pref in prefs:
            if parts[2] in pref.lower() and parts[0] == pref[:2].lower():
                prefix = pref
                break
    else:
        prefix = prefs[0]

    if prefix.endswith('Kick') or prefix.endswith('KL') or \
            prefix.endswith('Kx'):
        prefix += '-SP'
    elif ':TI-' in prefix:
        prefix += ':Status-Mon'
    else:
        if not prefix.endswith(':Diag'):
            prefix += ':'
        prefix += 'Version-Cte'
    pvs[ioc] = PV(prefix)

for pv in pvs.values():
    if not pv.connected:
        print(pv.pvname)
