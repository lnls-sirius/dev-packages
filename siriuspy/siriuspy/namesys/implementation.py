import types as _types
import re as _re


def join_name(section, discipline, device, subsection, instance=None,
              proper=None, field=None,  prefix=None, channel_type=None):
    name = channel_type + '://' if channel_type else ''
    name += prefix + '-' if prefix else ''
    name += (section.upper() + '-' + subsection + ':' +
             discipline.upper() + '-' + device)
    name += ('-' + instance) if instance else ""
    name += (':' + proper) if proper else ""
    name += ('.' + field) if field else ""
    return SiriusPVName(name)


def split_name(pvname):
    """Return dict with PV name split into fields."""
    dic_ = {}
    dic_['channel_type'] = ''
    if pvname.startswith('ca://'):
        dic_['channel_type'] = 'ca'
        pvname = pvname[5:]

    list_ = pvname.split(':')
    slist_ = list_[0].split('-')
    dic_['prefix'] = '-'.join([s for s in slist_[:-2]])
    dic_['area_name'] = '-'.join([s for s in slist_[-2:]])
    dic_['dev_name'] = dic_['area_name'] + ':' + list_[1]

    dic_['section'] = slist_[-2]
    dic_['subsection'] = slist_[-1]

    slist_ = list_[1].split('-')
    dic_['discipline'] = slist_[0]
    dic_['dev_type'] = slist_[1]
    dic_['dev_idx'] = slist_[2] if len(slist_) >= 3 else ''

    if len(list_) > 2:
        slist_ = list_[2].split('.')
        sslist_ = slist_[0].split('-')
        dic_['propty'] = slist_[0]
        dic_['propty_name'] = sslist_[0]
        dic_['propty_sufix'] = sslist_[1] if len(sslist_) > 1 else ''
        dic_['field'] = slist_[1] if len(slist_) >= 2 else ''
    else:
        dic_['propty'] = ''
        dic_['propty_name'] = ''
        dic_['propty_sufix'] = ''
        dic_['field'] = ''

    dic_['dev_propty'] = (dic_['dev_type'] +
                          ('-' + dic_['dev_idx'] if dic_['dev_idx'] else '') +
                          (':' + dic_['propty'] if dic_['propty'] else '') +
                          ('.' + dic_['field'] if dic_['field'] else ''))
    return dic_

class SiriusPVName(str):

    def __new__(cls, pv_name):
        name = split_name(pv_name)
        obj = super().__new__(cls, pv_name)
        obj.channel_type = name['channel_type']
        obj.prefix = name['prefix']
        obj.area_name = name['area_name']
        obj.dev_name = name['dev_name']
        obj.section = name['section']
        obj.subsection = name['subsection']
        obj.discipline = name['discipline']
        obj.dev_type = name['dev_type']
        obj.dev_instance = name['dev_idx']
        obj.propty = name['propty']
        obj.propty_name = name['propty_name']
        obj.propty_sufix = name['propty_sufix']
        obj.field = name['field']
        obj.dev_propty = name['dev_propty']
        return obj

    def __lt__(self, other):
        cond = ((type(other) == type(self)) and
                (self.section == other.section) and
                (self.subsection != other.subsection))
        return self._subsec_comp(other) if cond else super().__lt__(other)

    def __gt__(self, other):
        return other.__lt__(self)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def _subsec_comp(self, other):
        my_ssec = self.subsection
        th_ssec = other.subsection
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
    filters.FAM = {'sub_section': patterns.FAM}
    filters.TRIM = {'sub_section': patterns.TRIM}
    filters.DIPOLE = {'device': patterns.DIPOLE}
    filters.QUADRUPOLE = {'device': patterns.QUADRUPOLE}
    filters.QUADRUPOLE_SKEW = {'device': patterns.QUADRUPOLE_SKEW}
    filters.QD = {'device': patterns.QD}
    filters.QF = {'device': patterns.QF}
    filters.SEXTUPOLE = {'device': patterns.SEXTUPOLE}
    filters.SD = {'device': patterns.SD}
    filters.SF = {'device': patterns.SF}
    filters.CORRECTOR = {'device': patterns.CORRECTOR}
    filters.SLOW_CHV = {'device': patterns.SLOW_CHV}
    filters.SLOW_CH = {'device': patterns.SLOW_CH}
    filters.SLOW_CV = {'device': patterns.SLOW_CV}
    filters.FAST_CHV = {'device': patterns.FAST_CHV}
    filters.FAST_CH = {'device': patterns.FAST_CH}
    filters.FAST_CV = {'device': patterns.FAST_CV}

    def add_filter(filters=None, section=None, sub_section=None,
                   discipline=None, device=None):
        if filters is None:
            filters = []
        f = {}
        if section is not None:
            f['section'] = section
        if sub_section is not None:
            f['sub_section'] = sub_section
        if discipline is not None:
            f['discipline'] = discipline
        if device is not None:
            f['device'] = device
        if f:
            filters.append(f)
        return filters

    def process_filters(pvnames, filters=None, sorting=None):
        """ Return a sorted and filtered list of given pv name lists.

        'filters' is either a dictionary of a list of dictionaries whose keys
        are pv sub parts and the values are the desired patterns
        """
        if filters is None:
            return pvnames
        if isinstance(filters, dict):
            filters = [filters]
        if isinstance(pvnames, str):
            pvnames = [pvnames]

        # build filter regexp
        fs = []
        for f in filters:
            if 'section' not in f or f['section'] is None:
                f['section'] = '[A-Z]{2}'
            if 'sub_section' not in f or f['sub_section'] is None:
                f['sub_section'] = '\w{2,4}'
            if 'discipline' not in f or f['discipline'] is None:
                f['discipline'] = '[A-Z]{2,6}'
            if 'device' not in f or f['device'] is None:
                f['device'] = '.+'
            pattern = (f['section'] + '-' + f['sub_section'] + ':' +
                       f['discipline'] + '-' + f['device'])
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
