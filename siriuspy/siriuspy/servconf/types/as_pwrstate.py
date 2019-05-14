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
    ['LA-CN:H1MLPS-1:setpwm', _on, 0.0],
    ['LA-CN:H1MLPS-2:setpwm', _on, 0.0],
    ['LA-CN:H1MLPS-3:setpwm', _on, 0.0],
    ['LA-CN:H1MLPS-4:setpwm', _on, 0.0],
    ['LA-CN:H1SCPS-1:setpwm', _on, 0.0],
    ['LA-CN:H1SCPS-2:setpwm', _on, 0.0],
    ['LA-CN:H1SCPS-3:setpwm', _on, 0.0],
    ['LA-CN:H1SCPS-4:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-1:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-2:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-3:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-4:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-5:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-6:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-7:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-8:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-9:setpwm', _on, 0.0],
    ['LA-CN:H1LCPS-10:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-1:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-2:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-3:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-4:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-5:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-6:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-7:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-8:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-9:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-10:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-11:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-12:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-13:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-14:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-15:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-16:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-17:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-18:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-19:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-20:setpwm', _on, 0.0],
    ['LA-CN:H1SLPS-21:setpwm', _on, 0.0],
    ['LA-CN:H1FQPS-1:setpwm', _on, 0.0],
    ['LA-CN:H1FQPS-2:setpwm', _on, 0.0],
    ['LA-CN:H1FQPS-3:setpwm', _on, 0.0],
    ['LA-CN:H1DQPS-1:setpwm', _on, 0.0],
    ['LA-CN:H1DQPS-2:setpwm', _on, 0.0],
    ['LA-CN:H1RCPS-1:setpwm', _on, 0.0],
    ['LA-CN:H1DPPS-1:setpwm', _on, 0.0],
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
    ['TB-04:PS-CH:PwrState-Sel', _on, 0.0],
    ['TB-04:PS-CV-1:PwrState-Sel', _on, 0.0],
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
