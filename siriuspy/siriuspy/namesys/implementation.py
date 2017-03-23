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

class SiriusPVName:

    def __init__(self, pv_name):

        name = split_name(pv_name)
        self.area = name['Area_name']
        self.device_slot = name['Device_name']
        self.section = name['Section']
        self.subsection = name['Subsection']
        self.discipline = name['Discipline']
        self.device = name['Device']
        self.instance = name['Instance']
        self.propty = name['Property']
        self.field = name['Field']

    @property
    def device_property(self):
        device = self.device + '-' + self.instance if self.instance else self.device
        return device + ':' + self.propty

    @property
    def pv_name(self):
        return join_name(self.section,
                  self.discipline,
                  self.device,
                  self.subsection,
                  self.instance,
                  self.propty,
                  self.field)
