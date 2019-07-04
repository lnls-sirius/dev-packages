
"""Utilities for cycle."""

import time as _time
import numpy as _np
from math import isclose as _isclose
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch


def get_manames():
    """Return manames."""
    return _MASearch.get_manames({'sec': '(TB|BO)', 'dis': 'MA'})
    # TODO: uncomment when using TS and SI
    # return _MASearch.get_manames({'sec': '(TB|BO|TS|SI)', 'dis': 'MA'})


def get_manames_from_same_udc(maname):
    """Return manames that are controled by same udc as maname."""
    psname = _MASearch.conv_maname_2_psnames(maname)[0]
    udc = _PSSearch.conv_psname_2_udc(psname)
    bsmp_list = _PSSearch.conv_udc_2_bsmps(udc)
    psnames = [bsmp[0] for bsmp in bsmp_list]
    manames = set([_MASearch.conv_psname_2_psmaname(name) for name in psnames])
    return manames


def pv_timed_get(pv, value, wait=5):
    """Do timed get."""
    if not pv.connected:
        return False
    t0 = _time.time()
    while _time.time() - t0 < wait:
        pvvalue = pv.get()
        status = False
        if isinstance(value, (tuple, list, _np.ndarray)):
            if not isinstance(pvvalue, (tuple, list, _np.ndarray)):
                status = False
            elif len(value) != len(pvvalue):
                status = False
            else:
                for i in range(len(value)):
                    if _isclose(pvvalue[i], value[i],
                                rel_tol=1e-06, abs_tol=0.0):
                        status = True
                    else:
                        status = False
                        break
                else:
                    break
        else:
            if _isclose(pvvalue, value, rel_tol=1e-06, abs_tol=0.0):
                status = True
                break
            else:
                status = False
        _time.sleep(wait/10.0)
    return status


def pv_conn_put(pv, value):
    """Put if connected."""
    if not pv.connected:
        return False
    if pv.put(value):
        return True
    return False
