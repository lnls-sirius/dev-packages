"""Main module of AS-AP-PosAng IOC."""

import as_ap_posang.pvs as _pvs
import time as _time
import epics as _epics
import siriuspy as _siriuspy
from siriuspy import util as _util

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

        self._respmat_x, self._respmat_y = self._get_respmat()

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

        elif reason == 'RespMatX-SP':
            self._respmat_x = value
            self._set_respmat(value, self._respmat_y)
            updated = self._update_delta(
                self._orbx_deltapos, self._orbx_deltaang,
                self._respmat_x,
                self._corr_kick_sp_pvs[self._correctors[0]],
                self._corr_kick_sp_pvs[self._correctors[1]],
                self._corr_kickref[self._correctors[0]],
                self._corr_kickref[self._correctors[1]])
            self.driver.setParam('RespMatX-RB', value)
            self.driver.updatePVs()
            status = True

        elif reason == 'RespMatY-SP':
            self._respmat_y = value
            self._set_respmat(self._respmat_x, value)
            updated = self._update_delta(
                self._orby_deltapos, self._orby_deltaang,
                self._respmat_y,
                self._corr_kick_sp_pvs[self._correctors[0]],
                self._corr_kick_sp_pvs[self._correctors[1]],
                self._corr_kickref[self._correctors[0]],
                self._corr_kickref[self._correctors[1]])
            self.driver.setParam('RespMatY-RB', value)
            self.driver.updatePVs()
            status = True

        return status  # return True to invoke super().write of PCASDrive

    def _get_respmat(self):
        """Get response matrix from local file."""
        f = open('/home/fac_files/lnls-sirius/machine-applications'
                 '/as-ap-posang/as_ap_posang/' + _pvs._TL.lower() +
                 '-posang.txt', 'r')
        text = f.read()
        f.close()
        m, _ = _util.read_text_data(text)

        respmat_x = 4*[0]
        respmat_x[0] = float(m[0][0])
        respmat_x[1] = float(m[0][1])
        respmat_x[2] = float(m[1][0])
        respmat_x[3] = float(m[1][1])

        respmat_y = 4*[0]
        respmat_y[0] = float(m[2][0])
        respmat_y[1] = float(m[2][1])
        respmat_y[2] = float(m[3][0])
        respmat_y[3] = float(m[3][1])
        self.driver.setParam('RespMatX-SP', respmat_x)
        self.driver.setParam('RespMatX-RB', respmat_x)
        self.driver.setParam('RespMatY-SP', respmat_y)
        self.driver.setParam('RespMatY-RB', respmat_y)
        self.driver.updatePVs()
        return respmat_x, respmat_y

    def _set_respmat(self, respmat_x, respmat_y):
        m = ['', '']
        header = ['', '']
        if _pvs._TL.lower() == 'tb':
            header[0] = (
                "# Position-Angle Correction Response Matrices for the Booster"
                " Injection (TB correctors)\n"
                "#\n"
                "# Horizontal Matrix:\n"
                "#\n"
                "#  | DeltaPosX @ TB-04:PM-InjS |    | h11  h12 |"
                "   | Kick TB-03:MA-CH   |\n"
                "#  |                           | =  |          |"
                " * |                    |\n"
                "#  | DeltaAngX @ TB-04:PM-InjS |    | h21  h22 |"
                "   | Kick TB-04:PM-InjS |\n"
                "#\n"
                "# Data structure:\n"
                "#         h11   h12\n"
                "#         h21   h22\n\n\n")

            header[1] = (
                "\n\n"
                "# Vertical Matrix:\n"
                "#\n"
                "#  | DeltaPosY @ TB-04:PM-InjS |    | v11  v12 |"
                "   | Kick TB-04:MA-CV-1 |\n"
                "#  |                           | =  |          |"
                " * |                    |\n"
                "#  | DeltaAngY @ TB-04:PM-InjS |    | v21  v22 |"
                "   | Kick TB-04:MA-CV-2 |\n"
                "#\n"
                "# Data structure:\n"
                "#         v11   v12\n"
                "#         v21   v22\n\n\n")

        elif _pvs._TL.lower() == 'ts':
            header[0] = (
                "# Position-Angle Correction Response Matrices for the Storage"
                " Ring Injection (TS correctors)\n"
                "#\n"
                "# Horizontal Matrix:\n"
                "#\n"
                "#  | DeltaPosX @ TS-04:DI-Scrn-3 |    | h11  h12 |"
                "   | Kick TS-04:MA-CH    |\n"
                "#  |                             | =  |          |"
                " * |                     |\n"
                "#  | DeltaAngX @ TS-04:DI-Scrn-3 |    | h21  h22 |"
                "   | Kick TS-04:PM-InjSF |\n"
                "#\n"
                "# Data structure:\n"
                "#         h11   h12\n"
                "#         h21   h22\n\n\n")

            header[1] = (
                "\n\n"
                "# Vertical Matrix:\n"
                "#\n"
                "#  | DeltaPosY @ TS-04:DI-Scrn-3 |    | v11  v12 |"
                "   | Kick TS-04:MA-CV-1 |\n"
                "#  |                             | =  |          |"
                " * |                    |\n"
                "#  | DeltaAngY @ TS-04:DI-Scrn-3 |    | v21  v22 |"
                "   | Kick TS-04:MA-CV-2 |\n"
                "#\n"
                "# Data structure:\n"
                "#         v11   v12\n"
                "#         v21   v22\n\n\n")

        orb = 0
        for mat in [respmat_x, respmat_y]:
            index = 0
            m[orb] = ''
            for row in range(2):
                for col in range(2):
                    if mat[index] < 0:
                        space = '  '
                    else:
                        space = '   '
                    m[orb] += space + str(mat[index])
                    index += 1
                m[orb] += '\n'
            m[orb] += '\n'
            orb += 1

        text = header[0] + m[0] + header[1] + m[1]

        f = open('/home/fac_files/lnls-sirius/machine-applications'
                 '/as-ap-posang/as_ap_posang/' + _pvs._TL.lower() +
                 '-posang.txt', 'w')
        f.write(text)
        f.close()
        return text

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
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' disconnected')
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
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Off')

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
        self.driver.setParam('Log-Mon', 'WARN:'+ps+' changed')
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
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Local')
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
                                     'ERR:' + corr + ' is disconnected')
                self.driver.updatePVs()
                return False
        self.driver.setParam('Log-Mon', 'Sent configuration to correctors')
        self.driver.updatePVs()
        return True
