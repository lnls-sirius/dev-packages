import pvs as _pvs
import time as _time
from threading import Thread as _Thread
import logging as _log
from siriuspy.timesys.time_data import Connections, Events, Clocks
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.pwrsupply import psdata as _psdata
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

TINY_INTERVAL = 0.001

NR_BPMS  = 180
NR_CH    = 120
NR_CV    = 160
NR_CORRS = NR_CH + NR_CV + 1
MTX_SZ   = (2*NR_BPMS) * NR_CORRS
DANG = 1E-3
DFREQ = 100
SECTION = 'SI'
LL_PREF = 'VAF-'

class App:

    def get_database(self):
        db = dict()
        pre = self.prefix
        db.update(self.correctors.get_database())
        db.update(self.matrix.get_database())
        db.update(self.orbit.get_database())
        db[pre + 'AutoCorrState-Sel'] = {'type':'enum','enums':('Off','On'),value=0,
                                   'set_pv_fun':self._toggle_auto_corr}
        db[pre + 'AutoCorrState-Sts'] = {'type':'enum','enums':('Off','On'),value=0}
        db[pre + 'AutoCorrFreq-SP']   = {'type':float,'value':1,
                                         'set_pv_fun':self._set_auto_corr_frequency}
        db[pre + 'AutoCorrFreq-SP']    = {'type':float,'value':1}
        db[pre + 'StartMeasRSPMtx-Cmd']  = {'type':'int',value=0,'set_pv_fun':self._start_measure_response_matrix}
        db[pre + 'AbortMeasRSPMtx-Cmd']  = {'type':'int',value=0,'set_pv_fun':self._abort_measure_response_matrix}
        db[pre + 'ResetMeasRSPMtx-Cmd']  = {'type':'int',value=0,'set_pv_fun':self._reset_measure_response_matrix}
        db[pre + 'MeasRSPMtxState-Sts']  = {'type':'enum','enums':('Idle','Measuring','Completed','Aborted'),value=1}
        db[pre + 'CorrectionMode-Sel'] = {'type':'enum','enums':('OffLine','Online'),value=1,
                                          'unit':'Defines is correction is offline or online',
                                          'set_pv_fun':self._toggle_correction_mode}
        db[pre + 'CorrectionMode-Sts'] = {'type':'enum','enums':('OffLine','Online'),value=1,
                                          'unit':'Defines is correction is offline or online'}
        db[pre + 'CalcCorr-Cmd']     = {'type':'int',value=0,'unit':'Calculate kicks',
                                        'set_pv_fun':self._calc_correction}
        db[pre + 'ApplyKicks-Cmd']   = {'type':'enum','enums':('CH','CV','RF','All'),value=0,
                                        'unit':'Apply last calculated kicks.',
                                        'set_pv_fun':lambda x: self._apply_kicks(x)}
        return db

    def __init__(self,driver=None):
        _log.info('Starting App...')
        self._driver = driver
        self.prefix = SECTION+'-Glob:AP-SOFB:'
        self.orbit = Orbit(prefix = self.prefix, callback = self._update_driver)
        self.correctors = Correctors(prefix = self.prefix, callback = self._update_driver)
        self.matrix = Matrix(prefix = self.prefix, callback = self._update_driver)
        self.auto_corr = 0
        self.auto_corr_freq = 1
        self.correction_mode = 1
        self.dtheta = None
        self._thread = None
        self._database = self.get_database()

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self,driver):
        _log.debug("Setting App's driver.")
        self._driver = driver

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

    def process(self,interval):
        t0 = _time.time()
        # _log.debug('App: Executing check.')
        # self.check()
        tf = _time.time()
        dt = (tf-t0)
        if dt > 0.2: _log.debug('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt>0: _time.sleep(dt)

    def connect(self):
        _log.info('Connecting to Orbit PVs:')
        self.orbit.connect()
        _log.info('All Orbit connection opened.')
        _log.info('Connecting to Correctors PVs:')
        self.correctors.connect()
        _log.info('All Correctors connection opened.')

    def _call_callback(self,pv,value):
        self._update_driver(self.prefix + pv, value)

    def _abort_measure_response_matrix(self, value):
        if not self.measuring_resp_matrix:
            self._call_callback('Error-Mon','No Measurement ocurring.')
            return
        self.measuring_resp_matrix = False
        self._thread.join()

    def _reset_measure_response_matrix(self,value):
        if self.measuring_resp_matrix:
            self._call_callback('Error-Mon','Cannot Reset, Measurement in process.')
            return
        self._call_callback('MeasRSPMtxState-Sts',0)

    def _start_measure_response_matrix(self,value):
        if self.measuring_resp_matrix:
            self._call_callback('Error-Mon','Measurement already in process.')
            return
        if self._thread and self._thread.isAlive():
            self._call_callback( 'Error-Mon','Cannot Measure, AutoCorr is On.')
            return
        self.masuring_resp_matrix = True
        self._thread = _Thread(target=self._measure_response_matrix)
        self._thread.start()

    def _measure_response_matrix(self):
        self._call_callback('MeasRSPMtxState-Sts',1)
        mat = _np.zeros(2*NR_BPMS,NR_CORRS)
        for i in range(NR_CORRS):
            if not self.measuring_resp_matrix:
                self._call_callback('MeasRSPMtxState-Sts',3)
                return
            delta = DANG if i<NR_CORRS-1 else DFREQ
            kicks = _np.zeros(NR_CORRS)
            kicks[i] = delta/2
            self.correctors.apply_kicks(kicks)
            orbp = self.orbit.get_orbit()
            kicks[i] = -delta
            self.correctors.apply_kicks(kicks)
            orbn = self.orbit.get_orbit()
            kicks[i] = delta/2
            self.correctors.apply_kicks(kicks)
            mat[:,i] = (orbp-orbn)/delta
        self.matrix.set_resp_matrix(list(mat.flatten()))
        self._call_callback('MeasRSPMtxState-Sts',2)
        self.measuring_resp_matrix = False
        return

    def _toggle_auto_corr(self,value):
        if self.auto_corr:
            self._call_callback( 'Error-Mon','AutoCorr is Already On.')
            return
        if self._thread and self._thread.isAlive():
            self._call_callback( 'Error-Mon','Cannot Correct, Measuring RSPMtx.')
            return
        self.auto_corr = value
        if self.auto_corr:
            self._thread = _Thread(target=self._automatic_correction)
            self._thread.start()

    def _automatic_correction(self):
        if not self.correction_mode:
            self._update_driver( 'Error-Mon','Error in AutoCorr: Offline Correction')
            self._update_driver(self.prefix + 'AutoCorrState-Sel',0)
            self._update_driver(self.prefix + 'AutoCorrState-Sts',0)
            return
        self._update_driver(self.prefix + 'AutoCorrState-Sts',1)
        while self.auto_corr:
            t0 = _time.time()
            orb = self.orbit.get_orbit()
            self.dtheta = self.matrix.calc_kicks(orb)
            correctors.apply_kicks(dtheta)
            tf = _time.time()
            dt = (tf-t0)
            interval = 1/self.auto_corr_freq
            if dt > interval: _log.debug('App: check took {0:f}ms.'.format(dt*1000))
            dt = inteval - dt
            if dt>0: _time.sleep(dt)
        self._update_driver(self.prefix + 'AutoCorrState-Sts',0)

    def _toggle_correction_mode(self,value):
        self.correction_mode = value
        self._call_callback( 'CorrectionMode-Sts',value)
        self.orbit.get_orbit(value)

    def _set_auto_corr_frequency(self,value):
        self.auto_corr_freq = value

    def _calc_correction(self,value):
        if self._thread and self._thread.isAlive():
            self._update_driver( 'Error-Mon','AutoCorr or MeasRSPMtx is On.')
            return
        orb = self.orbit.get_orbit(self.correction_mode)
        self.dtheta = self.matrix.calc_kicks(orb)

    def _apply_kicks(self,code):
        if not self.correction_mode:
            self._call_callback( 'Error-Mon','Cannot apply kicks. Offline Correction')
            return
        if self._thread and self._thread.isAlive():
            self._call_callback( 'Error-Mon','AutoCorr or MeasRSPMtx is On.')
            return
        kicks = self.dtheta.copy()
        if code == 1:
            kicks[NR_CH:] = 0
        elif code == 2:
            kicks[:NR_CH] = 0
            kicks[-1] = 0
        elif code == 3:
            kicks[:-1] = 0
        if any(kicks):
            self.correctors.apply_kicks(kicks)

    def _update_driver(self,pvname,value,**kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'.format(pvname,str(value)))
        self._driver.setParam(pvname,value)
        self._driver.updatePVs()

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


class Orbit:

    REF_ORBIT_FILENAME = 'data/reference_orbit'
    GOLDEN_ORBIT_FILENAME = 'data/golden_orbit'
    EXT = '.siorb'

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'OrbitRefX-SP'] = {'type':'float','count':NR_BPMS,'value'=0,
                                    'set_pv_fun':lambda x: self._set_ref_orbit('x',x)}
        db[pre + 'OrbitRefX-RB'] = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'OrbitRefY-SP'] = {'type':'float','count':NR_BPMS,'value'=0,
                                    'set_pv_fun':lambda x: self._set_ref_orbit('y',x)}
        db[pre + 'OrbitRefY-RB'] = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'GoldenOrbitX-SP'] = {'type':'float','count':NR_BPMS,'value'=0,
                                    'set_pv_fun':lambda x: self._set_golden_orbit('x',x)}
        db[pre + 'GoldenOrbitX-RB'] = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'GoldenOrbitY-SP'] = {'type':'float','count':NR_BPMS,'value'=0,
                                    'set_pv_fun':lambda x: self._set_golden_orbit('y',x)}
        db[pre + 'GoldenOrbitY-RB'] = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'setRefwithGolden-Cmd'] = {'type':'int',value=0,'unit':'Set the reference orbit with the Golden Orbit',
                                        'set_pv_fun':self._set_ref_with_golden}
        db[pre + 'OrbitX-Mon']      = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'OrbitY-Mon']      = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'OfflineOrbitX-SP'] = {'type':'float','count':NR_BPMS,'value'=0,
                                        'set_pv_fun':lambda x: self._set_offline_orbit('x',x)}
        db[pre + 'OfflineOrbitX-RB'] = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'OfflineOrbitY-SP'] = {'type':'float','count':NR_BPMS,'value'=0,
                                        'set_pv_fun':lambda x: self._set_offline_orbit('y',x)}
        db[pre + 'OfflineOrbitY-RB'] = {'type':'float','count':NR_BPMS,'value'=0}
        db[pre + 'OrbitAvgNum-SP']   = {'type':'int','value'=1,'unit':'number of averages',
                                        'set_pv_fun':self._set_orbit_avg_num}
        db[pre + 'OrbitAvgNum-RB']   = {'type':'int','value'=1,'unit':'number of averages'}

    def __init__(self,prefix,callback):
        self._call_callback = callback
        self.prefix = prefix
        self.orbs = {'x':[],'y':[]}
        self.orb = {'x':None,'y':None}
        self.offline_orbit = {'x':_np.zeros(NR_BPMS),'y':_np.zeros(NR_BPMS)}
        self.acquire = {'x':False,'y':False}
        self.relative = True
        self._load_basic_orbits()
        self.orbit_avg_num = 1
        self.pv = {'x':None, 'y':None}

    def connect(self):
        self.pv ={'x':_epics.PV(SECTION + '-Glob:AP-Orbit:PosX-Mon',
                                callback=self._update_orbs('x'),
                                connection_callback= self._on_connection ),
                  'y':_epics.PV(SECTION + '-Glob:AP-Orbit:PosY-Mon',
                                callback=self._update_orbs('y'),
                                connection_callback= self._on_connection )  }
        if not self.pv['x'].connected or not self.pv['y'].connected:
            raise Exception('Orbit PVs not Connected.')
        if self.pv['x'].count != NR_BPMS:
            raise Exception('Orbit length not consistent')

    def get_orbit(self, mode):
        if not mode:
            orbx = self.offline_orbit['x']
            orby = self.offline_orbit['y']
        else:
            self.acquire = {'x':True,'y':True}
            while any(self.acquire.values()):  _time.sleep(TINY_INTERVAL)
            orbx = self.orb['x']
            orby = self.orb['y']
            self._reset_orbs('x')
            self._reset_orbs('y')
        self._call_callback( 'OrbitX-Mon',list(orbx))
        self._call_callback( 'OrbitY-Mon',list(orby))
        return _np.hstack([orbx, orby])

    def _on_connection(self,pvname,conn,pv):
        if not conn:
            self._call_callback('Error-Mon','PV '+pvname+'disconnected.')

    def _call_callback(self,pv,value):
        self.callback(self.prefix + pv, value)

    def _set_offline_orbit(self,plane,value):
        self.offline_orbit[plane] = _np.array(value)

    def _load_basic_orbits(self):
        self.ref_orbit = dict()
        self.golden_orbit = dict()
        for plane in ('x','y'):
            filename = self.REF_ORBIT_FILENAME+plane.upper() + self.EXT
            self.ref_orbit[plane] = _np.zeros(NR_BPMS,dtype=float)
            if os.path.isfile(filename):
                self.ref_orbit[plane] = _np.loadtxt(filename)
            filename = self.GOLDEN_ORBIT_FILENAME+plane.upper() + self.EXT
            self.golden_orbit[plane] = _np.zeros(NR_BPMS,dtype=float)
            if os.path.isfile(filename):
                self.golden_orbit[plane] = _np.loadtxt(filename)

    def _save_ref_orbit(self,plane, orb):
        _np.savetxt(self.REF_ORBIT_FILENAME+plane.upper() + self.EXT,orb)

    def _save_golden_orbit(self,plane, orb):
        _np.savetxt(self.GOLDEN_ORBIT_FILENAME+plane.upper() + self.EXT,orb)

    def _reset_orbs(self,plane):
        self.orbs[plane] = []
        self.orb[plane] = None

    def _update_orbs(self,plane):
        def update(pvname,value,**kwargs):
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
        self._call_callback('OrbitAvgNum-RB', num)

    def _set_ref_orbit(self,plane,orb):
        self._save_ref_orbit(plane,orb)
        self.ref_orbit[plane] = _np.array(orb,dtype=float)
        self._reset_orbs(plane)
        self._call_callback('OrbitRef'+plane.upper()+'-RB', orb)

    def _set_golden_orbit(self,plane,orb):
        self._save_golden_orbit(plane,orb)
        self.golden_orbit[plane] = _np.array(orb,dtype=float)
        self._call_callback('GoldenOrbit'+plane.upper()+'-RB', orb)

    def _set_ref_with_golden(self,value):
        for pl,orb in self.golden_orbit.items():
            self._call_callback('OrbitRef'+pl.upper()+'-SP', orb.copy())
            self._set_ref_orbit(pl,orb.copy())

class Matrix:

    RSP_MTX_FILENAME = 'data/response_matrix'

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'RSPMatrix-SP'] = {'type':'float','count':MTX_SZ,'value'=0,
                                    'unit':'(BH,BV)(nm) x (CH,CV,RF)(urad,Hz)',
                                    'set_pv_fun':lambda x: self.set_resp_matrix(x)}
        db[pre + 'RSPMatrix-RB'] = {'type':'float','count':MTX_SZ,'value'=0,
                                    'unit':'(BH,BV)(nm) x (CH,CV,RF)(urad,Hz)'}
        db[pre + 'SingValues-Mon']= {'type':'float','count':NR_CORRS,'value'=0,
                                    'unit':'Singular values of the matrix in use'}
        db[pre + 'InvRSPMatrix-Mon']= {'type':'float','count':MTX_SZ,'value'=0,
                                    'unit':'(CH,CV,RF)(urad,Hz) x (BH,BV)(nm)'}
        db[pre + 'CHEnblList-SP']= {'type':'int','count':NR_CH,'value'=1,
                                    'unit':'CHs used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('ch',x)}
        db[pre + 'CHEnblList-RB']= {'type':'int','count':NR_CH,'value'=1,
                                    'unit':'CHs used in correction'}
        db[pre + 'CVEnblList-SP']= {'type':'int','count':NR_CV,'value'=1,
                                    'unit':'CVs used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('cv',x)}
        db[pre + 'CVEnblList-RB']= {'type':'int','count':NR_CV,'value'=1,
                                    'unit':'CVs used in correction'}
        db[pre + 'BPMxEnblList-SP']= {'type':'int','count':NR_BPMS,'value'=1,
                                    'unit':'BPMx used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('bpmx',x)}
        db[pre + 'BPMxEnblList-RB']= {'type':'int','count':NR_BPMS,'value'=1,
                                    'unit':'BPMx used in correction'}
        db[pre + 'BPMyEnblList-SP']= {'type':'int','count':NR_BPMS,'value'=1,
                                    'unit':'BPMy used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('bpmy',x)}
        db[pre + 'BPMyEnblList-RB']= {'type':'int','count':NR_BPMS,'value'=1,
                                    'unit':'BPMy used in correction'}
        db[pre + 'RFEnbl-Sel'] = {'type':'enum','enums':self.RF_ENBL_ENUMS,'value'=0,
                                    'unit':'If RF is used in correction',
                                    'set_pv_fun':lambda x: self._set_enbl_list('rf',x)}
        db[pre + 'RFEnbl-Sts'] = {'type':'enum','enums':self.RF_ENBL_ENUMS,'value'=0,
                                    'unit':'If RF is used in correction'}
        db[pre + 'NumSingValues-SP']= {'type':'int','value'=NR_CORRS,
                                    'unit':'Maximum number of SV to use',
                                    'set_pv_fun':lambda x: self._set_num_sing_values(x)}
        db[pre + 'NumSingValues-RB']= {'type':'int','value'=NR_CORRS,
                                    'unit':'Maximum number of SV to use'}
        db[pre + 'CHCalcdKicks-Mon']= {'type':'float','count':NR_CH,'value'=0,'unit':'Last CH kicks calculated.'}
        db[pre + 'CVCalcdKicks-Mon']= {'type':'float','count':NR_CV,'value'=0,'unit':'Last CV kicks calculated.'}
        db[pre + 'RFCalcdKicks-Mon']= {'type':'float','value'=1,'unit':'Last RF kick calculated.'}

    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.select_items = {
            'bpmx':_np.ones(NR_BPMS,dtype=bool),
            'bpmy':_np.ones(NR_BPMS,dtype=bool),
              'ch':_np.ones(NR_CH,  dtype=bool),
              'cv':_np.ones(NR_CV,  dtype=bool),
              'rf':_np.zeros(False,dtype=bool),
            }
        self.selection_pv_names = {
              'ch':'CHEnblList-RB',
              'cv':'CVEnblList-RB',
            'bpmx':'BPMxEnblList-RB',
            'bpmy':'BPMyEnblList-RB',
              'rf':'RFEnbl-Sts',
            }
        self.num_sing_values = NR_CORRS
        self.sing_values = _np.zeros(NR_CORRS,dtype=float)
        self.response_matrix = _np.zeros(2*NR_BPMS,NR_CORRS)
        self.inv_response_matrix = _np.zeros(2*NR_BPMS,NR_CORRS).T
        self._load_response_matrix()

    def set_resp_matrix(self,mat):
        mat = _np.reshape(mat,[2*NR_BPMS,NR_CORRS])
        old_ = self.response_matrix.copy()
        self.response_matrix = mat
        if not self._calc_matrices():
            self.response_matrix = old_
            return
        self._save_resp_matrix(mat)
        self._call_callback('RSPMatrix-RB',list(self.response_matrix.flatten()))

    def calc_kicks(self,orbit):
        kicks = _np.dot(-self.inv_respm,orbit)
        self._call_callback('CHCalcdKicks-Mon',list(kicks[:NR_CH]))
        self._call_callback('CVCalcdKicks-Mon',list(kicks[NR_CH:NR_CH+NR_CV]))
        self._call_callback('RFCalcdKicks-Mon',kicks[-1])
        return kicks

    def _call_callback(self,pv,value):
        self.callback(self.prefix + pv, value)

    def _set_enbl_list(self,key,val):
        copy_ = self.select_items[key]
        self.select_items[key] = _np.array(val,dtype=bool)
        if not self._calc_matrices():
            self.select_items[key] = copy_
            return
        self.call_callback(self.selection_pv_names[key],val)

    def _calc_matrices(self):
        sel_ = self.select_items
        selecbpm = _np.hstack(  [  sel_['bpmx'],  sel_['bpmy']  ]    )
        seleccor = _np.hstack(  [  sel_['ch'],    sel_['cv'],  sel_['rf']  ]   )
        if not any(selecbpm):
            self._call_callback('Error-Mon','No BPM selected in EnblList')
            return False
        if not any(seleccor):
            self._call_callback('Error-Mon','No Corrector selected in EnblList')
            return False
        sel_mat = selecbpm[:,None] * seleccor[None,:]
        mat = self.response_matrix[sel_mat]
        mat = _np.reshape(mat,[sum(selecbpm),sum(seleccor)])
        try:
            U, s, V = _np.linalg.svd(mat, full_matrices = False)
        except _np.linalg.LinAlgError():
            self._call_callback('Error-Mon','Could not calculate SVD')
            return False
        inv_s = 1/s
        inv_s[self.num_sing_values:] = 0
        Inv_S = _np.diag(inv_s)
        inv_mat = _np.dot(  _np.dot( V.T, Inv_S ),  U.T  )
        valid_ = _np.any(   _np.bitwise_or( _np.isnan(inv_mat), _np.isinf(inv_mat) )   )
        if not valid_:
            self._call_callback('Error-Mon','Pseudo inverse contains nan or inf.')
            return False

        self.sing_values[:] = 0
        self.sing_values[:len(s)] = s
        self._call_callback('SingValues-Mon',list(self.sing_values))
        self.inv_response_matrix = _np.zeros(2*NR_BPMS,NR_CORRS).T
        self.inv_response_matrix[sel_mat.T] = inv_mat.flatten()
        self._call_callback('InvRSPMatrix-Mon',list(self.inv_response_matrix.flatten()))
        return True

    def _set_num_sing_values(self,num):
        copy_ = self.num_sing_values
        self.num_sing_values = num
        if not self._calc_matrices():
            self.num_sing_values = copy_
            return
        self._call_callback('NumSingValues-RB',num)

    def _load_response_matrix(self):
        filename = self.RSP_MTX_FILENAME+'.txt'
        if os.path.isfile(filename):
            copy_ = self.response_matrix.copy()
            self.response_matrix = _np.loadtxt(filename)
            if not self._calc_matrices():
                self.response_matrix = copy_
                return
            self._call_callback('RSPMatrix-RB',list(self.response_matrix.flatten()))

    def _save_resp_matrix(self, mat):
        _np.savetxt(self.RSP_MTX_FILENAME+'.txt',mat)


class Correctors:
    SLOW_REF = 0
    SLOW_REF_SYNC = 1

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'CHStrength-SP'] = {'type':float,'value':0,'unit'='%',
                                    'set_pv_fun':lambda x:self._set_strength('ch',x)}
        db[pre + 'CHStrength-RB'] = {'type':float,'value':0,'unit'='%'}
        db[pre + 'CVStrength-SP'] = {'type':float,'value':0,'unit'='%',
                                    'set_pv_fun':lambda x:self._set_strength('cv',x)}
        db[pre + 'CVStrength-RB'] = {'type':float,'value':0,'unit'='%'}
        db[pre + 'RFStrength-SP'] = {'type':float,'value':0,'unit'='%',
                                    'set_pv_fun':lambda x:self._set_strength('rf',x)}
        db[pre + 'RFStrength-RB'] = {'type':float,'value':0,'unit'='%'}
        db[pre + 'SyncKicks-Sel'] = {'type':'enum','enums':('Off','On'),value=1,
                                     'set_pv_fun':self._set_corr_pvs_mode}
        db[pre + 'SyncKicks-Sts'] = {'type':'enum','enums':('Off','On'),value=1}

    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.strengths = {  'ch':0.0, 'cv':0.0, 'rf':0.0  }
        self.sync_kicks = True
        self.corr_pvs_opmode_sel = list()
        self.corr_pvs_opmode_sts = list()
        self.corr_pvs_opmode_ready = dict()
        self.corr_pvs_sp = list()
        self.corr_pvs_rb = list()
        self.corr_pvs_ready = dict()

    def connect(self):
        _psdata.clear_filter()
        _psdata.add_filter(discipline='PS',device='CH',section=SECTION,sub_section='.*')
        ch_names = _psdata.get_filtered_names()
        _psdata.clear_filter()
        _psdata.add_filter(discipline='PS',device='CV',section=SECTION,sub_section='.*')
        cv_names = _psdata.get_filtered_names()
        ma_names = ch_names + cv_names

        for dev in ma_names:
            self.corr_pvs_opmode_sel.append(_epics.PV(LL_PREF+dev+':OpMode-Sel',
                                                      connection_timeout=_TIMEOUT))
            self.corr_pvs_opmode_sts.append(_epics.PV(LL_PREF+dev+':OpMode-Sts',
                                            connection_timeout=_TIMEOUT,
                                            callback=self._corrIsOnMode))
            self.corr_pvs_opmode_ready[LL_PREF+dev+':OpMode-Sts'] = False
            self.corr_pvs_sp.append(_epics.PV(LL_PREF+dev+':Current-SP',
                                              connection_timeout=_TIMEOUT,))
            self.corr_pvs_rb.append(_epics.PV(LL_PREF+dev+':Current-RB',
                                    connection_timeout=_TIMEOUT,
                                    callback=self._corrIsReady))
            self.corr_pvs_ready[LL_PREF+dev+':Current-RB'] = False
        self.rf_pv_sp = _eptics.PV(LL_PREF+SECTION + '-Glob:RF-P5Cav:Freq-SP')
        self.rf_pv_rb = _eptics.PV(LL_PREF+SECTION + '-Glob:RF-P5Cav:Freq-RB')
        self.event_pv_mode_sel = _epics.PV(SECTION + '-Glob:TI-Event:OrbitMode-Sel')
        self.event_pv_sp = _epics.PV(SECTION + '-Glob:TI-Event:OrbitExtTrig-Cmd')

    def apply_kicks(self,values):
        if values[-1]:
            if self.rf_pv_sp.connected:
                self.rf_pv_sp.value = self.rf_pv_sp.value + self.strengths['rf']*values[-1]
            else:
                self._call_callback('Error-Mon','PV '+self.rf_pv_sp.pvname+' Not Connected.')
        for i, pv in enumerate(self.corr_pvs_sp):
            pvname = pv.pvname.replace('-SP','-RB')
            self.pvs_ready[pvname] = True
            if not values[i]: continue
            if not pv.connected:
                self._call_callback('Error-Mon','PV '+pv.pvname+' Not Connected.')
                continue
            plane = 'ch' if i>=NR_CH else 'cv'
            self.pvs_ready[pvname] = False
            pv.value = pv.value + self.strengths[plane] * values[i]
        while not all(self.pvs_ready.values()):
            _time.sleep(TINY_INTERVAL)
        if self.sync_kicks:
            if self.event_pv_sp.connected:
                self.event_pv_sp.value = 1
            else:
                self._call_callback('Error-Mon','Kicks not sent, Timing PV Disconnected.')

    def _call_callback(self,pv,value):
        self.callback(self.prefix + pv, value)

    def _set_strength(self,plane,value):
        self.strengths[plane] = value/100
        self._call_callback(plane.upper() + 'Strength-RB', value)

    def _set_corr_pvs_mode(self,value):
        self.sync_kicks = True if value else False
        val = self.SLOW_REF_SYNC if self.sync_kicks else self.SLOW_REF
        for pv in self.corr_pvs_opmode_sel:
            pv.value = val

    def _corrIsReady(self,pvname,value,**kwargs):
        self.corr_pvs_ready[pvname] = True

    def _corrIsOnMode(self,pvname,value,**kwargs):
        val = self.SLOW_REF_SYNC if self.sync_kicks else self.SLOW_REF
        self.corr_pvs_opmode_ready[pvname] = (value == val)
        if all(self.corr_pvs_opmode_ready.values()):
            self._call_callback('SyncKicks-Sts',val == self.SLOW_REF_SYNC)

class BPMs:

    def get_bpms_device_names(self):
        return ordered_list_bpm_names

    def _on_monitor_change(self,pvname,value,**kwargs):


    def get_orbit(self):
        self.reset_count()
        while True:
            for i, bpm in enumerate(self.bpms):
                if self.count[i]
