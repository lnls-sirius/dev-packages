"""Main module of AS-AP-PosAng IOC."""

import as_ap_posang.pvs as _pvs
import time as _time
import epics as _epics
import siriuspy as _siriuspy
from siriuspy.servconf.conf_service import ConfigService as _ConfigService

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

        self._status = 0xf
        self._orbx_deltapos = 0
        self._orby_deltapos = 0
        self._orbx_deltaang = 0
        self._orby_deltaang = 0
        self._setnewref_cmd_count = 0
        self._config_corr_ps_cmd_count = 0

        self._corr_check_connection = 4*[0]
        self._corr_check_pwrstate_sts = 4*[0]
        self._corr_check_opmode_sts = 4*[0]
        self._corr_check_ctrlmode_mon = 4*[0]

        config_name = self._get_config_name()
        self._get_respmat(config_name)
        self.driver.setParam('RespMatConfigName-SP', config_name)
        self.driver.setParam('RespMatConfigName-RB', config_name)
        self.driver.setParam('RespMatX-Mon', self._respmat_x)
        self.driver.setParam('RespMatY-Mon', self._respmat_y)

        # The correctors are listed as:
        # First horizontal corretor, second horizontal corretor,
        # first vertical corretor and second vertical corretor.
        self._correctors = ['', '', '', '']
        if _pvs._TL == 'TS':
            self._correctors[0] = 'TS-04:MA-CH'
            self._correctors[1] = 'TS-04:PM-InjSF'
            self._correctors[2] = 'TS-04:MA-CV-1'
            self._correctors[3] = 'TS-04:MA-CV-2'

        elif _pvs._TL == 'TB':
            self._correctors[0] = 'TB-03:MA-CH'
            self._correctors[1] = 'TB-04:PM-InjS'
            self._correctors[2] = 'TB-04:MA-CV-1'
            self._correctors[3] = 'TB-04:MA-CV-2'

        # Connect to correctors
        self._corr_kick_sp_pvs = {}
        self._corr_kick_rb_pvs = {}
        self._corr_pwrstate_sel_pvs = {}
        self._corr_pwrstate_sts_pvs = {}
        self._corr_opmode_sel_pvs = {}
        self._corr_opmode_sts_pvs = {}
        self._corr_ctrlmode_mon_pvs = {}
        self._corr_kickref = {}

        for corr in self._correctors:
            self._corr_kick_sp_pvs[corr] = _epics.PV(
                _pvs._PREFIX_VACA + corr + ':Kick-SP',
                connection_timeout=0.05)
            self._corr_kick_rb_pvs[corr] = _epics.PV(
                _pvs._PREFIX_VACA + corr + ':Kick-RB',
                connection_timeout=0.05)

            self._corr_pwrstate_sel_pvs[corr] = _epics.PV(
                _pvs._PREFIX_VACA + corr + ':PwrState-Sel',
                connection_timeout=0.05)
            self._corr_pwrstate_sts_pvs[corr] = _epics.PV(
                _pvs._PREFIX_VACA + corr + ':PwrState-Sts',
                connection_timeout=0.05)

            self._corr_opmode_sel_pvs[corr] = _epics.PV(
                _pvs._PREFIX_VACA + corr + ':OpMode-Sel',
                connection_timeout=0.05)
            self._corr_opmode_sts_pvs[corr] = _epics.PV(
                _pvs._PREFIX_VACA + corr + ':OpMode-Sts',
                connection_timeout=0.05)

            self._corr_ctrlmode_mon_pvs[corr] = _epics.PV(
                _pvs._PREFIX_VACA + corr + ':CtrlMode-Mon',
                connection_timeout=0.05)

        for corr in self._correctors:
            corr_index = self._correctors.index(corr)
            self._corr_kickref[corr] = self._corr_kick_sp_pvs[corr].get()
            self._corr_check_connection[corr_index] = (
                self._corr_kick_sp_pvs[corr].connected)

            self._corr_pwrstate_sts_pvs[corr].add_callback(
                self._callback_corr_pwrstate_sts)
            self._corr_check_pwrstate_sts[corr_index] = (
                self._corr_pwrstate_sts_pvs[corr].value)

            if corr_index != 1:
                self._corr_opmode_sts_pvs[corr].add_callback(
                    self._callback_corr_opmode_sts)
                self._corr_check_opmode_sts[corr_index] = (
                    self._corr_opmode_sts_pvs[corr].value)

            self._corr_ctrlmode_mon_pvs[corr].add_callback(
                self._callback_corr_ctrlmode_mon)
            self._corr_check_ctrlmode_mon[corr_index] = (
                self._corr_ctrlmode_mon_pvs[corr].value)

        self._update_ref()

        # Set current status
        if all(conn == 1 for conn in self._corr_check_connection):
            self._status = self._status & 0xe
        if all(pwr == 1 for pwr in self._corr_check_pwrstate_sts):
            self._status = self._status & 0xd
        if all(op == 0 for op in self._corr_check_opmode_sts):
            self._status = self._status & 0xb
        if all(ctrl == 0 for ctrl in self._corr_check_ctrlmode_mon):
            self._status = self._status & 0x7
        self.driver.setParam('Status-Mon', self._status)

        self.driver.setParam('Log-Mon', 'Started.')
        self.driver.updatePVs()

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
            updated = self._update_delta(
                value, self._orbx_deltaang,
                self._respmat_x,
                self._corr_kick_sp_pvs[self._correctors[0]],
                self._corr_kick_sp_pvs[self._correctors[1]],
                self._corr_kickref[self._correctors[0]],
                self._corr_kickref[self._correctors[1]])
            if updated:
                self._orbx_deltapos = value
                self.driver.setParam('DeltaPosX-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'DeltaAngX-SP':
            updated = self._update_delta(
                self._orbx_deltapos, value,
                self._respmat_x,
                self._corr_kick_sp_pvs[self._correctors[0]],
                self._corr_kick_sp_pvs[self._correctors[1]],
                self._corr_kickref[self._correctors[0]],
                self._corr_kickref[self._correctors[1]])
            if updated:
                self._orbx_deltaang = value
                self.driver.setParam('DeltaAngX-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'DeltaPosY-SP':
            updated = self._update_delta(
                value, self._orby_deltaang,
                self._respmat_y,
                self._corr_kick_sp_pvs[self._correctors[2]],
                self._corr_kick_sp_pvs[self._correctors[3]],
                self._corr_kickref[self._correctors[2]],
                self._corr_kickref[self._correctors[3]])
            if updated:
                self._orby_deltapos = value
                self.driver.setParam('DeltaPosY-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'DeltaAngY-SP':
            updated = self._update_delta(
                self._orby_deltapos, value,
                self._respmat_y,
                self._corr_kick_sp_pvs[self._correctors[2]],
                self._corr_kick_sp_pvs[self._correctors[3]],
                self._corr_kickref[self._correctors[2]],
                self._corr_kickref[self._correctors[3]])
            if updated:
                self._orby_deltaang = value
                self.driver.setParam('DeltaAngY-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'SetNewRef-Cmd':
            self._update_ref()
            self._setnewref_cmd_count += 1
            self.driver.setParam('SetNewRef-Cmd', self._setnewref_cmd_count)
            self.driver.updatePVs()  # in case PV states change.

        elif reason == 'ConfigPS-Cmd':
            done = self._config_corr_ps()
            if done:
                self._config_corr_ps_cmd_count += 1
                self.driver.setParam('ConfigPS-Cmd',
                                     self._config_corr_ps_cmd_count)
                self.driver.updatePVs()

        elif reason == 'RespMatConfigName-SP':
            done = self._get_respmat(value)
            if done:
                self._set_config_name(value)
                updated = self._update_delta(
                    self._orbx_deltapos, self._orbx_deltaang,
                    self._respmat_x,
                    self._corr_kick_sp_pvs[self._correctors[0]],
                    self._corr_kick_sp_pvs[self._correctors[1]],
                    self._corr_kickref[self._correctors[0]],
                    self._corr_kickref[self._correctors[1]])
                updated = self._update_delta(
                    self._orby_deltapos, self._orby_deltaang,
                    self._respmat_y,
                    self._corr_kick_sp_pvs[self._correctors[0]],
                    self._corr_kick_sp_pvs[self._correctors[1]],
                    self._corr_kickref[self._correctors[0]],
                    self._corr_kickref[self._correctors[1]])
                self.driver.setParam('RespMatConfigName-RB', value)
                self.driver.setParam('RespMatX-Mon', self._respmat_x)
                self.driver.setParam('RespMatY-Mon', self._respmat_y)
                self.driver.setParam('Log-Mon', 'Updated correction matrices.')
                self.driver.updatePVs()
                status = True
            else:
                self.driver.setParam(
                    'Log-Mon', 'ERR:Configuration not found in configdb.')
                self.driver.updatePVs()

        return status  # return True to invoke super().write of PCASDrive

    def _get_respmat(self, config_name):
        """Get response matrix from configurations database."""
        cs = _ConfigService()
        q = cs.get_config(_pvs._TL.lower()+'_posang_respm', config_name)
        done = q['code']

        if done == 200:
            done = True
            mats = q['result']['value']
            mx = mats['respm-x']
            my = mats['respm-y']

            respmat_x = 4*[0]
            respmat_x[0] = float(mx[0][0])
            respmat_x[1] = float(mx[0][1])
            respmat_x[2] = float(mx[1][0])
            respmat_x[3] = float(mx[1][1])
            self._respmat_x = respmat_x

            respmat_y = 4*[0]
            respmat_y[0] = float(my[0][0])
            respmat_y[1] = float(my[0][1])
            respmat_y[2] = float(my[1][0])
            respmat_y[3] = float(my[1][1])
            self._respmat_y = respmat_y
        else:
            done = False
        return done

    def _get_config_name(self):
        f = open('/home/fac_files/lnls-sirius/machine-applications'
                 '/as-ap-posang/as_ap_posang/' + _pvs._TL.lower() +
                 '-posang.txt', 'r')
        config_name = f.read().strip('\n')
        f.close()
        return config_name

    def _set_config_name(self, config_name):
        f = open('/home/fac_files/lnls-sirius/machine-applications'
                 '/as-ap-posang/as_ap_posang/' + _pvs._TL.lower() +
                 '-posang.txt', 'w')
        f.write(config_name)
        f.close()

    def _update_delta(self, delta_pos, delta_ang, respmat, c1_kick_sp_pv,
                      c2_kick_sp_pv, c1_kickref, c2_kickref):
        if self._status == 0x0:
            delta_pos_meters = delta_pos/1000
            delta_ang_rad = delta_ang/1000

            det = respmat[0] * respmat[3] - respmat[1] * respmat[2]
            delta_kick_c1 = (respmat[3] * delta_pos_meters-respmat[1] *
                             delta_ang_rad) / det
            delta_kick_c2 = (-respmat[2]*delta_pos_meters+respmat[0] *
                             delta_ang_rad) / det

            c1_kick_sp_pv.put(c1_kickref + delta_kick_c1)
            c2_kick_sp_pv.put(c2_kickref + delta_kick_c2)

            self.driver.setParam('Log-Mon', 'Applied new delta.')
            self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon',
                                 'ERR:Failed on applying new delta.')
            self.driver.updatePVs()
            return False

    def _update_ref(self):
        # updates reference
        self._corr_kickref[self._correctors[0]] = (
            self._corr_kick_rb_pvs[self._correctors[0]].get())
        self.driver.setParam('CH1RefKick-Mon',
                             self._corr_kickref[self._correctors[0]])

        self._corr_kickref[self._correctors[1]] = (
            self._corr_kick_rb_pvs[self._correctors[1]].get())
        self.driver.setParam('CH2RefKick-Mon',
                             self._corr_kickref[self._correctors[1]])

        self._corr_kickref[self._correctors[2]] = (
            self._corr_kick_rb_pvs[self._correctors[2]].get())
        self.driver.setParam('CV1RefKick-Mon',
                             self._corr_kickref[self._correctors[2]])

        self._corr_kickref[self._correctors[3]] = (
            self._corr_kick_rb_pvs[self._correctors[3]].get())
        self.driver.setParam('CV2RefKick-Mon',
                             self._corr_kickref[self._correctors[3]])

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

        self.driver.setParam('Log-Mon', 'Updated Kick References.')
        self.driver.updatePVs()

    def _connection_callback_corr_kick_pvs(self, pvname, conn, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' disconnected.')
            self.driver.updatePVs()

        corr = ps.split(':')[0]+':'+ps.split(':')[1]
        corr_index = self._correctors.index(corr)
        self._corr_check_connection[corr_index] = (1 if conn else 0)

        # Change the first bit of correction status
        if any(q == 0 for q in self._corr_check_connection):
            conn_status = 0x1
            self._status = self._status | conn_status
        else:
            conn_status = 0xe
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_corr_pwrstate_sts(self, pvname, value, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        if value == 0:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Off.')

        corr = ps.split(':')[0]+':'+ps.split(':')[1]
        corr_index = self._correctors.index(corr)
        self._corr_check_pwrstate_sts[corr_index] = value

        # Change the second bit of correction status
        if any(q == 0 for q in self._corr_check_pwrstate_sts):
            conn_status = 0x2
            self._status = self._status | conn_status
        else:
            conn_status = 0xd
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_corr_opmode_sts(self, pvname, value, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        self.driver.setParam('Log-Mon', 'WARN:'+ps+' changed.')
        self.driver.updatePVs()

        corr = ps.split(':')[0]+':'+ps.split(':')[1]
        corr_index = self._correctors.index(corr)
        self._corr_check_opmode_sts[corr_index] = value

        # Change the third bit of correction status
        if any(s != 0 for s in self._corr_check_opmode_sts):
            conn_status = 0x4
            self._status = self._status | conn_status
        else:
            conn_status = 0xb
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_corr_ctrlmode_mon(self,  pvname, value, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        if value == 1:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Local.')
            self.driver.updatePVs()

        corr = ps.split(':')[0]+':'+ps.split(':')[1]
        corr_index = self._correctors.index(corr)
        self._corr_check_ctrlmode_mon[corr_index] = value

        # Change the fourth bit of correction status
        if any(q == 1 for q in self._corr_check_ctrlmode_mon):
            conn_status = 0x8
            self._status = self._status | conn_status
        else:
            conn_status = 0x7
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _config_corr_ps(self):
        for corr in self._correctors:
            corr_index = self._correctors.index(corr)
            if self._corr_pwrstate_sel_pvs[corr].connected:
                self._corr_pwrstate_sel_pvs[corr].put(1)
                if corr_index != 1:
                    self._corr_opmode_sel_pvs[corr].put(0)
            else:
                self.driver.setParam('Log-Mon',
                                     'ERR:' + corr + ' is disconnected.')
                self.driver.updatePVs()
                return False
        self.driver.setParam('Log-Mon', 'Sent configuration to correctors.')
        self.driver.updatePVs()
        return True
