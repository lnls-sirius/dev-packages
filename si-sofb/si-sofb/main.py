import time as _time
import numpy as _np
from threading import Thread as _Thread
import logging as _log
from matrix import Matrix
from orbit import Orbit
from correctors import Correctors

with open('VERSION') as f:
    __version__ = f.read()
_TIMEOUT = 0.05

NR_BPMS  = 160
NR_CH    = 120
NR_CV    = 160
NR_CORRS = NR_CH + NR_CV + 1
DANG = 2E-1
DFREQ = 200
SECTION = 'SI'
LL_PREF = 'VAF-'

class App:

    def get_database(self):
        db = dict()
        pre = self.prefix
        db.update(self.correctors.get_database())
        db.update(self.matrix.get_database())
        db.update(self.orbit.get_database())
        db[pre + 'Log-Mon'] = {'type':'string','value':''}
        db[pre + 'AutoCorrState-Sel'] = {'type':'enum','enums':('Off','On'),'value':0,
                                         'fun_set_pv':self._toggle_auto_corr}
        db[pre + 'AutoCorrState-Sts'] = {'type':'enum','enums':('Off','On'),'value':0}
        db[pre + 'AutoCorrFreq-SP']   = {'type':'float','value':1,'lolim':1e-3, 'hilim':20,'unit':'Hz',
                                         'prec':3, 'fun_set_pv':self._set_auto_corr_frequency}
        db[pre + 'AutoCorrFreq-RB']    = {'type':'float','value':1,'prec':2, 'unit':'Hz'}
        db[pre + 'StartMeasRSPMtx-Cmd']  = {'type':'int','value':0,'fun_set_pv':self._start_measure_response_matrix}
        db[pre + 'AbortMeasRSPMtx-Cmd']  = {'type':'int','value':0,'fun_set_pv':self._abort_measure_response_matrix}
        db[pre + 'ResetMeasRSPMtx-Cmd']  = {'type':'int','value':0,'fun_set_pv':self._reset_measure_response_matrix}
        db[pre + 'MeasRSPMtxState-Sts']  = {'type':'enum','enums':('Idle','Measuring','Completed','Aborted'),'value':0}
        db[pre + 'CorrectionMode-Sel'] = {'type':'enum','enums':('OffLine','Online'),'value':1,
                                          'unit':'Defines is correction is offline or online',
                                          'fun_set_pv':self._toggle_correction_mode}
        db[pre + 'CorrectionMode-Sts'] = {'type':'enum','enums':('OffLine','Online'),'value':1,
                                          'unit':'Defines is correction is offline or online'}
        db[pre + 'CalcCorr-Cmd']     = {'type':'int','value':0,'unit':'Calculate kicks',
                                        'fun_set_pv':self.calc_correction}
        db[pre + 'CHStrength-SP'] = {'type':'float','value':0,'unit':'%','lolim':-1000, 'hilim':1000,
                                    'prec':2, 'fun_set_pv':lambda x:self._set_strength('ch',x)}
        db[pre + 'CHStrength-RB'] = {'type':'float','value':0,'prec':2, 'unit':'%'}
        db[pre + 'CVStrength-SP'] = {'type':'float','value':0,'unit':'%','lolim':-1000, 'hilim':1000,
                                    'prec':2, 'fun_set_pv':lambda x:self._set_strength('cv',x)}
        db[pre + 'CVStrength-RB'] = {'type':'float','value':0,'prec':2, 'unit':'%'}
        db[pre + 'RFStrength-SP'] = {'type':'float','value':0,'unit':'%','lolim':-1000, 'hilim':1000,
                                    'prec':2, 'fun_set_pv':lambda x:self._set_strength('rf',x)}
        db[pre + 'RFStrength-RB'] = {'type':'float','value':0,'prec':2, 'unit':'%'}
        db[pre + 'MaxKickStrength-SP'] =  {'type':'float','value':300,'unit':'urad','lolim':0, 'hilim':1000,
                                    'prec':3, 'fun_set_pv':self._set_max_kick}
        db[pre + 'MaxKickStrength-RB'] = {'type':'float','value':300,'prec':2, 'unit':'urad'}
        db[pre + 'ApplyKicks-Cmd']   = {'type':'enum','enums':('CH','CV','RF','All'),'value':0,
                                        'unit':'Apply last calculated kicks.',
                                        'fun_set_pv':self._apply_kicks}
        return db

    def __init__(self,driver=None):
        _log.info('Starting App...')
        self._driver = driver
        self.prefix = SECTION+'-Glob:AP-SOFB:'
        self.orbit = Orbit(prefix = self.prefix, callback = self._update_driver)
        self.correctors = Correctors(prefix = self.prefix, callback = self._update_driver)
        self.matrix = Matrix(prefix = self.prefix, callback = self._update_driver)
        self.auto_corr = 0
        self.measuring_resp_matrix = False
        self.auto_corr_freq = 1
        self.correction_mode = 1
        self.strengths = {  'ch':0.0, 'cv':0.0, 'rf':0.0  }
        self._max_kick = 300
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
        self._call_callback('Log-Mon', 'Connecting to Low Level PVs')
        self.orbit.connect()
        _log.info('All Orbit connection opened.')
        self.matrix.connect()
        _log.info('Connecting to Correctors PVs:')
        self.correctors.connect()
        _log.info('All Correctors connection opened.')

    def _call_callback(self,pv,value):
        self._update_driver(self.prefix + pv, value)

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

    def _abort_measure_response_matrix(self, value):
        if not self.measuring_resp_matrix:
            self._call_callback('Log-Mon','Err :No Measurement ocurring.')
            return False
        self._call_callback('Log-Mon','Aborting measurement.')
        self.measuring_resp_matrix = False
        self._thread.join()
        self._call_callback('Log-Mon','Measurement aborted.')
        return True

    def _reset_measure_response_matrix(self,value):
        if self.measuring_resp_matrix:
            self._call_callback('Log-Mon','Cannot Reset, Measurement in process.')
            return False
        self._call_callback('Log-Mon','Reseting measurement status.')
        self._call_callback('MeasRSPMtxState-Sts',0)
        return True

    def _start_measure_response_matrix(self,value):
        if self.measuring_resp_matrix:
            self._call_callback('Log-Mon','Err: Measurement already in process.')
            return False
        if self._thread and self._thread.isAlive():
            self._call_callback('Log-Mon','Err: Cannot Measure, AutoCorr is On.')
            return False
        self.measuring_resp_matrix = True
        self._call_callback('Log-Mon', 'Starting RSP Matrix measurement.')
        self._thread = _Thread(target=self._measure_response_matrix,daemon=True)
        self._thread.start()
        return True

    def _measure_response_matrix(self):
        self._call_callback('MeasRSPMtxState-Sts',1)
        mat = _np.zeros([2*NR_BPMS,NR_CORRS])
        for i in range(NR_CORRS):
            if not self.measuring_resp_matrix:
                self._call_callback('MeasRSPMtxState-Sts',3)
                return
            self._call_callback('Log-Mon', 'Varying Corrector {0:d} of {1:d}'.format(i,NR_CORRS))
            delta = DANG if i<NR_CORRS-1 else DFREQ
            kicks = _np.zeros(NR_CORRS)
            kicks[i] = delta/2
            self.correctors.apply_kicks(kicks,delta=True)
            orbp = self.orbit.get_orbit(True)
            kicks[i] = -delta
            self.correctors.apply_kicks(kicks,no_scaling=True)
            orbn = self.orbit.get_orbit(True)
            mat[:,i] = (orbp-orbn)/delta
            kicks[i] = delta/2
            self.correctors.apply_kicks(kicks,no_scaling=True)
        self._call_callback('Log-Mon', 'Measurement Completed.')
        self.matrix.set_resp_matrix(list(mat.flatten()))
        self._call_callback('MeasRSPMtxState-Sts',2)
        self.measuring_resp_matrix = False

    def _toggle_auto_corr(self,value):
        if value:
            if self.auto_corr:
                self._call_callback('Log-Mon','Err: AutoCorr is Already On.')
                return False
            self.auto_corr = value
            if self._thread and self._thread.isAlive():
                self._call_callback('Log-Mon','Err: Cannot Correct, Measuring RSPMtx.')
                return False
            self._call_callback('Log-Mon', 'Turning Auto Correction On.')
            self._thread = _Thread(target=self._automatic_correction,daemon=True)
            self._thread.start()
        else:
            self._call_callback('Log-Mon', 'Turning Auto Correction Off.')
            self.auto_corr = value
        return True

    def _automatic_correction(self):
        if not self.correction_mode:
            self._call_callback('Log-Mon','Err: Cannot Auto Correct in Offline Mode')
            self._call_callback('AutoCorrState-Sel',0)
            self._call_callback('AutoCorrState-Sts',0)
            return
        self._call_callback('AutoCorrState-Sts',1)
        while self.auto_corr:
            t0 = _time.time()
            orb = self.orbit.get_orbit()
            self.dtheta = self.matrix.calc_kicks(orb)
            kicks = self.process_kicks()
            self.correctors.apply_kicks(self.dtheta, delta=True)
            tf = _time.time()
            dt = (tf-t0)
            interval = 1/self.auto_corr_freq
            if dt > interval:
                _log.debug('App: check took {0:f}ms.'.format(dt*1000))
                self._call_callback('Log-Mon', 'Warn: Auto Corr Loop took {0:6.2f}ms.'.format(dt*1000))
            dt = interval - dt
            if dt>0: _time.sleep(dt)
        self._call_callback('Log-Mon', 'Auto Correction is Off.')
        self._call_callback('AutoCorrState-Sts',0)

    def _toggle_correction_mode(self,value):
        self.correction_mode = value
        self.orbit.correction_mode = value
        self._call_callback('Log-Mon', 'Changing to {0:s} mode.'.format('Online' if value else 'Offline'))
        self._call_callback('CorrectionMode-Sts',value)
        self.orbit.get_orbit()
        return True

    def _set_auto_corr_frequency(self,value):
        self.auto_corr_freq = value
        self._call_callback('AutoCorrFreq-RB',value)
        return True

    def calc_correction(self,value):
        if self._thread and self._thread.isAlive():
            self._call_callback('Log-Mon','Err: AutoCorr or MeasRSPMtx is On.')
            return False
        Thread(target=self._calc_correction,daemon=True).start()
        return True

    def _calc_correction(self):
        self._call_callback('Log-Mon', 'Getting the orbit.')
        orb = self.orbit.get_orbit()
        self._call_callback('Log-Mon', 'Calculating the kicks.')
        self.corr_kicks = self.correctors.get_correctors_strength()
        self.dtheta = self.matrix.calc_kicks(orb)

    def _set_max_kick(self,value):
        self._max_kick = float(value)
        self._call_callback('MaxKickStrength-RB', float(value))

    def _set_strength(self,plane,value):
        self.strengths[plane] = value/100
        self._call_callback('Log-Mon','Setting {0:s} Strength to {1:6.2f}'.format(plane.upper(),value))
        self._call_callback(plane.upper() + 'Strength-RB', value)
        return True

    def _apply_kicks(self,code):
        if not self.correction_mode:
            self._call_callback('Log-Mon','Err: Offline, cannot apply kicks.')
            return False
        if self._thread and self._thread.isAlive():
            self._call_callback('Log-Mon','Err: AutoCorr or MeasRSPMtx is On.')
            return False
        kicks = self.dtheta.copy()
        str_ = 'Applying '
        if code == 0:
            str_ += 'CH '
            kicks[NR_CH:] = 0
        elif code == 1:
            str_ += 'CV '
            kicks[:NR_CH] = 0
            kicks[-1] = 0
        elif code == 2:
            str_ += 'RF '
            kicks[:-1] = 0
        elif code == 3:
            str_ += 'All '
        self._call_callback('Log-Mon',str_ + 'kicks.')
        kicks = self.process_kicks(kicks)
        if any(kicks):
            self.correctors.apply_kicks(self.corr_kicks + kicks, delta=False)
        return True
