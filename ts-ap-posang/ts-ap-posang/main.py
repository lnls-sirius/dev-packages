import pvs as _pvs
import time as _time
import epics as _epics

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__ = _pvs.__version__

class App:

    pvs_database = _pvs.pvs_database

    def __init__(self,driver):
        self._driver = driver
        self._pvs_database        = _pvs.pvs_database
        self._ch1_kick_mon_pv     = _epics.PV('TS-04:MA-CH:Kick-Mon', connection_timeout=0.05)
        self._ch2_kick_mon_pv     = _epics.PV('TS-04:PM-InjSF:Kick-Mon', connection_timeout=0.05)
        self._cv1_kick_mon_pv     = _epics.PV('TS-04:MA-CV-1:Kick-Mon', connection_timeout=0.05)
        self._cv2_kick_mon_pv     = _epics.PV('TS-04:MA-CV-2:Kick-Mon', connection_timeout=0.05)
        self._ch1_kick_sp_pv      = _epics.PV('TS-04:MA-CH:Kick-SP', connection_timeout=0.05)
        self._ch2_kick_sp_pv      = _epics.PV('TS-04:PM-InjSF:Kick-SP', connection_timeout=0.05)
        self._cv1_kick_sp_pv      = _epics.PV('TS-04:MA-CV-1:Kick-SP', connection_timeout=0.05)
        self._cv2_kick_sp_pv      = _epics.PV('TS-04:MA-CV-2:Kick-SP', connection_timeout=0.05)
        self._ch1_pwrstate_sts_pv = _epics.PV('TS-04:MA-CH:PwrState-Sts', connection_timeout=0.05)
        self._ch2_pwrstate_sts_pv = _epics.PV('TS-04:PM-InjSF:PwrState-Sts', connection_timeout=0.05)
        self._cv1_pwrstate_sts_pv = _epics.PV('TS-04:MA-CV-1:PwrState-Sts', connection_timeout=0.05)
        self._cv2_pwrstate_sts_pv = _epics.PV('TS-04:MA-CV-2:PwrState-Sts', connection_timeout=0.05)
        self._orbx_respmat        = self._get_respmat('x')
        self._orby_respmat        = self._get_respmat('y')
        self._ch1_kickref         = self._ch1_kick_mon_pv.get()
        self._ch2_kickref         = self._ch2_kick_mon_pv.get()
        self._cv1_kickref         = self._cv1_kick_mon_pv.get()
        self._cv2_kickref         = self._cv2_kick_mon_pv.get()
        self._orbx_deltapos       = 0
        self._orby_deltapos       = 0
        self._orbx_deltaang       = 0
        self._orby_deltaang       = 0

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        _time.sleep(interval)

    def read(self,reason):
        value = None # implementation here
        #self.driver.updatePVs() # this should be used in case PV states change.
        return value

    def write(self,reason,value):
        status = False
        if reason == 'OrbXDeltaPos-SP':
            print('orbx deltapos')
            updated = self._update_delta(value, self._orbx_deltaang,
                                        self._orbx_respmat,
                                        self._ch1_kick_sp_pv, self._ch2_kick_sp_pv,
                                        self._ch1_kickref, self._ch2_kickref,
                                        self._ch1_pwrstate_sts_pv,self._ch2_pwrstate_sts_pv)
            if updated:
                self._orbx_deltapos = value
                self.driver.setParam('OrbXDeltaPos-RB',value)
                self.driver.updatePVs()
                status = True
        elif reason == 'OrbXDeltaAng-SP':
            print('orbx deltaang')
            updated = self._update_delta(self._orbx_deltapos, value,
                                        self._orbx_respmat,
                                        self._ch1_kick_sp_pv, self._ch2_kick_sp_pv,
                                        self._ch1_kickref, self._ch2_kickref,
                                        self._ch1_pwrstate_sts_pv,self._ch2_pwrstate_sts_pv)
            if updated:
                self._orbx_deltaang = value
                self.driver.setParam('OrbXDeltaAng-RB',value)
                self.driver.updatePVs()
                status = True
        elif reason == 'OrbYDeltaPos-SP':
            print('orby deltapos')
            updated = self._update_delta(value, self._orby_deltaang,
                                        self._orby_respmat,
                                        self._cv1_kick_sp_pv, self._cv2_kick_sp_pv,
                                        self._cv1_kickref, self._cv2_kickref,
                                        self._cv1_pwrstate_sts_pv,self._cv2_pwrstate_sts_pv)
            if updated:
                self._orby_deltapos = value
                self.driver.setParam('OrbYDeltaPos-RB',value)
                self.driver.updatePVs()
                status = True
        elif reason == 'OrbYDeltaAng-SP':
            print('orby deltaang')
            updated = self._update_delta(self._orby_deltapos, value,
                                        self._orby_respmat,
                                        self._cv1_kick_sp_pv, self._cv2_kick_sp_pv,
                                        self._cv1_kickref, self._cv2_kickref,
                                        self._cv1_pwrstate_sts_pv,self._cv2_pwrstate_sts_pv)
            if updated:
                self._orby_deltaang = value
                self.driver.setParam('OrbYDeltaAng-RB',value)
                self.driver.updatePVs()
                status = True
        elif reason == 'SetNewRef':
            self._update_ref()
            self.driver.updatePVs()
        #self.driver.updatePVs() # this should be used in case PV states change.
        return status # when returning True super().write of PCASDrive is invoked

    def _get_respmat(self,orb):
        if orb == 'x':
            return [1,2,3,4]
        if orb == 'y':
            return [1,2,3,4]

    def _update_delta(self,delta_pos,delta_ang,respmat,c1_kick_sp_pv,c2_kick_sp_pv,c1_kickref,c2_kickref,c1_pwrstate_sts_pv,c2_pwrstate_sts_pv):
        if not c1_kick_sp_pv.connected:
            print('First corrector pv is disconnected')
            return False
        elif not c2_kick_sp_pv.connected:
            print('Second corrector pv is disconnected')
            return False
        else:
            delta_kick_c1 = ( respmat[3]*delta_pos-respmat[1]*delta_ang)/(respmat[0]*respmat[3]-respmat[1]*respmat[2])
            delta_kick_c2 = (-respmat[2]*delta_pos+respmat[0]*delta_ang)/(respmat[0]*respmat[3]-respmat[1]*respmat[2])
            print('delta_c1:' + str(delta_kick_c1))
            print('delta_c2:' + str(delta_kick_c2))

            if c1_pwrstate_sts_pv.get() != 1:
                print('First corrector is off')
                return False
            elif c2_pwrstate_sts_pv.get() != 1:
                print('Second corrector is off')
                return False
            else:
                c1_kick_sp_pv.put(c1_kickref + delta_kick_c1)
                c2_kick_sp_pv.put(c2_kickref + delta_kick_c2)
                return True

    def _update_ref(self):
        # updates reference
        self._ch1_kickref = self._ch1_kick_mon_pv.get()
        self.driver.setParam('CH1KickRef-Mon',self._ch1_kickref)
        self._ch2_kickref = self._ch2_kick_mon_pv.get()
        self.driver.setParam('CH2KickRef-Mon',self._ch2_kickref)
        self._cv1_kickref = self._cv1_kick_mon_pv.get()
        self.driver.setParam('CV1KickRef-Mon',self._cv1_kickref)
        self._cv2_kickref = self._cv2_kick_mon_pv.get()
        self.driver.setParam('CV2KickRef-Mon',self._cv2_kickref)
        # the deltas from new kick references are zero
        self._orbx_deltapos = 0
        self._orby_deltapos = 0
        self._orbx_deltaang = 0
        self._orby_deltaang = 0
        self.driver.setParam('OrbXDeltaPos-SP', self._orbx_deltapos)
        self.driver.setParam('OrbXDeltaPos-RB', self._orbx_deltapos)
        self.driver.setParam('OrbXDeltaAng-SP', self._orbx_deltaang)
        self.driver.setParam('OrbXDeltaAng-RB', self._orbx_deltaang)
        self.driver.setParam('OrbYDeltaPos-SP', self._orby_deltapos)
        self.driver.setParam('OrbYDeltaPos-RB', self._orby_deltapos)
        self.driver.setParam('OrbYDeltaAng-SP', self._orby_deltaang)
        self.driver.setParam('OrbYDeltaAng-RB', self._orby_deltaang)
