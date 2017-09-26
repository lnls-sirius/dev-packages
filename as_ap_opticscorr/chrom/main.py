"""Main module of AS-AP-OpticsCorr-Chrom IOC."""

import time as _time
import epics as _epics
import siriuspy as _siriuspy
import siriuspy.servweb as _siriuspy_servweb
from as_ap_opticscorr.opticscorr_utils import OpticsCorr
import as_ap_opticscorr.chrom.pvs as _pvs

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
            ioc_name=_pvs._ACC+'-AP-OpticsCorr-Chrom',
            db=App.pvs_database,
            description=_pvs._ACC+'-AP-OpticsCorr-Chrom Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list(
            _pvs._ACC.lower()+'-ap-opticscorr-chrom',
            (_pvs._DEVICE,
             _pvs._PREFIX_VACA),
            App.pvs_database)

        self._driver = driver
        self._pvs_database = App.pvs_database

        self._sfam_sl_mon_pvs = {}
        self._sfam_sl_sp_pvs = {}
        self._sfam_pwrstate_sts_pvs = {}
        self._sfam_slrefs = {}
        for fam in _pvs._SFAMS:
            self._sfam_sl_mon_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':SL-Mon',
                connection_timeout=0.05)
            self._sfam_sl_sp_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':SL-SP',
                connection_timeout=0.05)
            self._sfam_pwrstate_sts_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':PwrState-Sts',
                connection_timeout=0.05)

        # Initialize from static tables
        # If needed to set chrom 0 and corrmat from control system, discomment
        # code (main and pvs) related to these pvs and change initializing

        self._lastcalcd_sl = len(_pvs._SFAMS)*[0]

        if _pvs._ACC == 'BO':
            corrmat, chrom0 = self._get_srefs_corrmat_and_chrom0()
        elif _pvs._ACC == 'SI':
            corrmat, chrom0, srefs = self._get_srefs_corrmat_and_chrom0()
            # Reference SL are SLnom for initial case
            self._sfam_slrefs = srefs

        self._opticscorrection = OpticsCorr()

        # Using grouping and proportional method, the number of famlies is 2:
        # Focusing and Defocusing Groups
        mat, invmat = self._opticscorrection.set_corr_mat(
            'chrom', 2, corrmat)
        # self.driver.setParam('ChromCorrMat-RB', mat)
        # self.driver.setParam('ChromCorrInvMat-Mon', invmat)
        # self.driver.setParam('InitialChrom-RB', chrom0)
        # self.driver.updatePVs()

        # Change these lines if initializing considers last set tune that can
        # be in a local archive
        chrom0 = self._opticscorrection.set_chrom0(chrom0[0], chrom0[1])
        self._chromx = chrom0[0]
        self.driver.setParam('ChromX-SP', chrom0[0])
        self.driver.setParam('ChromX-RB', chrom0[0])
        self._chromy = chrom0[1]
        self.driver.setParam('ChromY-SP', chrom0[1])
        self.driver.setParam('ChromY-RB', chrom0[1])
        # Delete these pvs if access to chrom0 is enable to control system
        self.driver.setParam('InitialChromX-Mon', chrom0[0])
        self.driver.setParam('InitialChromY-Mon', chrom0[1])
        self.driver.updatePVs()

        self._corr_factor = 0.0
        self._calc_sl_cmd_count = 0
        self._apply_sl_cmd_count = 0

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
        if reason == 'ChromX-SP':
            self._chromx = value
            self.driver.setParam('ChromX-RB', value)
            self.driver.updatePVs()  # in case PV states change.
            status = True
        elif reason == 'ChromY-SP':
            self._chromy = value
            self.driver.setParam('ChromY-RB', value)
            self.driver.updatePVs()
            status = True

        elif reason == 'CalcSL-Cmd':
            self._calc_sl_cmd_count += 1
            self.driver.setParam('CalcSL-Cmd',
                                 self._calc_sl_cmd_count)
            self._calc_sl()
            for fam in _pvs._SFAMS:
                fam_index = _pvs._SFAMS.index(fam)
                self.driver.setParam('LastCalcd' + fam + 'SL-Mon',
                                     self._lastcalcd_sl[fam_index])
            self.driver.updatePVs()
        elif reason == 'ApplySL-Cmd':
            self._apply_sl_cmd_count += 1
            self.driver.setParam('ApplySL-Cmd',
                                 self._apply_sl_cmd_count)
            self._apply_sl()
            self.driver.updatePVs()

        # elif reason == 'ChromCorrMat-SP':
        #     mat, invmat = self._opticscorrection.set_corr_mat(
        #         'chrom', len(_pvs._SFAMS), value)
        #     if (mat is not None) and (invmat is not None):
        #         self.driver.setParam('ChromCorrMat-RB', mat)
        #         self.driver.setParam('ChromCorrInvMat-Mon', invmat)
        #         status = True
        # elif reason == 'InitialChromX-SP':
        #     chrom0y = self._opticscorrection.chrom0[1]
        #     chrom0 = self._opticscorrection.set_chrom0(value, chrom0y)
        #     self.driver.setParam('InitialChromX-RB', chrom0)
        #     status = True
        # elif reason == 'InitialChromY-SP':
        #     chrom0x = self._opticscorrection.chrom0[0]
        #     chrom0 = self._opticscorrection.set_chrom0(chrom0x, value)
        #     self.driver.setParam('InitialChromY-RB', chrom0)
        #     status = True
        return status  # return True to invoke super().write of PCASDriver

    def _get_srefs_corrmat_and_chrom0(self):
        m, _ = _siriuspy_servweb.response_matrix_read(
            _pvs._ACC.lower()+'-optics-correction-chromaticity.txt')

        chrom0 = [0, 0]
        chrom0[0] = float(m[0][0])
        chrom0[1] = float(m[0][1])

        chrom_corrmat = 2*2*[0]  # Just 2 columns: SFs and SDs
        index = 0
        for coordinate in [1, 2]:  # Read in C-like format
            for fam in [0, 1]:  # Just 2 columns: SFs and SDs
                chrom_corrmat[index] = float(m[coordinate][fam])
                index += 1

        if _pvs._ACC == 'BO':
            return chrom_corrmat, chrom0

        srefs = {}
        if _pvs._ACC == 'SI':
            for fam in _pvs._SFAMS:
                fam_index = _pvs._SFAMS.index(fam)
                srefs[fam] = float(m[3][fam_index])

            return chrom_corrmat, chrom0, srefs

    def _calc_sl(self):
        if _pvs._ACC == 'SI':
            lastcalcd_propfactor = self._opticscorrection.calc_sl(
                self._chromx, self._chromy)
            for fam in _pvs._SFAMS:
                fam_index = _pvs._SFAMS.index(fam)
                if 'SF' in fam:
                    self._lastcalcd_sl[fam_index] = (
                        self._sfam_slrefs[fam]*lastcalcd_propfactor[0])
                elif 'SD' in fam:
                    self._lastcalcd_sl[fam_index] = (
                        self._sfam_slrefs[fam]*(lastcalcd_propfactor[1]))

        elif _pvs._ACC == 'BO':
            self._lastcalcd_sl = self._opticscorrection.calc_sl(
                self._chromx, self._chromy)

    def _apply_sl(self):
        for fam in self._sfam_sl_sp_pvs:
            pv = self._sfam_sl_sp_pvs[fam]
            if not pv.connected:
                print(pv.pvname + ' is disconnected')
                return False

        for fam in self._sfam_pwrstate_sts_pvs:
            pv = self._sfam_pwrstate_sts_pvs[fam]
            if pv.get() != 1:
                print(pv.pvname + ' is off')
                return False

        for fam in self._sfam_sl_sp_pvs:
            fam_index = _pvs._SFAMS.index(fam)
            pv = self._sfam_sl_sp_pvs[fam]
            pv.put(self._lastcalcd_sl[fam_index])
        return True
