from .csdev import HLFOFBConst as _Const
from ..devices import FamFOFBControllers as _FamFOFBCtrls, Device as _Device,\
    FamFastCorrs as _FamFastCorrs, SOFB as _SOFB, RFGen as _RFGen

def set_default_psconfig_mat(self, option):
        """Set corrector accumulator filter."""

        _const = _Const()
        _llfofb_dev = _FamFOFBCtrls()

        corrnames = _const.ch_names + _const.cv_names
        _corrs_dev = _FamFastCorrs(corrnames)

        num_biquads = _llfofb_dev.fofbacc_filter_num_biquads
        unit = _const.FILTER_UNIT
        sw2 = _const.FILTER_SW_2
        sw4 = _const.FILTER_SW_4

        if option == 'Unit':
                filter_coeffs = num_biquads * unit

        if option == 'Switching':
               filter_coeffs = sw2 + sw4 + (num_biquads - 2) * unit

#             elif value == self._const.FilterOpt.Switching:
#                 filter = sw2 + sw4 + (num_biquads - 2) * unit

#             else:
#                 filter = self._corr_accfilter_val

#             self.run_callbacks('FOFBAccFilter-Sts', value)
#             self.run_callbacks('FOFBAccFilter-SP', filter)
#         else:
#             filter = value
#         self._corr_accfilter_val = filter

#         self._update_log('Setting FOFB Acc filter...')
#         self._corrs_dev.set_fofbacc_filter(filter)
#         self._update_log('...done!')
#         self.run_callbacks('FOFBAccFilter-RB', filter)

#         return True
