
"""Utilities for cycle."""

import time as _time
import numpy as _np
from siriuspy.namesys import Filter as _Filter
from siriuspy.search import PSSearch as _PSSearch


def get_psnames():
    """Return psnames."""
    names = _PSSearch.get_psnames({'sec': '(LI|TB|BO|TS)', 'dis': 'PS'})
    # names.extend(_PSSearch.get_psnames(
    #     {'sec': 'SI', 'sub': 'Fam', 'dis': 'PS', 'dev': '(B|Q.*|S.*)'}))
    # names.extend(_PSSearch.get_psnames(
    #     {'sec': 'SI', 'sub': '[0-2][0-9]C2', 'dis': 'PS',
    #      'dev': 'CV', 'idx': '2'}))
    return names


def get_sections(psnames):
    sections = list()
    for s in ['LI', 'TB', 'BO', 'TS', 'SI']:
        if _Filter.process_filters(psnames, filters={'sec': s}):
            sections.append(s)
    return sections


def get_trigger_by_psname(psnames):
    triggers = set()
    if _Filter.process_filters(psnames, filters={'sec': 'TB'}):
        triggers.add('TB-Glob:TI-Mags')
    if _Filter.process_filters(psnames, filters={'sec': 'TS'}):
        triggers.add('TS-Glob:TI-Mags')
    if _Filter.process_filters(psnames, filters={'sec': 'BO', 'sub': 'Fam'}):
        triggers.add('BO-Glob:TI-Mags-Fams')
    if _Filter.process_filters(
            psnames, filters={'sec': 'BO', 'sub': '[0-2][0-9].*'}):
        triggers.add('BO-Glob:TI-Mags-Corrs')
    if _Filter.process_filters(psnames, filters={'sec': 'SI', 'dev': 'B1B2'}):
        triggers.add('SI-Glob:TI-Mags-Bends')
    if _Filter.process_filters(psnames, filters={
            'sec': 'SI', 'sub': 'Fam', 'dev': '(QD.*|QF.*|Q[1-4])'}):
        triggers.add('SI-Glob:TI-Mags-Quads')
    if _Filter.process_filters(psnames, filters={
            'sec': 'SI', 'sub': '[0-2][0-9].*', 'dev': '(QD.*|QF.*|Q[1-4])'}):
        triggers.add('SI-Glob:TI-Mags-QTrims')
        # TODO: remove following line when timing table is updated
        triggers.add('SI-Glob:TI-Mags-Skews')
    if _Filter.process_filters(psnames, filters={'sec': 'SI', 'dev': 'QS'}):
        triggers.add('SI-Glob:TI-Mags-Skews')
        # TODO: remove following line when timing table is updated
        triggers.add('SI-Glob:TI-Mags-QTrims')
    if _Filter.process_filters(psnames, filters={'sec': 'SI', 'dev': 'S.*'}):
        triggers.add('SI-Glob:TI-Mags-Sexts')
    if _Filter.process_filters(psnames, filters={'sec': 'SI', 'dev': 'C.*'}):
        triggers.add('SI-Glob:TI-Mags-Corrs')
    return triggers


def pv_timed_get(pv, value, wait=5, abs_tol=0.0, rel_tol=1e-06):
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
                if all(_np.isclose(pvvalue, value,
                                   atol=abs_tol, rtol=rel_tol)):
                    status = True
                    break
        else:
            if _np.isclose(pvvalue, value, atol=abs_tol, rtol=rel_tol):
                status = True
                break
        _time.sleep(wait/10.0)
    return status


def pv_conn_put(pv, value):
    """Put if connected."""
    if not pv.connected:
        return False
    if pv.put(value):
        return True
    return False
