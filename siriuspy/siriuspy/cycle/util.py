
"""Utilities for cycle."""

import time as _time
import math as _math
import numpy as _np

from ..csdev import Const as _Const
from ..namesys import Filter as _Filter
from ..search import PSSearch as _PSSearch, HLTimeSearch as _HLTimeSearch


TRIGGER_NAMES = {
    'TB-Glob:TI-Mags', 'TS-Glob:TI-Mags',
    'BO-Glob:TI-Mags-Fams', 'BO-Glob:TI-Mags-Corrs',
    'SI-Glob:TI-Mags-Bends', 'SI-Glob:TI-Mags-Quads',
    'SI-Glob:TI-Mags-Sexts', 'SI-Glob:TI-Mags-Skews',
    'SI-Glob:TI-Mags-Corrs', 'SI-Glob:TI-Mags-QTrims'}


def get_psnames(isadv=False):
    """Return psnames."""
    names = _PSSearch.get_psnames({'sec': '(LI|TB|TS)', 'dis': 'PS'})

    if not isadv:
        names.extend(_PSSearch.get_psnames(
            {'sec': 'SI', 'sub': 'Fam', 'dis': 'PS', 'dev': '(B|Q.*|S.*)'}))
        names.extend(_PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '[0-2][0-9]C2', 'dis': 'PS',
             'dev': 'CV', 'idx': '2'}))
        names.extend(_PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '[0-2][0-9]C2', 'dis': 'PS',
             'dev': 'QS'}))
        names.extend(_PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '[0-2][0-9]S(A|B|P)', 'dis': 'PS',
             'dev': '(CH|CV|QS)'}))
        names.extend(_PSSearch.get_psnames(
            {'sec': 'SI', 'dis': 'PS', 'dev': 'FC.*'}))
    else:
        names.extend(_PSSearch.get_psnames(
            {'sec': 'SI', 'dis': 'PS', 'dev': '(B|Q.*|S.*|C.*|FC.*)'}))

    to_remove = _PSSearch.get_psnames({'sec': 'TS', 'idx': '(0|1E2)'})
    to_remove.extend(_PSSearch.get_psnames(
        {'sec': 'SI', 'sub': '(10SB|17SA)', 'dev': '(CH|CV|QS)'}))
    to_remove.extend(_PSSearch.get_psnames(
        {'sec': 'SI', 'sub': '(01M1|01M2)', 'dev': '(FCH|FCV)'}))
    for name in to_remove:
        names.remove(name)
    return names


def get_sections(psnames):
    """Return sections."""
    sections = list()
    for sec in ('LI', 'TB', 'BO', 'TS', 'SI'):
        if _Filter.process_filters(psnames, filters={'sec': sec}):
            sections.append(sec)
    return sections


def get_trigger_by_psname(psnames):
    """Return triggers corresponding to psnames."""
    psnames = set(psnames)
    triggers = set()
    for trig in TRIGGER_NAMES:
        dev_names = set(_HLTimeSearch.get_hl_trigger_channels(trig))
        dev_names = {dev.device_name for dev in dev_names}
        if psnames & dev_names:
            triggers.add(trig)
    return triggers


def pv_timed_get(pvobj, value, wait=5, abs_tol=0.0, rel_tol=1e-06):
    """Do timed get."""
    if not pvobj.connected:
        return False
    time0 = _time.time()
    while _time.time() - time0 < wait:
        pvvalue = pvobj.value
        if isinstance(value, (tuple, list, _np.ndarray)):
            if not isinstance(pvvalue, (tuple, list, _np.ndarray)):
                _time.sleep(wait/10.0)
                continue
            elif len(value) != len(pvvalue):
                _time.sleep(wait/10.0)
                continue
            else:
                if _np.allclose(pvvalue, value, atol=abs_tol, rtol=rel_tol):
                    return True
        else:
            if _math.isclose(pvvalue, value, abs_tol=abs_tol, rel_tol=rel_tol):
                return True
    return False


def pv_conn_put(pvobj, value):
    """Put if connected."""
    if not pvobj.connected:
        return False
    if pvobj.put(value):
        return True
    return False


class Const(_Const):
    """PSCycle Constants."""

    CycleEndStatus = _Const.register(
        'CycleEndStatus', ('Ok', 'LackTriggers', 'NotFinished', 'Interlock'))
