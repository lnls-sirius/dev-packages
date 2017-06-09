from   siriuspy.pwrsupply import PowerSupply
from   siriuspy.pwrsupply import ControllerSim


_prefix = 'VAX-SI-Fam:'


psnames = ('PS-B1B2-1','PS-B1B2-2')
ps = {}
for psname in psnames:
    c = ControllerSim(current_min=0, current_max=100, psname=psname)
    ps[psname] = PowerSupply(psname='SI-Fam:' + psname, controller=c)



with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

def get_database():

    db = {}
    for psname in psnames:
        ps_db = ps[psname].database
        props = list(ps_db.keys())
        for i in range(len(props)):
            db[psname+':'+props[i]] = ps_db[props[i]]
    return {_prefix:db}

