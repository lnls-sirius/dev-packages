"""Booster strenght PVs."""
import re
from siriuspy.search import MASearch


def get_dict():
    """Return BO PVs as dict."""
    module_name = __name__.split('.')[-1]
    pvs = dict()
    slots = MASearch.get_manames({"dis": "MA"})
    if slots:
        for slot in slots:
            strength_name = getStrengthName(slot)
            pv = slot + ":" + strength_name + "-RB"
            if re.match("^BO-\w{2,4}:MA-(B|Q|S|C|F)", pv):
                pvs[pv] = 0.0
    _dict = {
        'config_type_name': module_name,
        'value': pvs
    }
    return _dict


def getStrengthName(slot):
    """Return strength name for given device."""
    if re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-B", slot):
        return "Energy"
    elif re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-Q", slot):
        return "KL"
    elif re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-S", slot):
        return "SL"
    elif re.match("^[A-Z]{2}-\w{2,4}:[A-Z]{2}-(C|F)", slot):
        return "Kick"
    else:
        raise NotImplementedError
