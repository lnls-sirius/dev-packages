
"""Utilities for cycle."""

import time as _time
import numpy as _np
from math import isclose as _isclose
from siriuspy.namesys import Filter as _Filter
from siriuspy.search import PSSearch as _PSSearch


def get_psnames():
    """Return psnames."""
    names = _PSSearch.get_psnames({'sec': '(LI|TB|BO|TS)', 'dis': 'PS'})
    names.extend(_PSSearch.get_psnames(
        {'sec': 'SI', 'sub': 'Fam', 'dis': 'PS', 'dev': '(B|Q.*|S.*)'}))
    names.extend(_PSSearch.get_psnames(
        {'sec': 'SI', 'sub': '[0-2][0-9]C2', 'dis': 'PS',
         'dev': 'CV', 'idx': '2'}))
    return names


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
