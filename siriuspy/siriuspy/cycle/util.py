
"""Utilities for cycle."""

import time as _time
import numpy as _np
from math import isclose as _isclose
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
from siriuspy.search import PSSearch as _PSSearch


def get_psnames():
    """Return psnames."""
    names = _PSSearch.get_psnames({'sec': '(TB|BO)', 'dis': 'PS'})
    # TODO: uncomment when using TS and SI
    # names = _PSSearch.get_psnames({'sec': '(TB|BO|TS|SI)', 'dis': 'PS'})
    names.extend(_PSSearch.get_psnames({'sec': 'LI'}))
    return names


def get_psnames_from_same_udc(psname):
    """Return psnames that are controled by same udc as psname."""
    psname = _PVName(psname)
    if psname.dev == 'B':
        psnames = _PSSearch.get_psnames({'sec': psname.sec, 'dev': 'B'})
    else:
        udc = _PSSearch.conv_psname_2_udc(psname)
        bsmp_list = _PSSearch.conv_udc_2_bsmps(udc)
        psnames = [bsmp[0] for bsmp in bsmp_list]
    return psnames


def get_sections(psnames):
    sections = list()
    for s in ['LI', 'TB', 'BO', 'TS', 'SI']:
        if _Filter.process_filters(psnames, filters={'sec': s}):
            sections.append(s)
    return sections


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
