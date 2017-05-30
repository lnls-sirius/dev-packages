def join_name(section, discipline, device, subsection,
              instance=None, proper=None, field=None):

    name = section.upper() + '-' + subsection + ':' + discipline.upper() + '-' + device
    name += ('-' + instance) if instance else ""
    name += (':' + proper)   if proper   else ""
    name += ('.' + field)   if field   else ""
    return name

def split_name(pvname):
    name_dict = {}
    name_list = pvname.split(':')
    name_dict['area_name'] = name_list[0]
    name_dict['dev_name'] = name_list[0] + ':' + name_list[1]

    name_sublist = name_list[0].split('-')
    name_dict['section']    = name_sublist[0]
    name_dict['subsection'] = name_sublist[1]

    name_sublist = name_list[1].split('-')
    name_dict['discipline']      = name_sublist[0]
    name_dict['dev_type']     = name_sublist[1]
    name_dict['dev_idx'] = name_sublist[2] if len(name_sublist) >= 3 else ''

    if len(name_list) >= 3:
        name_sublist = name_list[2].split('.')
        name_dict['propty'] = name_sublist[0]
        name_dict['field'] = name_sublist[1] if len(name_sublist) >= 2 else ''
    else:
        name_dict['propty'] = ''
        name_dict['field'] = ''

    name_dict['dev_propty'] = (name_dict['dev_type'] +
                               ('-' + name_dict['dev_idx'] if name_dict['dev_idx'] else '') +
                               (':' + name_dict['propty']   if name_dict['propty']   else '') +
                               ('.' + name_dict['field']    if name_dict['field']    else ''))

    return name_dict

class SiriusPVName(str):

    def __new__(cls, pv_name):
        name = split_name(pv_name)
        obj = super().__new__(cls, pv_name)
        obj.area_name = name['area_name']
        obj.dev_name = name['dev_name']
        obj.section = name['section']
        obj.subsection = name['subsection']
        obj.discipline = name['discipline']
        obj.dev_type = name['dev_type']
        obj.dev_instance = name['dev_idx']
        obj.propty = name['propty']
        obj.field = name['field']
        obj.dev_propty = name['dev_propty']
        return obj

    def __lt__(self,other):
        if ( (type(other) == type(self)) and
             (self.section == other.section) and
             (self.subsection != other.subsection)  ):
            return self._subsection_comparison(other)
        else:
            return super().__lt__(other)

    def __gt__(self,other):
        return other.__lt__(self)

    def __le__(self,other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self,other):
        return self.__gt__(other) or self.__eq__(other)

    def _subsection_comparison(self,other):
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
