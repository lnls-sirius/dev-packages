import pvs as _pvs
import time as _time
import logging as _log
from siriuspy.timesys.time_data import Connections, Events, Clocks
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers
from hl_classes import get_hl_trigger_object, HL_Event, HL_Clock

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__ = _pvs.__version__
_TIMEOUT = 0.05

def check_triggers_consistency():
    triggers = _get_triggers()
    Connections.add_bbb_info()
    Connections.add_crates_info()
    from_evg = Connections.get_connections_from_evg()
    twds_evg = Connections.get_connections_twds_evg()
    for trig, val in triggers.items():
        chans = {  _PVName(chan) for chan in val['channels']  }
        for chan in chans:
            tmp = twds_evg.get(chan)
            if tmp is None:
                _log.warning('Device '+chan+' defined in the high level trigger '+
                      trig+' not specified in timing connections data.')
                return False
            up_dev = tmp.pop()
            diff_devs = from_evg[up_dev] - chans
            if diff_devs and not chan.dev_type.endswith('BPM'):
                _log.warning('Devices: '+' '.join(diff_devs)+' are connected to the same output of '
                             +up_dev+' as '+chan+' but are not related to the sam trigger ('+trig+').')
                # return False
    return True


class App:

    def get_database(self):
        db = dict()
        db.update(self.correctors.get_database())
        db.update(self.matrix.get_database())
        db.update(self.orbit.get_database())
        return db

    def __init__(self,driver=None):
        _log.info('Starting App...')
        self._driver = driver
        self.orbit = Orbit(prefix = prefix, callback = self._update_driver)
        self.correctors = Correctors(prefix = prefix, callback = self._update_driver)
        self.matrix = Matrix(prefix = prefix, callback = self._update_driver)

        self._database = self.get_database()


    def main_loop(self):

        orb = orbit.get_orbit()
        while self.correct_orbit:
            t0 = _time.time()
            # _log.debug('App: Executing check.')
            dtheta = matrix.get_kicks(orb)
            if self.apply_kicks:
                correctors.apply(dtheta)

            orb = orbit.get_orbit()


            tf = _time.time()
            dt = (tf-t0)
            if dt > 0.2: _log.debug('App: check took {0:f}ms.'.format(dt*1000))
            dt = interval - dt
            if dt>0: _time.sleep(dt)

    def connect(self):
        _log.info('Connecting to Low Level Clocks:')
        for key,val in self._clocks.items(): val.connect()
        _log.info('All Clocks connection opened.')
        _log.info('Connecting to Low Level Events:')
        for key,val in self._events.items(): val.connect()
        _log.info('All Events connection opened.')
        _log.info('Connecting to Low Level Triggers:')
        for key,val in self._triggers.items(): val.connect()
        _log.info('All Triggers connection opened.')

    def _update_driver(self,pvname,value,**kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'.format(pvname,str(value)))
        self._driver.setParam(pvname,value)
        self._driver.updatePVs()

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self,driver):
        _log.debug("Setting App's driver.")
        self._driver = driver

    def process(self,interval):
        t0 = _time.time()
        # _log.debug('App: Executing check.')
        self.check()
        tf = _time.time()
        dt = (tf-t0)
        if dt > 0.2: _log.debug('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt>0: _time.sleep(dt)

    def read(self,reason):
        # _log.debug("PV {0:s} read from App.".format(reason))
        return None # Driver will read from database

    def check(self):
        for ev in self._events.values():
            ev.check()
        for tr in self._triggers.values():
            tr.check()

    def _isValid(self,reason,value):
        if reason.endswith(('-Sts','-RB', '-Mon')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False
        enums = self._database[reason].get('enums')
        if enums is not None:
            len_ = len(enums)
            if int(value) >= len_:
                _log.warning('App: value {0:d} too large for PV {1:s} of type enum'.format(value,reason))
                return False
        return True

    def write(self,reason,value):
        _log.debug('App: Writing PV {0:s} with value {1:s}'.format(reason,str(value)))
        if not self._isValid(reason,value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('App: Write unsuccessful. PV {0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.debug('App: Write complete.')
        else:
            _log.warning('App: Unsuccessful write of PV {0:s}; value = {1:s}.'.format(reason,str(value)))
        return ret_val


TINY_INTERVAL = 0.001

class Orbit:

    REF_ORBIT_FILENAME = 'data/reference_orbit'
    NR_BPMS = 180

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'OrbitRefX-SP'] = {'type':'float','count':self.NR_BPMS,'value'=0,
                                            'set_pv_fun':lambda x: self._set_ref_orbit('x',x)}
        db[pre + 'OrbitRefX-RB'] = {'type':'float','count':self.NR_BPMS,'value'=0}
        db[pre + 'OrbitRefY-SP'] = {'type':'float','count':self.NR_BPMS,'value'=0,
                                            'set_pv_fun':lambda x: self._set_ref_orbit('y',x)}
        db[pre + 'OrbitRefY-RB'] = {'type':'float','count':self.NR_BPMS,'value'=0}
        db[pre+'OrbitAvgNum-SP']= {'type':'int','value'=1,
                                            'set_pv_fun':lambda x: self._set_orbit_avg_num}
        db[pre+'OrbitAvgNum-RB']= {'type':'int','value'=1}


    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.orbs = {'x':[],'y':[]}
        self.orb = {'x':None,'y':None}
        self.acquire = {'x':False,'y':False}
        self.relative = True
        self._load_ref_orbits()
        self.orbit_avg_num = 1
        self.pv ={'x':_epics.PV( 'SI-Glob:AP-Orbit:PosX-Mon', callback=self._update_orbs('x') ),
                  'y':_epics.PV( 'SI-Glob:AP-Orbit:PosY-Mon', callback=self._update_orbs('y') )  }
        if not self.pv['x'].connected or not self.pv['y'].connected:
            raise Exception('Orbit PVs not Connected.')
        if self.pv['x'].count != self.NR_BPMS:
            raise Exception('Orbit length not consistent')

    def _load_ref_orbits(self):
        self.ref_orbit = dict()
        for plane in ('x','y'):
            filename = self.REF_ORBIT_FILENAME+plane.upper()+'.txt'
            self.ref_orbit[plane] = _np.zeros(self.NR_BPMS,dtype=float)
            if os.path.isfile(filename):
                self.ref_orbit[plane] = _np.loadtxt(filename)

    def _save_ref_orbit(self,plane, orb):
        _np.savetxt(self.REF_ORBIT_FILENAME+plane.upper()+'.txt',orb)

    def _reset_orbs(self,plane):
        self.orbs[plane] = []
        self.orb[plane] = None

    def _get_count(self,plane):
        return len(self.orbs[plane])

    def _update_orbs(self,plane):
        def _update(pvname,value,**kwargs):
            if value is None or not self.acquire[plane]: return
            if len(self.orbs[plane]) < self.orbit_avg_num:
                orb = _np.array(value, dtype=float)
                self.orbs[plane].append(orb)
            if len(self.orbs[plane]) == self.orbit_avg_num:
                self.orb[plane] = _np.array(self.orbs[plane]).mean(axis=1)
                if self.relative:
                    self.orb[plane] -= self.ref_orbit[plane]
                self.acquire[plane] = False
        return update

    def _set_orbit_avg_num(self,num):
        self.orbit_avg_num = num
        self._reset_orbs('x')
        self._reset_orbs('y')
        pvname = self.prefix+'OrbitAvgNum-RB'
        self.callback(pvname, num)

    def _set_ref_orbit(self,plane,orb):
        self._save_ref_orbit(plane,orb)
        self.ref_orbit[plane] = _np.array(orb,dtype=float)
        self._reset_orbs(plane)
        pvname = self.prefix+'OrbitRef'+plane.upper()+'-RB'
        self.callback(pvname, orb)

    def get_orbit(self):
        self.acquire = {'x':True,'y':True}
        while any(self.acquire.values()):  _time.sleep(TINY_INTERVAL)
        orbx = self.orb['x']
        orby = self.orb['y']
        self._reset_orbs('x')
        self._reset_orbs('y')
        return orbx, orby

class Matrix:

    RSP_MTX_FILENAME = 'data/response_matrix'
    NR_BPMS = Orbit.NR_BPMS
    NR_CH   = Correctors.NR_CH
    NR_CV   = Correctors.NR_CV
    NR_CORRS = NR_CH + NR_CV + 1
    MTX_SZ = (2*NR_BPMS) * NR_CORRS

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'RSPMatrix-SP'] = {'type':'float','count':self.MTX_SZ,'value'=0,
                                    'unit':'(BH,BV)(nm) x (CH,CV,RF)(urad,Hz)',
                                    'set_pv_fun':lambda x: self._set_resp_matrix(x)}
        db[pre + 'RSPMatrix-RB'] = {'type':'float','count':self.MTX_SZ,'value'=0,
                                    'unit':'(BH,BV)(nm) x (CH,CV,RF)(urad,Hz)'}
        db[pre + 'SingValues-Mon']= {'type':'float','count':self.NR_CORRS,'value'=0,
                                    'unit':'Singular values of the matrix in use'}
        db[pre + 'CHEnblList-SP']= {'type':'int','count':self.NR_CH,'value'=1,
                                    'unit':'CHs used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('ch',x)}
        db[pre + 'CHEnblList-RB']= {'type':'int','count':self.NR_CH,'value'=1,
                                    'unit':'CHs used in correction'}
        db[pre + 'CVEnblList-SP']= {'type':'int','count':self.NR_CV,'value'=1,
                                    'unit':'CVs used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('cv',x)}
        db[pre + 'CVEnblList-RB']= {'type':'int','count':self.NR_CV,'value'=1,
                                    'unit':'CVs used in correction'}
        db[pre + 'BPMxEnblList-SP']= {'type':'int','count':self.NR_BPMS,'value'=1,
                                    'unit':'BPMx used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('bpmx',x)}
        db[pre + 'BPMxEnblList-RB']= {'type':'int','count':self.NR_BPMS,'value'=1,
                                    'unit':'BPMx used in correction'}
        db[pre + 'BPMyEnblList-SP']= {'type':'int','count':self.NR_BPMS,'value'=1,
                                    'unit':'BPMy used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('bpmy',x)}
        db[pre + 'BPMyEnblList-RB']= {'type':'int','count':self.NR_BPMS,'value'=1,
                                    'unit':'BPMy used in correction'}
        db[pre + 'RFEnbl-Sel'] = {'type':'enum','enums':self.RF_ENBL_ENUMS,'value'=0,
                                    'unit':'If RF is used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('rf',x)}
        db[pre + 'RFEnbl-Sts'] = {'type':'enum','enums':self.RF_ENBL_ENUMS,'value'=0,
                                    'unit':'If RF is used in correction'}
        db[pre + 'NumSingValues-SP']= {'type':'int','value'=self.NR_CORRS,
                                    'unit':'Maximum number of SV to use',
                                    'set_pv_fun':lambda x: self._set_num_sing_values(x)}
        db[pre + 'NumSingValues-RB']= {'type':'int','value'=self.NR_CORRS,
                                    'unit':'Maximum number of SV to use'}

    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.selection_configs = {
            'bpmx':_np.ones(self.NR_BPMS,dtype=bool),
            'bpmy':_np.ones(self.NR_BPMS,dtype=bool),
              'ch':_np.ones(self.NR_CH,  dtype=bool),
              'cv':_np.ones(self.NR_CV,  dtype=bool),
              'rf':_np.zeros(False,dtype=bool),
            }
        self.selection_pv_names = {
            'bpmx':'CHEnblList-RB',
            'bpmy':'CVEnblList-RB',
              'ch':'BPMxEnblList-RB',
              'cv':'BPMyEnblList-RB',
              'rf':'RFEnbl-Sts',
            }
        self.num_sing_values = self.NR_CORRS
        self.sing_values = _np.zeros(self.NR_CORRS,dtype=float)
        self._load_response_matrix()

    def _set_enbl_list(self,key,val):
        copy_ = self.selection_configs[key]
        self.selection_configs[key] = _np.array(val,dtype=bool)
        ok_ = self._calc_matrices()
        if not ok_:
            self.selection_configs[key] = copy
            return
        pvname = self.prefix + self.selection_pv_names[key]
        self.callback(pvname,val)

    def _calc_matrices(self):
        selecbpm = _np.hstack([ self.selection_configs['bpmx'],
                                self.selection_configs['bpmy'] ]  )
        seleccor = _np.hstack([ self.selection_configs['ch'],
                                self.selection_configs['cv'],
                                self.selection_configs['rf'] ]  )
        if not any(selecbpm) or not any(seleccor):
            return False
        mat = self.response_matrix[selecbpm,seleccor]
        U, s, V = _np.linalg.svd(mat, full_matrices = False)
        inv_s = 1/s
        inv_s[self.num_sing_values:] = 0
        Inv_S = np.diag(inv_s)
        self.inv_response_matrix = _np.dot(  _np.dot( V.T, Inv_S ),  U.T  )
        self.sing_values[:] = 0
        self.sing_values[:len(s)] = s
        pvname = self.prefix + 'SingValues-Mon'
        self.callback(pvname,list(self.sing_values))
        return True

    def _set_num_sing_values(self,num):
        self.num_sing_values = num
        pvname = self.prefix + 'NumSingValues-RB'
        self.callback(pvname,num)

    def _load_response_matrix(self):
        filename = self.RSP_MTX_FILENAME+'.txt'
        if os.path.isfile(filename):
            self.response_matrix = _np.loadtxt(filename)
            self._calc_matrices()
            pvname = self.prefix + 'RSPMatrix-RB'
            self.callback(pvname,list(self.response_matrix.flatten()))

    def _save_ref_orbit(self, mat):
        _np.savetxt(self.RSP_MTX_FILENAME+'.txt',mat)

    def _reset_orbs(self,plane):
        self.orbs[plane] = []
        self.orb[plane] = None

    def _get_count(self,plane):
        return len(self.orbs[plane])

    def _update_orbs(self,plane):
        def _update(pvname,value,**kwargs):
            if value is None or not self.acquire[plane]: return
            if len(self.orbs[plane]) < self.orbit_avg_num:
                orb = _np.array(value, dtype=float)
                self.orbs[plane].append(orb)
            if len(self.orbs[plane]) == self.orbit_avg_num:
                self.orb[plane] = _np.array(self.orbs[plane]).mean(axis=1)
                if self.relative:
                    self.orb[plane] -= self.ref_orbit[plane]
                self.acquire[plane] = False
        return update

    def _set_orbit_avg_num(self,num):
        self.orbit_avg_num = num
        self._reset_orbs('x')
        self._reset_orbs('y')
        pvname = self.prefix+'OrbitAvgNum-RB'
        self.callback(pvname, num)

    def _set_ref_orbit(self,plane,orb):
        self._save_ref_orbit(plane,orb)
        self.ref_orbit[plane] = _np.array(orb,dtype=float)
        self._reset_orbs(plane)
        pvname = self.prefix+'OrbitRef'+plane.upper()+'-RB'
        self.callback(pvname, orb)

    def get_orbit(self):
        self.acquire = {'x':True,'y':True}
        while any(self.acquire.values()):  _time.sleep(TINY_INTERVAL)
        orbx = self.orb['x']
        orby = self.orb['y']
        self._reset_orbs('x')
        self._reset_orbs('y')
        return orbx, orby


class BPMs:

    def get_bpms_device_names(self):
        return ordered_list_bpm_names

    def _on_monitor_change(self,pvname,value,**kwargs):


    def get_orbit(self):
        self.reset_count()
        while True:
            for i, bpm in enumerate(self.bpms):
                if self.count[i]
