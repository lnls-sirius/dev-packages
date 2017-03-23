def join_name(section, discipline, device, subsection,
              instance=None, proper=None, field=None):

    name = section.upper() + '-' + subsection + ':' + discipline.upper() + '-' + device
    name += ('-' + instance) if instance else ""
    name += (':' + proper)   if proper   else ""
    name += ('.' + field)   if field   else ""
    return name

def split_name(name):
    name_dict = {}
    name_list = name.split(':')
    name_dict['Area_name'] = name_list[0]
    name_dict['Device_name'] = name_list[0] + ':' + name_list[1]

    name_sublist = name_list[0].split('-')
    name_dict['Section']    = name_sublist[0]
    name_dict['Subsection'] = name_sublist[1]

    name_sublist = name_list[1].split('-')
    name_dict['Discipline'] = name_sublist[0]
    name_dict['Device']     = name_sublist[1]
    name_dict['Instance']   = name_sublist[2] if len(name_sublist) >= 3 else ''

    if len(name_list) >= 3:
        name_sublist = name_list[2].split('.')
        name_dict['Property'] = name_sublist[0]
        name_dict['Field'] = name_sublist[1] if len(name_sublist) >= 2 else ''
    else:
        name_dict['Property'] = ''
        name_dict['Field'] = ''

    return name_dict

class SiriusPVName(str):

    def __new__(cls, pv_name):
        name = split_name(pv_name)
        obj = super().__new__(cls, pv_name)
        obj.area = name['Area_name']
        obj.device_slot = name['Device_name']
        obj.section = name['Section']
        obj.subsection = name['Subsection']
        obj.discipline = name['Discipline']
        obj.device = name['Device']
        obj.instance = name['Instance']
        obj.property = name['Property']
        obj.field = name['Field']
        return obj
