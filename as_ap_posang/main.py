"""Main module of AS-AP-PosAng IOC."""

import time as _time
import numpy as _np
import epics as _epics
import siriuspy as _siriuspy
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.posang import Const as _PAConst
from siriuspy.namesys import SiriusPVName as _SiriusPVName
import as_ap_posang.pvs as _pvs

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


# Constants
_ALLSET = 0xf
_ALLCLR = 0x0


class App:
    """Main application for handling injection in transport lines."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner_and_save_pv_list()

        self._TL = _pvs.get_pvs_section()
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._PREFIX = _pvs.get_pvs_prefix()

        self._driver = driver

        self._status = _ALLSET
        self._orbx_deltapos = 0
        self._orby_deltapos = 0
        self._orbx_deltaang = 0
        self._orby_deltaang = 0
        self._setnewrefkick_cmd_count = 0
        self._config_ma_cmd_count = 0

        self._corr_check_connection = 4*[0]
        self._corr_check_pwrstate_sts = 4*[0]
        self._corr_check_opmode_sts = [1, _PSConst.States.SlowRef, 1, 1]
        self._corr_check_ctrlmode_mon = [1, _PSConst.Interface.Remote, 1, 1]
        # obs: ignore PM on OpMode and CtrlMode checks

        config_name = self._get_config_name()
        [done, corrparams] = self._get_corrparams(config_name)
        if done:
            self.driver.setParam('ConfigName-SP', config_name)
            self.driver.setParam('ConfigName-RB', config_name)
            self._respmat_x = corrparams[0]
            self.driver.setParam('RespMatX-Mon', corrparams[0])
            self._respmat_y = corrparams[1]
            self.driver.setParam('RespMatY-Mon', corrparams[1])

        # The correctors are listed as:
        # First horizontal corretor, second horizontal corretor,
        # first vertical corretor and second vertical corretor.
        self._correctors = ['', '', '', '']
        if self._TL == 'TS':
            self._correctors[0] = _PAConst.TS_CORRH_POSANG[0]
            self._correctors[1] = _PAConst.TS_CORRH_POSANG[1]
            self._correctors[2] = _PAConst.TS_CORRV_POSANG[0]
            self._correctors[3] = _PAConst.TS_CORRV_POSANG[1]

        elif self._TL == 'TB':
            self._correctors[0] = _PAConst.TB_CORRH_POSANG[0]
            self._correctors[1] = _PAConst.TB_CORRH_POSANG[1]
            self._correctors[2] = _PAConst.TB_CORRV_POSANG[0]
            self._correctors[3] = _PAConst.TB_CORRV_POSANG[1]

        # Connect to correctors
        self._corr_kick_sp_pvs = {}
        self._corr_kick_rb_pvs = {}
        self._corr_pwrstate_sel_pvs = {}
        self._corr_pwrstate_sts_pvs = {}
        self._corr_opmode_sel_pvs = {}
        self._corr_opmode_sts_pvs = {}
        self._corr_ctrlmode_mon_pvs = {}
        self._corr_refkick = {}

        for corr in self._correctors:
            corr_index = self._correctors.index(corr)

            self._corr_kick_sp_pvs[corr] = _epics.PV(
                self._PREFIX_VACA + corr + ':Kick-SP')

            self._corr_refkick[corr] = 0
            self._corr_kick_rb_pvs[corr] = _epics.PV(
                self._PREFIX_VACA + corr + ':Kick-RB',
                callback=self._callback_init_refkick,
                connection_callback=self._connection_callback_corr_kick_pvs)

            self._corr_pwrstate_sel_pvs[corr] = _epics.PV(
                self._PREFIX_VACA + corr + ':PwrState-Sel')
            if corr_index != 1:
                self._corr_pwrstate_sts_pvs[corr] = _epics.PV(
                    self._PREFIX_VACA + corr + ':PwrState-Sts',
                    callback=self._callback_corr_pwrstate_sts)

                self._corr_opmode_sel_pvs[corr] = _epics.PV(
                    self._PREFIX_VACA + corr + ':OpMode-Sel')
                self._corr_opmode_sts_pvs[corr] = _epics.PV(
                    self._PREFIX_VACA + corr + ':OpMode-Sts',
                    callback=self._callback_corr_opmode_sts)

                self._corr_ctrlmode_mon_pvs[corr] = _epics.PV(
                    self._PREFIX_VACA + corr + ':CtrlMode-Mon',
                    callback=self._callback_corr_ctrlmode_mon)
            else:
                # PU IOCs do not have PwrState-Sts PVs
                self._corr_pwrstate_sts_pvs[corr] = _epics.PV(
                    self._PREFIX_VACA + corr + ':PwrState-Sel',
                    callback=self._callback_corr_pwrstate_sts)

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
            updated = self._update_delta(value, self._orbx_deltaang, 'x')
            if updated:
                self._orbx_deltapos = value
                self.driver.setParam('DeltaPosX-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'DeltaAngX-SP':
            updated = self._update_delta(self._orbx_deltapos, value, 'x')
            if updated:
                self._orbx_deltaang = value
                self.driver.setParam('DeltaAngX-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'DeltaPosY-SP':
            updated = self._update_delta(value, self._orby_deltaang, 'y')
            if updated:
                self._orby_deltapos = value
                self.driver.setParam('DeltaPosY-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'DeltaAngY-SP':
            updated = self._update_delta(self._orby_deltapos, value, 'y')
            if updated:
                self._orby_deltaang = value
                self.driver.setParam('DeltaAngY-RB', value)
                self.driver.updatePVs()
                status = True

        elif reason == 'SetNewRefKick-Cmd':
            updated = self._update_ref()
            if updated:
                self._setnewrefkick_cmd_count += 1
                self.driver.setParam('SetNewRefKick-Cmd',
                                     self._setnewrefkick_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigMA-Cmd':
            done = self._config_ma()
            if done:
                self._config_ma_cmd_count += 1
                self.driver.setParam('ConfigMA-Cmd',
                                     self._config_ma_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigName-SP':
            [done, corrparams] = self._get_corrparams(value)
            if done:
                self._set_config_name(value)
                self.driver.setParam('ConfigName-RB', value)
                self._respmat_x = corrparams[0]
                self.driver.setParam('RespMatX-Mon', corrparams[0])
                self._respmat_y = corrparams[1]
                self.driver.setParam('RespMatY-Mon', corrparams[1])
                updated = self._update_delta(
                    self._orbx_deltapos, self._orbx_deltaang, 'x')
                updated = self._update_delta(
                    self._orby_deltapos, self._orby_deltaang, 'y')
                self.driver.setParam('Log-Mon', 'Updated correction matrices.')
                self.driver.updatePVs()
                status = True
            else:
                self.driver.setParam(
                    'Log-Mon', 'ERR:Configuration not found in configdb.')
                self.driver.updatePVs()  # in case PV states change.

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self, config_name):
        """Get response matrix from configurations database."""
        cs = _ConfigService()
        querry = cs.get_config(self._TL.lower()+'_posang_respm', config_name)
        querry_result = querry['code']

        if querry_result == 200:
            done = True
            mats = querry['result']['value']
            respmat_x = [item for sublist in mats['respm-x']
                         for item in sublist]
            respmat_y = [item for sublist in mats['respm-y']
                         for item in sublist]
            return [done, [respmat_x, respmat_y]]
        else:
            done = False
            return [done, []]

    def _get_config_name(self):
        try:
            f = open('/home/sirius/iocs/' + self._TL.lower() + '-ap-posang/' +
                     self._TL.lower() + '-posang.txt', 'r')
            config_name = f.read().strip('\n')
            f.close()
        except Exception:
            f = open('/home/sirius/iocs/' + self._TL.lower() + '-ap-posang/' +
                     self._TL.lower() + '-posang.txt', 'w+')
            config_name = 'Default'
            f.write(config_name)
            f.close()
        return config_name

    def _set_config_name(self, config_name):
        f = open('/home/sirius/iocs/' + self._TL.lower() + '-ap-posang/' +
                 self._TL.lower() + '-posang.txt', 'w+')
        f.write(config_name)
        f.close()

    def _update_delta(self, delta_pos, delta_ang, orbit):
        if orbit == 'x':
            respmat = self._respmat_x
            c1_kick_sp_pv = self._corr_kick_sp_pvs[self._correctors[0]]
            c2_kick_sp_pv = self._corr_kick_sp_pvs[self._correctors[1]]
            c1_refkick = self._corr_refkick[self._correctors[0]]
            c2_refkick = self._corr_refkick[self._correctors[1]]
            c1_unit_factor = 1e-6  # urad to rad
            c2_unit_factor = 1e-3  # mrad to rad
        else:
            respmat = self._respmat_y
            c1_kick_sp_pv = self._corr_kick_sp_pvs[self._correctors[2]]
            c2_kick_sp_pv = self._corr_kick_sp_pvs[self._correctors[3]]
            c1_refkick = self._corr_refkick[self._correctors[2]]
            c2_refkick = self._corr_refkick[self._correctors[3]]
            c1_unit_factor = 1e-6  # urad to rad
            c2_unit_factor = 1e-6  # urad to rad

        if self._status == _ALLCLR:
            # Convert to respm units (SI):
            #  - deltas position and angle from mrad and mm to rad and meters
            #  - refkicks from urad or mrad to rad
            delta_pos_meters = delta_pos*1e-3
            delta_ang_rad = delta_ang*1e-3
            c1_refkick_rad = c1_refkick*c1_unit_factor
            c2_refkick_rad = c2_refkick*c2_unit_factor

            [[c1_deltakick_rad], [c2_deltakick_rad]] = _np.dot(
                _np.linalg.inv(_np.reshape(respmat, (2, 2), order='C')),
                _np.array([[delta_pos_meters], [delta_ang_rad]]))

            # Convert kicks from rad to correctors units
            c1_kick_sp_pv.put(
                (c1_refkick_rad + c1_deltakick_rad)/c1_unit_factor)
            c2_kick_sp_pv.put(
                (c2_refkick_rad + c2_deltakick_rad)/c2_unit_factor)

            self.driver.setParam('Log-Mon', 'Applied new delta.')
            self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon',
                                 'ERR:Failed on applying new delta.')
            self.driver.updatePVs()
            return False

    def _update_ref(self):
        if (self._status & 0x1) == 0:  # Check connection
            # updates reference
            corr_id = ['CH1', 'CH2', 'CV1', 'CV2']
            for corr in self._correctors:
                corr_index = self._correctors.index(corr)
                value = self._corr_kick_rb_pvs[
                        self._correctors[corr_index]].get()
                # Get correctors kick in urad (MA) or mrad (PM).
                self._corr_refkick[self._correctors[corr_index]] = value
                self.driver.setParam('RefKick' + corr_id[corr_index] + '-Mon',
                                     value)

            # the deltas from new kick references are zero
            self._orbx_deltapos = 0
            self.driver.setParam('DeltaPosX-SP', 0)
            self.driver.setParam('DeltaPosX-RB', 0)
            self._orbx_deltaang = 0
            self.driver.setParam('DeltaAngX-SP', 0)
            self.driver.setParam('DeltaAngX-RB', 0)
            self._orby_deltapos = 0
            self.driver.setParam('DeltaPosY-SP', 0)
            self.driver.setParam('DeltaPosY-RB', 0)
            self._orby_deltaang = 0
            self.driver.setParam('DeltaAngY-SP', 0)
            self.driver.setParam('DeltaAngY-RB', 0)

            self.driver.setParam('Log-Mon', 'Updated Kick References.')
            updated = True
        else:
            self.driver.setParam('Log-Mon', 'ERR:Some pv is disconnected.')
            updated = False
        self.driver.updatePVs()
        return updated

    def _callback_init_refkick(self, pvname, value, cb_info, **kws):
        """Initialize RefKick-Mon pvs and remove this callback."""
        corr_index = self._correctors.index(_SiriusPVName(pvname).device_name)

        # Get reference. Correctors kick in urad (MA) or mrad (PM).
        self._corr_refkick[self._correctors[corr_index]] = value
        corr_id = ['CH1', 'CH2', 'CV1', 'CV2']
        self.driver.setParam('RefKick' + corr_id[corr_index] + '-Mon',
                             self._corr_refkick[self._correctors[corr_index]])

        # Remove callback
        cb_info[1].remove_callback(cb_info[0])

    def _connection_callback_corr_kick_pvs(self, pvname, conn, **kws):
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' disconnected.')
            self.driver.updatePVs()

        corr_index = self._correctors.index(_SiriusPVName(pvname).device_name)
        self._corr_check_connection[corr_index] = (1 if conn else 0)

        # Change the first bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=0,
            bit_val=any(q == 0 for q in self._corr_check_connection))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_corr_pwrstate_sts(self, pvname, value, **kws):
        if value != _PSConst.PwrStateSel.On:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' is not On.')

        corr_index = self._correctors.index(_SiriusPVName(pvname).device_name)
        self._corr_check_pwrstate_sts[corr_index] = value

        # Change the second bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=1,
            bit_val=any(q != _PSConst.PwrStateSel.On
                        for q in self._corr_check_pwrstate_sts))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_corr_opmode_sts(self, pvname, value, **kws):
        self.driver.setParam('Log-Mon', 'WARN:'+pvname+' changed.')
        self.driver.updatePVs()

        corr_index = self._correctors.index(_SiriusPVName(pvname).device_name)
        self._corr_check_opmode_sts[corr_index] = value

        # Change the third bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=2,
            bit_val=any(s != _PSConst.States.SlowRef
                        for s in self._corr_check_opmode_sts))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_corr_ctrlmode_mon(self,  pvname, value, **kws):
        if value != _PSConst.Interface.Remote:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' is not Remote.')
            self.driver.updatePVs()

        corr_index = self._correctors.index(_SiriusPVName(pvname).device_name)
        self._corr_check_ctrlmode_mon[corr_index] = value

        # Change the fourth bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=3,
            bit_val=any(q != _PSConst.Interface.Remote
                        for q in self._corr_check_ctrlmode_mon))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _config_ma(self):
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
