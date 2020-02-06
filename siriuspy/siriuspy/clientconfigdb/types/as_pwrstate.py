"""AS PowerState On configuration."""
from copy import deepcopy as _dcopy


_on = 1


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict),
        'check': False,
    }
    return _dict


# When using this type of configuration to set the machine,
# the list of PVs should be processed in the same order they are stored
# in the configuration. The second numeric parameter in the pair is the
# delay [s] the client should wait before setting the next PV.


_pvs_li_ps = [
    ['LI-01:PS-LensRev:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Lens-1:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Lens-2:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Lens-3:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Lens-4:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CV-1:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CH-1:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CV-2:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CH-2:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CV-3:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CH-3:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CV-4:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CH-4:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CV-5:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CH-5:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CV-6:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CH-6:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CV-7:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-CH-7:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-1:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-2:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-3:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-4:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-5:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-6:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-7:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-8:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-9:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-10:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-11:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-12:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Slnd-13:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-14:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-15:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-16:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-17:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-18:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-19:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-20:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-Slnd-21:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-QF1:PwrState-Sel', _on, 0.0],
    ['LI-Fam:PS-QF2:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-QF3:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-QD1:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-QD2:PwrState-Sel', _on, 0.0],
    ['LI-01:PS-Spect:PwrState-Sel', _on, 0.0],
    ]

_pvs_tb_ps = [
    ['TB-Fam:PS-B:PwrState-Sel', _on, 0.0],
    ['TB-01:PS-QD1:PwrState-Sel', _on, 0.0],
    ['TB-01:PS-QF1:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-QD2A:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-QF2A:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-QF2B:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-QD2B:PwrState-Sel', _on, 0.0],
    ['TB-03:PS-QF3:PwrState-Sel', _on, 0.0],
    ['TB-03:PS-QD3:PwrState-Sel', _on, 0.0],
    ['TB-04:PS-QF4:PwrState-Sel', _on, 0.0],
    ['TB-04:PS-QD4:PwrState-Sel', _on, 0.0],
    ['TB-01:PS-CH-1:PwrState-Sel', _on, 0.0],
    ['TB-01:PS-CV-1:PwrState-Sel', _on, 0.0],
    ['TB-01:PS-CH-2:PwrState-Sel', _on, 0.0],
    ['TB-01:PS-CV-2:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-CH-1:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-CV-1:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-CH-2:PwrState-Sel', _on, 0.0],
    ['TB-02:PS-CV-2:PwrState-Sel', _on, 0.0],
    ['TB-04:PS-CH-1:PwrState-Sel', _on, 0.0],
    ['TB-04:PS-CV-1:PwrState-Sel', _on, 0.0],
    ['TB-04:PS-CH-2:PwrState-Sel', _on, 0.0],
    ['TB-04:PS-CV-2:PwrState-Sel', _on, 0.0],
    ]

_pvs_pu = [
    ['TB-04:PU-InjSept:PwrState-Sel', 0, 0.0],
    ['BO-01D:PU-InjKckr:PwrState-Sel', 0, 0.0],
    ]

_pvs_bo_ps = [
    ['BO-Fam:PS-B-1:PwrState-Sel', _on, 0.0],
    ['BO-Fam:PS-B-2:PwrState-Sel', _on, 0.0],
    ['BO-Fam:PS-QD:PwrState-Sel', _on, 0.0],
    ['BO-Fam:PS-QF:PwrState-Sel', _on, 0.0],
    ['BO-02D:PS-QS:PwrState-Sel', _on, 0.0],
    ['BO-Fam:PS-SD:PwrState-Sel', _on, 0.0],
    ['BO-Fam:PS-SF:PwrState-Sel', _on, 0.0],
    ['BO-01U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-03U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-05U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-07U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-09U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-11U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-13U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-15U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-17U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-19U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-21U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-23U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-25U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-27U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-29U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-31U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-33U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-35U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-37U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-39U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-41U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-43U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-45U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-47U:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-49D:PS-CH:PwrState-Sel', _on, 0.0],
    ['BO-01U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-03U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-05U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-07U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-09U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-11U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-13U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-15U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-17U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-19U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-21U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-23U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-25U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-27U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-29U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-31U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-33U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-35U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-37U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-39U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-41U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-43U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-45U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-47U:PS-CV:PwrState-Sel', _on, 0.0],
    ['BO-49U:PS-CV:PwrState-Sel', _on, 0.0],
    ]

_template_dict = {
    'pvs':
        _pvs_li_ps + _pvs_tb_ps + _pvs_pu + _pvs_bo_ps
    }
