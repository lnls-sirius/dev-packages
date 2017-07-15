import time as _time
import os as _os
import numpy as _np
from threading import Thread as _Thread
import logging as _log
import epics as _epics
from siriuspy.search import PSSearch as _PSSearch

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

with open('VERSION') as f:
    __version__ = f.read()
_TIMEOUT = 0.05

TINY_INTERVAL = 0.001
NUM_TIMEOUT = 6000
WAIT_FOR_SIMULATOR = 0.5

NR_BPMS  = 160
NR_CH    = 120
NR_CV    = 160
NR_CORRS = NR_CH + NR_CV + 1
MTX_SZ   = (2*NR_BPMS) * NR_CORRS
DANG = 2E-1
DFREQ = 200
SECTION = 'SI'
LL_PREF = 'VAF-'

class Orbit:

    REF_ORBIT_FILENAME = 'data/reference_orbit'
    GOLDEN_ORBIT_FILENAME = 'data/golden_orbit'
    EXT = '.siorb'

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'OrbitRefX-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_ref_orbit('x',x)}
        db[pre + 'OrbitRefX-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OrbitRefY-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_ref_orbit('y',x)}
        db[pre + 'OrbitRefY-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'GoldenOrbitX-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_golden_orbit('x',x)}
        db[pre + 'GoldenOrbitX-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'GoldenOrbitY-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_golden_orbit('y',x)}
        db[pre + 'GoldenOrbitY-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'setRefwithGolden-Cmd'] = {'type':'int','value':0,
                                            'unit':'Set the reference orbit with the Golden Orbit',
                                            'fun_set_pv':self._set_ref_with_golden}
        db[pre + 'CorrOrbitX-Mon']   = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'CorrOrbitY-Mon']   = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OnlineOrbitX-Mon'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OnlineOrbitY-Mon'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}

        db[pre + 'OfflineOrbitX-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                        'fun_set_pv':lambda x: self._set_offline_orbit('x',x)}
        db[pre + 'OfflineOrbitX-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OfflineOrbitY-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                        'fun_set_pv':lambda x: self._set_offline_orbit('y',x)}
        db[pre + 'OfflineOrbitY-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OrbitPointsNum-SP']   = {'type':'int','value':1,'unit':'number of points for median',
                                        'fun_set_pv':self._set_orbit_points_num,
                                        'lolim':1, 'hilim':200}
        db[pre + 'OrbitPointsNum-RB']   = {'type':'int','value':1,'unit':'number of points for median'}
        return db

    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.orbs = {'x':[],'y':[]}
        self.orb = {'x':None,'y':None}
        self.offline_orbit = {'x':_np.zeros(NR_BPMS),'y':_np.zeros(NR_BPMS)}
        self.orbit_points_num = 1
        self.correction_mode = 1
        self.count = 0
        self.pv = {'x':None, 'y':None}

    def connect(self):
        self._load_basic_orbits()
        self.pv ={'x':_epics.PV(SECTION + '-Glob:AP-Orbit:OrbitX-Mon',
                                callback=self._update_orbs('x'),
                                connection_callback= self._on_connection ),
                  'y':_epics.PV(SECTION + '-Glob:AP-Orbit:OrbitY-Mon',
                                callback=self._update_orbs('y'),
                                connection_callback= self._on_connection )  }
        if not self.pv['x'].connected or not self.pv['y'].connected:
            self._call_callback('Log-Mon','Orbit PVs not Connected.')
        if self.pv['x'].count != NR_BPMS:
            self._call_callback('Log-Mon','Orbit length not consistent')

    def get_orbit(self, reset=False):
        if not self.correction_mode:
            orbx = self.offline_orbit['x']
            orby = self.offline_orbit['y']
            self._call_callback('CorrOrbitX-Mon',list(orbx))
            self._call_callback('CorrOrbitY-Mon',list(orby))
        else:
            if reset: self._reset_orbs()
            for i in range(2 * self.orbit_points_num):
                if self.orb['x'] is not None and self.orb['y'] is not None:
                    orbx = self.orb['x']
                    orby = self.orb['y']
                    break
                _time.sleep(0.1) #assuming 10Hz of update rate of orbit
            else:
                self._call_callback('Log-Mon','Err: get orbit function timeout.')
                orbx =  self.ref_orbit['x']
                orby =  self.ref_orbit['y']
        refx = self.ref_orbit['x']
        refy = self.ref_orbit['y']
        return _np.hstack([orbx-refx, orby-refy])

    def _on_connection(self,pvname,conn,pv):
        if not conn:
            self._call_callback('Log-Mon','PV '+pvname+'disconnected.')

    def _call_callback(self,pv,value):
        self.callback(self.prefix + pv, value)

    def _set_offline_orbit(self,plane,value):
        self._call_callback('Log-Mon','Setting New Offline Orbit.')
        if len(value) != NR_BPMS:
            self._call_callback('Log-Mon','Err: Wrong Size.')
            return False
        self.offline_orbit[plane] = _np.array(value)
        self._call_callback('OfflineOrbit'+plane.upper()+'-RB', _np.array(value))
        return True

    def _load_basic_orbits(self):
        self.ref_orbit = dict()
        self.golden_orbit = dict()
        for plane in ('x','y'):
            filename = self.REF_ORBIT_FILENAME+plane.upper() + self.EXT
            self.ref_orbit[plane] = _np.zeros(NR_BPMS,dtype=float)
            if _os.path.isfile(filename):
                self.ref_orbit[plane] = _np.loadtxt(filename)
            filename = self.GOLDEN_ORBIT_FILENAME+plane.upper() + self.EXT
            self.golden_orbit[plane] = _np.zeros(NR_BPMS,dtype=float)
            if _os.path.isfile(filename):
                self.golden_orbit[plane] = _np.loadtxt(filename)

    def _save_ref_orbit(self,plane, orb):
        _np.savetxt(self.REF_ORBIT_FILENAME+plane.upper() + self.EXT,orb)

    def _save_golden_orbit(self,plane, orb):
        _np.savetxt(self.GOLDEN_ORBIT_FILENAME+plane.upper() + self.EXT,orb)

    def _reset_orbs(self):
        self.count = 0
        self.orb['x'] = None
        self.orb['y'] = None

    def _update_orbs(self,plane):
        def update(pvname,value,**kwargs):
            if value is None: return True
            orb = _np.array(value, dtype=float)
            self.orbs[plane].append(orb)
            self.orbs[plane] = self.orbs[plane][-self.orbit_points_num:]
            if self.orbit_points_num > 1:
                orb = _np.mean(self.orbs[plane], axis=0)
            else:
                orb = self.orbs[plane][0]
            self._call_callback('OnlineOrbit'+plane.upper()+'-Mon',list(orb))
            if self.correction_mode:
                self._call_callback('CorrOrbit'+plane.upper()+'-Mon',list(orb))
            self.count += 1
            if self.count >= self.orbit_points_num:
                self.orb[plane] = orb
            return True
        return update

    def _set_orbit_points_num(self,num):
        self._call_callback('Log-Mon','Setting new number of points for median.')
        self.orbit_points_num = num
        self._reset_orbs()
        self._call_callback('OrbitPointsNum-RB', num)
        return True

    def _set_ref_orbit(self,plane,orb):
        self._call_callback('Log-Mon','Setting New Reference Orbit.')
        if len(orb) != NR_BPMS:
            self._call_callback('Log-Mon','Err: Wrong Size.')
            return False
        self._save_ref_orbit(plane,orb)
        self.ref_orbit[plane] = _np.array(orb,dtype=float)
        self._reset_orbs()
        self._call_callback('OrbitRef'+plane.upper()+'-RB', orb)
        return True

    def _set_golden_orbit(self,plane,orb):
        self._call_callback('Log-Mon','Setting New Golden Orbit.')
        if len(value) != NR_BPMS:
            self._call_callback('Log-Mon','Err: Wrong Size.')
            return False
        self._save_golden_orbit(plane,orb)
        self.golden_orbit[plane] = _np.array(orb,dtype=float)
        self._call_callback('GoldenOrbit'+plane.upper()+'-RB', orb)
        return True

    def _set_ref_with_golden(self,value):
        self._call_callback('Log-Mon','Golden Orbit --> Reference Orbit.')
        for pl,orb in self.golden_orbit.items():
            self._call_callback('OrbitRef'+pl.upper()+'-SP', orb.copy())
            self._set_ref_orbit(pl,orb.copy())
        return True
