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
