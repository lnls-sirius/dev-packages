"""Main module of AS-AP-PosAng IOC."""
import as_ap_posang.pvs as _pvs
import time as _time
import epics as _epics
import siriuspy as _siriuspy
import siriuspy.servweb as _siriuspy_servweb

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be
#      easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)

__version__ = _pvs._COMMIT_HASH


class App:
    """Main application for handling injection in transport lines."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _siriuspy.util.print_ioc_banner(
            ioc_name=_pvs._TL + '-AP-PosAng',
            db=App.pvs_database,
            description=_pvs._TL + '-AP-PosAng Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list(_pvs._TL.lower()+'-ap-posang',
                                        ('',
                                         _pvs._PREFIX),
                                        App.pvs_database)
        self._driver = driver
        self._pvs_database = App.pvs_database
        if _pvs._TL == 'TS':
            self._ch1_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CH:Kick-Mon',
                connection_timeout=0.05)
            self._ch2_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:PM-InjSF:Kick-Mon',
                connection_timeout=0.05)
            self._cv1_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CV-1:Kick-Mon',
                connection_timeout=0.05)
            self._cv2_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CV-2:Kick-Mon',
                connection_timeout=0.05)
            self._ch1_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CH:Kick-SP',
                connection_timeout=0.05)
            self._ch2_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:PM-InjSF:Kick-SP',
                connection_timeout=0.05)
            self._cv1_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CV-1:Kick-SP',
                connection_timeout=0.05)
            self._cv2_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CV-2:Kick-SP',
                connection_timeout=0.05)
            self._ch1_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CH:PwrState-Sts',
                connection_timeout=0.05)
            self._ch2_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:PM-InjSF:PwrState-Sts',
                connection_timeout=0.05)
            self._cv1_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CV-1:PwrState-Sts',
                connection_timeout=0.05)
            self._cv2_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TS-04:MA-CV-2:PwrState-Sts',
                connection_timeout=0.05)
        elif _pvs._TL == 'TB':
            self._ch1_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-03:MA-CH:Kick-Mon',
                connection_timeout=0.05)
            self._ch2_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:PM-InjS:Kick-Mon',
                connection_timeout=0.05)
            self._cv1_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:MA-CV-1:Kick-Mon',
                connection_timeout=0.05)
            self._cv2_kick_mon_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:MA-CV-2:Kick-Mon',
                connection_timeout=0.05)
            self._ch1_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-03:MA-CH:Kick-SP',
                connection_timeout=0.05)
            self._ch2_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:PM-InjS:Kick-SP',
                connection_timeout=0.05)
            self._cv2_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:MA-CV-2:Kick-SP',
                connection_timeout=0.05)
            self._cv1_kick_sp_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:MA-CV-1:Kick-SP',
                connection_timeout=0.05)
            self._ch1_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-03:MA-CH:PwrState-Sts',
                connection_timeout=0.05)
            self._ch2_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:PM-InjS:PwrState-Sts',
                connection_timeout=0.05)
            self._cv1_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:MA-CV-1:PwrState-Sts',
                connection_timeout=0.05)
            self._cv2_pwrstate_sts_pv = _epics.PV(
                _pvs._PREFIX_VACA + 'TB-04:MA-CV-2:PwrState-Sts',
                connection_timeout=0.05)
        self._orbx_respmat = self._get_respmat('x')
        self._orby_respmat = self._get_respmat('y')
        self._ch1_kickref = self._ch1_kick_mon_pv.get()
        self._ch2_kickref = self._ch2_kick_mon_pv.get()
        self._cv1_kickref = self._cv1_kick_mon_pv.get()
        self._cv2_kickref = self._cv2_kick_mon_pv.get()
        self._orbx_deltapos = 0
        self._orby_deltapos = 0
        self._orbx_deltaang = 0
        self._orby_deltaang = 0
        self._setnewref_cmd_count = 0

    @staticmethod
    def init_class():
        """Init class."""
        App.pvs_database = _pvs.get_pvs_database()

    @property
    def driver(self):
        """Return driver."""
        return self._driver

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'DeltaPosX-SP':
            print('orbx deltapos')
            updated = self._update_delta(
                value, self._orbx_deltaang,
                self._orbx_respmat,
                self._ch1_kick_sp_pv, self._ch2_kick_sp_pv,
                self._ch1_kickref, self._ch2_kickref,
                self._ch1_pwrstate_sts_pv, self._ch2_pwrstate_sts_pv)
            if updated:
                self._orbx_deltapos = value
                self.driver.setParam('DeltaPosX-RB', value)
                self.driver.updatePVs()
                status = True
        elif reason == 'DeltaAngX-SP':
            print('orbx deltaang')
            updated = self._update_delta(
                self._orbx_deltapos, value,
                self._orbx_respmat,
                self._ch1_kick_sp_pv, self._ch2_kick_sp_pv,
                self._ch1_kickref, self._ch2_kickref,
                self._ch1_pwrstate_sts_pv, self._ch2_pwrstate_sts_pv)
            if updated:
                self._orbx_deltaang = value
                self.driver.setParam('DeltaAngX-RB', value)
                self.driver.updatePVs()
                status = True
        elif reason == 'DeltaPosY-SP':
            print('orby deltapos')
            updated = self._update_delta(
                value, self._orby_deltaang,
                self._orby_respmat,
                self._cv1_kick_sp_pv, self._cv2_kick_sp_pv,
                self._cv1_kickref, self._cv2_kickref,
                self._cv1_pwrstate_sts_pv, self._cv2_pwrstate_sts_pv)
            if updated:
                self._orby_deltapos = value
                self.driver.setParam('DeltaPosY-RB', value)
                self.driver.updatePVs()
                status = True
        elif reason == 'DeltaAngY-SP':
            print('orby deltaang')
            updated = self._update_delta(
                self._orby_deltapos, value,
                self._orby_respmat,
                self._cv1_kick_sp_pv, self._cv2_kick_sp_pv,
                self._cv1_kickref, self._cv2_kickref,
                self._cv1_pwrstate_sts_pv, self._cv2_pwrstate_sts_pv)
            if updated:
                self._orby_deltaang = value
                self.driver.setParam('DeltaAngY-RB', value)
                self.driver.updatePVs()
                status = True
        elif reason == 'SetNewRef-Cmd':
            self._setnewref_cmd_count += 1
            self.driver.setParam('SetNewRef-Cmd', self._setnewref_cmd_count)
            self._update_ref()
            self.driver.updatePVs()  # in case PV states change.
        return status  # return True to invoke super().write of PCASDrive

    def _get_respmat(self, orb):
        """New get_respmat."""
        if orb == 'x':
            orbx_respmat = [0, 0, 0, 0]
            m, _ = _siriuspy_servweb.response_matrix_read(
                _pvs._TL.lower() + '-posang-correction-horizontal.txt')
            orbx_respmat[0] = float(m[0][0])
            orbx_respmat[1] = float(m[0][1])
            orbx_respmat[2] = float(m[1][0])
            orbx_respmat[3] = float(m[1][1])
            self.driver.setParam('RespMatX-Cte', orbx_respmat)
            self.driver.updatePVs()
            print('PosAng RespMat:')
            print(orbx_respmat)
            return orbx_respmat

        if orb == 'y':
            orby_respmat = [0, 0, 0, 0]
            m, _ = _siriuspy_servweb.response_matrix_read(
                _pvs._TL.lower() + '-posang-correction-vertical.txt')
            orby_respmat[0] = float(m[0][0])
            orby_respmat[1] = float(m[0][1])
            orby_respmat[2] = float(m[1][0])
            orby_respmat[3] = float(m[1][1])
            self.driver.setParam('RespMatY-Cte', orby_respmat)
            self.driver.updatePVs()
            print(orby_respmat)
            return orby_respmat

    def _update_delta(self, delta_pos, delta_ang, respmat, c1_kick_sp_pv,
                      c2_kick_sp_pv, c1_kickref, c2_kickref,
                      c1_pwrstate_sts_pv, c2_pwrstate_sts_pv):
        delta_pos_meters = delta_pos/1000
        delta_ang_rad = delta_ang/1000

        if not c1_kick_sp_pv.connected:
            print('First corrector pv is disconnected')
            return False
        elif not c2_kick_sp_pv.connected:
            print('Second corrector pv is disconnected')
            return False
        else:
            det = respmat[0] * respmat[3] - respmat[1] * respmat[2]
            delta_kick_c1 = (respmat[3] * delta_pos_meters-respmat[1] *
                             delta_ang_rad) / det
            delta_kick_c2 = (-respmat[2]*delta_pos_meters+respmat[0] *
                             delta_ang_rad) / det
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
        self.driver.setParam('CH1KickRef-Mon', self._ch1_kickref)
        self._ch2_kickref = self._ch2_kick_mon_pv.get()
        self.driver.setParam('CH2KickRef-Mon', self._ch2_kickref)
        self._cv1_kickref = self._cv1_kick_mon_pv.get()
        self.driver.setParam('CV1KickRef-Mon', self._cv1_kickref)
        self._cv2_kickref = self._cv2_kick_mon_pv.get()
        self.driver.setParam('CV2KickRef-Mon', self._cv2_kickref)
        # the deltas from new kick references are zero
        self._orbx_deltapos = 0
        self._orby_deltapos = 0
        self._orbx_deltaang = 0
        self._orby_deltaang = 0
        self.driver.setParam('DeltaPosX-SP', self._orbx_deltapos)
        self.driver.setParam('DeltaPosX-RB', self._orbx_deltapos)
        self.driver.setParam('DeltaAngX-SP', self._orbx_deltaang)
        self.driver.setParam('DeltaAngX-RB', self._orbx_deltaang)
        self.driver.setParam('DeltaPosY-SP', self._orby_deltapos)
        self.driver.setParam('DeltaPosY-RB', self._orby_deltapos)
        self.driver.setParam('DeltaAngY-SP', self._orby_deltaang)
        self.driver.setParam('DeltaAngY-RB', self._orby_deltaang)
