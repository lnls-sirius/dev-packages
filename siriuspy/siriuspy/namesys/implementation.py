"""Implementation of namesys functions nad classes."""

import types as _types
import re as _re


_attrs = (
    'channel_type',
    'prefix',
    'sec',
    'sub',
    'dis',
    'dev',
    'idx',
    'propty',
    'field',
    'device_name',
    'area_name',
    'propty_name',
    'propty_suffix',
    'device_propty',
)


def get_siriuspvname_attrs():
    """Return SiriusPVName attributes."""
    return [attr for attr in _attrs]


def join_name(**kwargs):
    """Return SiriusPVName object.

    Parameters
    ----------
    channel_type [str] : PyDM channel type, ex: 'ca'
    prefix [str] : Prefix, ex: 'fac-454lnls'
    sec [str] : Section, ex: 'SI'
    sub [str] : Subsection, ex: 'Glob'
    dis [str] : Discipline, ex: 'PS'
    dev [str] : Device, ex: 'B'
    idx [str] : Device index, ex: '1'
    propty_name [str] : Property name, ex: 'Properties'
    propty_suffix [str] : Property suffix, ex: 'Cte'
    propty [str] : Full property, ex: 'Properties-Cte'
    field [str] : Field, ex: 'STATUS'
    """
    e = {k: v for k, v in kwargs.items() if v}  # get valid args
    name = ''
    if len(e.keys()) == 1:
        if 'propty' in e.keys():
            name = e['propty']
        elif 'propty_name' in e.keys():
            name = e['propty_name']
    elif len(e.keys()) == 2:
        if 'sec' in e.keys() and 'sub' in e.keys():
            name = e['sec'].upper() + '-' + e['sub']
        elif 'dis' in e.keys() and 'dev' in e.keys():
            name = e['dis'].upper() + '-' + e['dev']
        elif 'propty_name' in e.keys() and 'propty_suffix' in e.keys():
            name = e['propty_name'].upper() + '-' + e['propty_name']
    elif len(e.keys()) == 3:
        if 'dis' in e.keys() and 'dev' in e.keys() and 'idx' in e.keys():
            name = e['dis'].upper() + '-' + e['dev'] + '-' + e['idx']
    elif len(e.keys()) > 3:
        name = e['channel_type'] + '://' if 'channel_type' in e.keys() else ''
        name = e['prefix'] + '-' if 'prefix' in e.keys() else ''
        name += (e['sec'].upper() + '-' + e['sub'] + ':' +
                 e['dis'].upper() + '-' + e['dev'])
        name += ('-' + e['idx']) if 'idx' in e.keys() else ''
        if 'propty_name' in e.keys() and 'propty_suffix' in e.keys():
            name += ':' + e['propty_name'] + '-' + e['propty_suffix']
            name += ('.' + e['field']) if 'field' in e.keys() else ''
        elif 'propty' in e.keys():
            name += ':' + e['propty']
            name += ('.' + e['field']) if 'field' in e.keys() else ''
        elif 'propty_name' in e.keys():
            name += ':' + e['propty_name']

    if not name:
        raise TypeError('Not a valid SiriusPVName elements set!')
    return SiriusPVName(name)


def split_name(pvname, elements='propty'):
    """Return dict with PV name split into fields."""
    # empty dictionary
    dic_ = {attr: '' for attr in _attrs}
    # strip PV name
    pvname = pvname.strip()
    if len(pvname) == 0:
        return dic_

    # deals with channel
    dic_['channel_type'] = ''
    names = pvname.split('://')
    if len(names) == 2:
        dic_['channel_type'] = names[0]
        pvname = names[1]

    list_ = pvname.split(':')

    if len(list_) == 1:
        slist_ = list_[0].split('-')
        if len(slist_) == 1:
            dic_['propty'] = slist_[0]
            dic_['propty_name'] = slist_[0]
        elif len(slist_) == 2:
            if elements == 'propty':
                dic_['propty'] = slist_[0]
                dic_['propty_name'] = slist_[0]
                dic_['propty_suffix'] = slist_[1]
            elif elements == 'sec-sub':
                dic_['sec'] = slist_[0]
                dic_['sub'] = slist_[1]
                dic_['area_name'] = slist_[0] + '-' + slist_[1]
            elif elements == 'dis-dev':
                dic_['dis'] = slist_[0]
                dic_['dev'] = slist_[1]
        elif len(slist_) == 3:
            dic_['dis'] = slist_[0]
            dic_['dev'] = slist_[1]
            dic_['idx'] = slist_[2]
    else:
        slist_ = list_[0].split('-')
        dic_['prefix'] = '-'.join([s for s in slist_[:-2]])
        dic_['area_name'] = '-'.join([s for s in slist_[-2:]])
        dic_['device_name'] = dic_['area_name'] + ':' + list_[1]

        dic_['sec'] = slist_[-2]
        dic_['sub'] = slist_[-1]

        slist_ = list_[1].split('-')
        dic_['dis'] = slist_[0]
        dic_['dev'] = slist_[1]
        dic_['idx'] = slist_[2] if len(slist_) >= 3 else ''

        if len(list_) > 2:
            slist_ = list_[2].split('.')
            sslist_ = slist_[0].split('-')
            dic_['propty'] = slist_[0]
            dic_['propty_name'] = sslist_[0]
            dic_['propty_suffix'] = sslist_[1] if len(sslist_) > 1 else ''
            dic_['field'] = slist_[1] if len(slist_) >= 2 else ''

        dic_['device_propty'] = (
            dic_['dev'] +
            ('-' + dic_['idx'] if dic_['idx'] else '') +
            (':' + dic_['propty'] if dic_['propty'] else '') +
            ('.' + dic_['field'] if dic_['field'] else ''))
    return dic_


def get_pair_sprb(pv_propty):
    """Return the equivalent [setpoint, readback] SiriusPVName property pair.

    Input: a SiriusPVName property, with a setpoint or a readback suffix.
    Output: the equivalent Sirius [setpoint, readback] pair.
    """
    _sp_rb = {'SP': 'RB', 'Sel': 'Sts'}
    for sp, rb in _sp_rb.items():
        if pv_propty.propty_suffix in sp:
            return [pv_propty, pv_propty.substitute(propty_suffix=rb)]
        elif pv_propty.propty_suffix in rb:
            return [pv_propty.substitute(propty_suffix=sp), pv_propty]
    else:
        raise TypeError('Input is not a setpoint/readback property!')


class SiriusPVName(str):
    """Sirius PV Name Class."""

    def __new__(cls, pv_name, elements='propty'):
        """Implement new method."""
        name = split_name(pv_name, elements)
        obj = super().__new__(cls, pv_name)
        obj.channel_type = name['channel_type']
        obj.prefix = name['prefix']
        obj.sec = name['sec']
        obj.sub = name['sub']
        obj.area_name = name['area_name']
        obj.dis = name['dis']
        obj.dev = name['dev']
        obj.idx = name['idx']
        obj.device_name = name['device_name']
        obj.propty_name = name['propty_name']
        obj.propty_suffix = name['propty_suffix']
        obj.propty = name['propty']
        obj.device_propty = name['device_propty']
        obj.field = name['field']
        return obj

    def substitute(self, **kwargs):
        """Return new SiriusPVName object with the atttributes changed."""
        dic_ = {}
        dic_['sec'] = self.sec
        dic_['sub'] = self.sub
        dic_['dis'] = self.dis
        dic_['dev'] = self.dev
        dic_['idx'] = self.idx
        dic_['propty'] = self.propty
        dic_['propty_name'] = self.propty_name
        dic_['propty_suffix'] = self.propty_suffix
        dic_['field'] = self.field
        dic_['prefix'] = self.prefix
        dic_['channel_type'] = self.channel_type
        dic_.update({k: v for k, v in kwargs.items() if isinstance(v, str)})
        return join_name(**dic_)

    def __lt__(self, other):
        """Less-than operator."""
        cond = ((type(other) == type(self)) and
                (self.sec == other.sec) and
                (self.sub != other.sub))
        return self._subsec_comp(other) if cond else super().__lt__(other)

    def __gt__(self, other):
        """Greater-than operator."""
        return other.__lt__(self)

    def __le__(self, other):
        """Less-or-equal operator."""
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        """Greater-or-equal operator."""
        return self.__gt__(other) or self.__eq__(other)

    def _subsec_comp(self, other):
        """Subsection comparison."""
        my_ssec = self.sub
        th_ssec = other.sub
        my_dev = self.dev
        th_dev = other.dev
        if my_ssec == 'Glob':
            return False
        elif th_ssec == 'Glob':
            return True
        elif my_ssec == 'Fam':
            return False
        elif th_ssec == 'Fam':
            return True
        elif my_ssec == '01M1':
            return False
        elif th_ssec == '01M1':
            return True
        elif my_ssec == '01U' and my_dev in {'CV', 'BPM'}:
            return False
        elif th_ssec == '01U' and th_dev in {'CV', 'BPM'}:
            return True
        elif my_ssec[:2] != th_ssec[:2]:
            return my_ssec[:2] < th_ssec[:2]
        elif len(my_ssec) == 2:
            return False
        elif len(th_ssec) == 2:
            return True
        if my_ssec[2] == th_ssec[2]:
            return my_ssec[3] < th_ssec[3]
        else:
            return not my_ssec[2] < th_ssec[2]


class Filter:

    # PVName regex filters
    patterns = _types.SimpleNamespace()
    patterns.FAM = 'Fam'
    patterns.TRIM = '\d{2}\w{0,2}'
    patterns.DIPOLE = 'B.*'
    patterns.QUADRUPOLE = '(?:QD|QF|Q[0-9]).*'
    patterns.QUADRUPOLE_SKEW = 'QS'
    patterns.QD = 'QD.*'
    patterns.QF = 'QF.*'
    patterns.SEXTUPOLE = 'S(?:D|F)*'
    patterns.SD = 'SD.*'
    patterns.SF = 'SF.*'
    patterns.CORRECTOR = '(?:C|FC).*'
    patterns.SLOW_CHV = 'C(?:H|V).*'
    patterns.SLOW_CH = 'CH.*'
    patterns.SLOW_CV = 'CV.*'
    patterns.FAST_CHV = 'FC.*'
    patterns.FAST_CH = 'FCH.*'
    patterns.FAST_CV = 'FCV.*'

    filters = _types.SimpleNamespace()
    filters.FAM = {'sub': patterns.FAM}
    filters.TRIM = {'sub': patterns.TRIM}
    filters.DIPOLE = {'dev': patterns.DIPOLE}
    filters.QUADRUPOLE = {'dev': patterns.QUADRUPOLE}
    filters.QUADRUPOLE_SKEW = {'dev': patterns.QUADRUPOLE_SKEW}
    filters.QD = {'dev': patterns.QD}
    filters.QF = {'dev': patterns.QF}
    filters.SEXTUPOLE = {'dev': patterns.SEXTUPOLE}
    filters.SD = {'dev': patterns.SD}
    filters.SF = {'dev': patterns.SF}
    filters.CORRECTOR = {'dev': patterns.CORRECTOR}
    filters.SLOW_CHV = {'dev': patterns.SLOW_CHV}
    filters.SLOW_CH = {'dev': patterns.SLOW_CH}
    filters.SLOW_CV = {'dev': patterns.SLOW_CV}
    filters.FAST_CHV = {'dev': patterns.FAST_CHV}
    filters.FAST_CH = {'dev': patterns.FAST_CH}
    filters.FAST_CV = {'dev': patterns.FAST_CV}

    def add_filter(filters=None, sec=None, sub=None,
                   dis=None, dev=None):
        if filters is None:
            filters = []
        f = {}
        if sec is not None:
            f['sec'] = sec
        if sub is not None:
            f['sub'] = sub
        if dis is not None:
            f['dis'] = dis
        if dev is not None:
            f['dev'] = dev
        if f:
            filters.append(f)
        return filters

    def process_filters(pvnames, filters=None, sorting=None):
        """Return a sorted and filtered list of given pv name lists.

        'filters' is either a dictionary of a list of dictionaries whose keys
        are pv sub parts and the values are the desired patterns
        """
        if filters is None:
            return pvnames
        if isinstance(filters, dict):
            filters = [filters]
        elif isinstance(pvnames, str):
            pvnames = [pvnames]

        # build filter regexp
        fs = []
        for f in filters:
            if 'sec' not in f or f['sec'] is None:
                f['sec'] = '[A-Z]{2,4}'
            if 'sub' not in f or f['sub'] is None:
                f['sub'] = '\w{2,16}'
            if 'dis' not in f or f['dis'] is None:
                f['dis'] = '[A-Z]{2,6}'
            if 'dev' not in f or f['dev'] is None:
                f['dev'] = '.+'
            pattern = (f['sec'] + '-' + f['sub'] + ':' +
                       f['dis'] + '-' + f['dev'])
            regexp = _re.compile(pattern)
            fs.append(regexp)

        # filter list
        filtered_list = list()
        for pvname in pvnames:
            for pattern in fs:
                if pattern.match(pvname):
                    filtered_list.append(pvname)
                    break

        if sorting is None:
            sorted_filtered_list = filtered_list
        elif sorting == 'length':
            raise NotImplementedError
        return sorted_filtered_list
