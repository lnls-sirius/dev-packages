import json as _json
import urllib as _urllib
import siriuspy.envars as _envars


def get_slots_list(timeout=1):
    '''Return a list of dictionaries with slots defined in CCDB'''
    url = _envars.server_url_ccdb + '/rest/slots'
    response = _urllib.request.urlopen(url, timeout=timeout)
    str_response = response.readall().decode('utf-8')
    data = _json.loads(str_response);
    try:
        slot_list = data['installationSlots']
    except:
        slot_list = data['slot']
    return slot_list

def get_devtypes_dict(timeout=1):
    '''Return dictionary with list of device types defined in CCDB'''
    url = _envars.server_url_ccdb + '/rest/deviceTypes'
    response = _urllib.request.urlopen(url, timeout=timeout)
    str_response = response.readall().decode('utf-8')
    lines = str_response.split('<deviceType>')
    device_types = {}
    for line in lines[1:]:
        line = line.replace('</deviceTypes>','')
        line = line.replace('<name>','')
        line = line.replace('</description></deviceType>','')
        words = line.split('</name><description>')
        name = words[0]; description = words[1]
        device_types[name] = description
    return device_types

def build_pvs_dict(slots_list):
    '''Return a dictionary with all PVs'''
    pvs_dict = {}
    for slot in slots_list:
        for prop in slot['properties']:
            pv_name = slot['name'] + ':' + prop['name']
            pvdict = {'dataType':prop['dataType'], 'unit':prop['unit'], 'value':prop['value']}
            pvs_dict[pv_name] = pvdict
    return pvs_dict

def build_devtypes_dict(slots_list):
    '''Return a dictionary with device types defined in CCDB'''
    dev_type_dict = {}
    for slot in slots_list:
        dtype = slot['deviceType']
        props = slot['properties']
        dev_type_dict[dtype] = props
    return dev_type_dict
