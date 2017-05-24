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


        self._database = self.get_database()


    def main_loop(self):

        orb = orbit.get_orbit()
        while self.correct_orbit:
            t0 = _time.time()
            # _log.debug('App: Executing check.')
            dtheta = matrix.get_kicks(orb)
            if self.apply_kicks:
                correctors.apply(dtheta)

            orb = BPMs.get_orbit()


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


TINY_INTERVAL = 0.01

class Orbit:

    REF_ORBIT_NUM   = 15
    REF_ORBIT_ENUMS = tuple(  ['RefOrbit{0:X}'.format(i) for i in range(REF_ORBIT_NUM)]  )

    def get_database(self):
        db = dict()
        pre = self.prefix
        for i in len(self.NUM_REF_ORBIT):
            str_ = self.ref_orbit_tmp.format(i)
            db[pre + 'OrbitRefX'+str_+'-SP'] = {'type':'float','count':self.nr_bpms,'value'=0,
                                                'set_pv_fun':lambda x: self.set_ref_orbit('x',i,x)}
            db[pre + 'OrbitRefX'+str_+'-RB'] = {'type':'float','count':self.nr_bpms,'value'=0}
            db[pre + 'OrbitRefY'+str_+'-SP'] = {'type':'float','count':self.nr_bpms,'value'=0,
                                                'set_pv_fun':lambda x: self.set_ref_orbit('y',i,x)}
            db[pre + 'OrbitRefY'+str_+'-RB'] = {'type':'float','count':self.nr_bpms,'value'=0}
            db[pre+'OrbitRefName'+str_+'-SP']= {'type':'float','value'='Null',
                                                'set_pv_fun':lambda x: self.set_ref_orbit_name(i,x)}
            db[pre+'OrbitRefName'+str_+'-RB']= {'type':'float','value'='Null'}
        db[pre+'OrbitRef-Sel'] = {'type':'enum','enums':self.REF_ORBIT_ENUMS,'value'=0,
                                        'set_pv_fun':self.set_ref_orbit_ind}
        db[pre+'OrbitRef-Sts'] = {'type':'enum','enums':self.REF_ORBIT_ENUMS,'value'=0}


    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.pv ={'x':_epics.PV( 'SI-Glob:AP-Orbit:PosX-Mon', callback=self.update_orbs('x') ),
                  'y':_epics.PV( 'SI-Glob:AP-Orbit:PosY-Mon', callback=self.update_orbs('y') )  }
        if not (self.pv['x'].connected and self.pv['y'].connected):
            raise Exception('Orbit PVs not Connected.')
        if self.pv['x'].count != self.pv['y'].count:
            raise Exception('Orbit not consistent')
        self.nr_bpms = self.pv['x'].count
        self.ref_orbit = {'x':self.REF_ORBIT_NUM*[_np.zeros(self.nr_bpms,dtype=float)],
                          'y':self.REF_ORBIT_NUM*[_np.zeros(self.nr_bpms,dtype=float)]  }
        self.ref_orbit_tmp = '{0:X}'
        self.ref_orbit_ind = 0
        self.orbs = {'x':[],'y':[]}
        self.orb = {'x':None,'y':None}

    def reset_orbs(self,plane):
        self.orbs[plane] = []
        self.orb[plane] = None

    def get_count(self,plane):
        return len(self.orbs[plane])

    def update_orbs(self,plane):
        def update(pvname,value,**kwargs):
            if value is None: return
            orb = _np.array(value, dtype=float) - self.ref_orbit['plane']
            self.orbs[plane].append()
            if len(self.orbs[plane]) >= self.nr_averages:
                self.orb[plane] = _np.array(self.orbs[plane]).mean(axis=1)
                self.orbs[ṕlane] = []
        return update

    def set_ref_orbit_ind(self,ind):
        self.ref_orbit_ind = ind
        pvname = self.prefix+'OrbitRef-Sts'
        self.callback(pvname, ind)

    def set_ref_orbit(plane,ind,orb):
        self.ref_orbit[plane][ind] = _np.array(orb,dtype=float)
        pvname = self.prefix+'OrbitRef'+plane.upper()+self.ref_orbit_tmp.format(ind)+'-RB'
        self.callback(pvname, orb)

    def set_ref_orbit_name(self,ind,name):
        self.ref_obit_name[ind] = name
        pvname = self.prefix+'OrbitRef'+plane.upper()+self.ref_orbit_tmp.format(ind)+'-RB'
        self.callback(pvname, name)

    def get_orbit(self):
        ref_orbitx = _np.zeros(self.nr_bpms)
        ref_orbity = _np.zeros(self.nr_bpms)
        if self.relative:
            ref_orbitx = self.ref_orbit['x'][self.ref_orbit_ind]
            ref_orbity = self.ref_orbit['y'][self.ref_orbit_ind]

        thx = _threads.Thread(target=self.set_orbit_plane,kwargs={'plane':'x'})
        thy = _threads.Thread(target=self.set_orbit_plane,kwargs={'plane':'y'})
        thx.start()
        thy.start()
        thx.join()
        thy.join()
        orbx = self.orb['x'] - ref_orbitx
        orby = self.orb['y'] - ref_orbity
        return orbx, orby

    def set_orbit_plane(self,plane):


        self.reset_orbs(plane)
        while self.orbx is None:
            _time.sleep(TINY_INTERVAL)


class BPMs:

    def get_bpms_device_names(self):
        return ordered_list_bpm_names

    def _on_monitor_change(self,pvname,value,**kwargs):


    def get_orbit(self):
        self.reset_count()
        while True:
            for i, bpm in enumerate(self.bpms):
                if self.count[i]
