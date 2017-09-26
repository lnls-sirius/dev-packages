"""Main module of AS-AP-OpticsCorr-Tune IOC."""

import time as _time
import epics as _epics
import siriuspy as _siriuspy
import siriuspy.servweb as _siriuspy_servweb
from as_ap_opticscorr.opticscorr_utils import OpticsCorr
import as_ap_opticscorr.tune.pvs as _pvs

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
            ioc_name=_pvs._ACC+'-AP-OpticsCorr-Tune',
            db=App.pvs_database,
            description=_pvs._ACC+'-AP-OpticsCorr-Tune Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list(
            _pvs._ACC.lower()+'-ap-opticscorr-tune',
            (_pvs._DEVICE,
             _pvs._PREFIX_VACA),
            App.pvs_database)

        self._driver = driver
        self._pvs_database = App.pvs_database

        self._qfam_kl_mon_pvs = {}
        self._qfam_kl_sp_pvs = {}
        self._qfam_pwrstate_sts_pvs = {}
        self._qfam_klrefs = {}
        for fam in _pvs._QFAMS:
            self._qfam_kl_mon_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':KL-Mon')
            self._qfam_kl_mon_pvs[fam].wait_for_connection(timeout=0.05)
            self._qfam_kl_sp_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':KL-SP',
                connection_timeout=0.05)
            self._qfam_pwrstate_sts_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':PwrState-Sts',
                connection_timeout=0.05)
            self._qfam_klrefs[fam] = self._qfam_kl_mon_pvs[fam].get()

        self._lastcalcd_deltakl = len(_pvs._QFAMS)*[0]
        self._update_ref()

        self._opticscorrection = OpticsCorr()

        # Initialize from static tables
        # If needed to set corrmat from control system, discomment code
        # (main and pvs) related to these pvs and change initializing
        # Using grouping and proportional method, the number of famlies is 2:
        # Focusing and Defocusing Groups
        mat, invmat = self._opticscorrection.set_corr_mat(
            'tune', 2, self._get_corrmat())
        # self.driver.setParam('TuneCorrMat-RB', mat)
        # self.driver.setParam('TuneCorrInvMat-Mon', invmat)
        # self.driver.updatePVs()

        self._delta_tunex = 0
        self._delta_tuney = 0
        self._corr_factor = 0.0
        self._calc_deltakl_cmd_count = 0
        self._apply_deltakl_cmd_count = 0
        self._set_new_kl_ref_cmd_count = 0

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
        if reason == 'DeltaTuneX-SP':
            self._delta_tunex = value
            self.driver.setParam('DeltaTuneX-RB', value)
            self.driver.updatePVs()
            status = True
        elif reason == 'DeltaTuneY-SP':
            self._delta_tuney = value
            self.driver.setParam('DeltaTuneY-RB', value)
            self.driver.updatePVs()
            status = True

        elif reason == 'CalcDeltaKL-Cmd':
            self._calc_deltakl_cmd_count += 1
            self.driver.setParam('CalcDeltaKL-Cmd',
                                 self._calc_deltakl_cmd_count)
            self._calc_deltakl()
            for fam in _pvs._QFAMS:
                fam_index = _pvs._QFAMS.index(fam)
                self.driver.setParam('LastCalcd' + fam + 'DeltaKL-Mon',
                                     self._lastcalcd_deltakl[fam_index])
            self.driver.updatePVs()
        elif reason == 'ApplyDeltaKL-Cmd':
            self._apply_deltakl_cmd_count += 1
            self.driver.setParam('ApplyDeltaKL-Cmd',
                                 self._apply_deltakl_cmd_count)
            self._apply_deltakl()
            self.driver.updatePVs()

        # elif reason == 'TuneCorrMat-SP':
        #     mat, invmat = self._opticscorrection.set_corr_mat(
        #         'tune', len(_pvs._QFAMS), value)
        #     if (mat is not None) and (invmat is not None):
        #         self.driver.setParam('TuneCorrMat-RB', mat)
        #         self.driver.setParam('TuneCorrInvMat-Mon', invmat)
        #         status = True
        elif reason == 'TuneCorrFactor-SP':
            self._corr_factor = value
            self.driver.setParam('TuneCorrFactor-RB', value)
            self.driver.updatePVs()
            status = True

        elif reason == 'SetNewKLRef-Cmd':
            self._set_new_kl_ref_cmd_count += 1
            self.driver.setParam('SetNewKLRef-Cmd',
                                 self._set_new_kl_ref_cmd_count)
            self._update_ref()
            self.driver.updatePVs()  # in case PV states change.
        return status  # return True to invoke super().write of PCASDriver

    def _get_corrmat(self):
        m, _ = _siriuspy_servweb.response_matrix_read(
            _pvs._ACC.lower()+'-optics-correction-tune.txt')

        tune_corrmat = 2*2*[0]  # Just 2 columns: SFs and SDs
        index = 0
        for coordinate in [0, 1]:  # Read in C-like format
            for fam in [0, 1]:  # Just 2 columns: SFs and SDs
                tune_corrmat[index] = float(m[coordinate][fam])
                index += 1
        return tune_corrmat

    def _calc_deltakl(self):
        if _pvs._ACC == 'SI':
            lastcalcd_propfactor = self._opticscorrection.calc_deltakl(
                self._delta_tunex, self._delta_tuney)
            for fam in _pvs._QFAMS:
                fam_index = _pvs._QFAMS.index(fam)
                if 'QF' in fam:
                    self._lastcalcd_deltakl[fam_index] = (
                        self._qfam_klrefs[fam]*lastcalcd_propfactor[0])
                elif 'QD' in fam:
                    self._lastcalcd_deltakl[fam_index] = (
                        self._qfam_klrefs[fam]*lastcalcd_propfactor[1])

        elif _pvs._ACC == 'BO':
            self._lastcalcd_deltakl = self._opticscorrection.calc_deltakl(
                self._delta_tunex, self._delta_tuney)

    def _apply_deltakl(self):
        for fam in self._qfam_kl_sp_pvs:
            pv = self._qfam_kl_sp_pvs[fam]
            if not pv.connected:
                print(pv.pvname + ' is disconnected')
                return False

        for fam in self._qfam_pwrstate_sts_pvs:
            pv = self._qfam_pwrstate_sts_pvs[fam]
            if pv.get() != 1:
                print(pv.pvname + ' is off')
                return False

        for fam in self._qfam_kl_sp_pvs:
            fam_index = _pvs._QFAMS.index(fam)
            pv = self._qfam_kl_sp_pvs[fam]
            pv.put(self._qfam_klrefs[fam] +
                   self._corr_factor*self._lastcalcd_deltakl[fam_index]/100)
        return True

    def _update_ref(self):
        # updates reference
        for fam in _pvs._QFAMS:
            self._qfam_klrefs[fam] = self._qfam_kl_mon_pvs[fam].get()
            self.driver.setParam(fam + 'KLRef-Mon', self._qfam_klrefs[fam])

            fam_index = _pvs._QFAMS.index(fam)
            self._lastcalcd_deltakl[fam_index] = 0
            self.driver.setParam('LastCalcd' + fam + 'DeltaKL-Mon',
                                 self._lastcalcd_deltakl[fam_index])

        # the deltas from new kl references are zero
        self._delta_tunex = 0
        self._delta_tuney = 0
        self.driver.setParam('DeltaTuneX-SP', self._delta_tunex)
        self.driver.setParam('DeltaTuneX-RB', self._delta_tunex)
        self.driver.setParam('DeltaTuneY-SP', self._delta_tuney)
        self.driver.setParam('DeltaTuneY-RB', self._delta_tuney)
