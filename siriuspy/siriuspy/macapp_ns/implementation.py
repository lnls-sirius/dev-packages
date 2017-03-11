import json as _json
import urllib.request as _urllib_request
import siriuspy.envars as _envars


def get_slots_list(timeout=1):
    '''Return a list of slots'''

    def _get_attribute_value(text, attr):
        try:
            words = text.split(attr+'>')
            value = words[1].replace('</','')
        except IndexError:
            value = None
        return value

    url = _envars.server_url_ns + '/rest/deviceNames'
    response = _urllib_request.urlopen(url, timeout=1)
    str_response = response.readall().decode('utf-8')
    words = str_response.split('deviceNameElement')
    tmpslots = []
    for i in range(1,len(words),2):
        w = words[i][1:-2]
        tmpslots.append(w)

    slots_list = []
    for slot in tmpslots:
        d = {}
        attr = 'deviceType'; d[attr] = _get_attribute_value(slot, attr)
        attr = 'discipline'; d[attr] = _get_attribute_value(slot, attr)
        attr = 'name'; d[attr] = _get_attribute_value(slot, attr)
        attr = 'status'; d[attr] = _get_attribute_value(slot, attr)
        attr = 'subSection'; d[attr] = _get_attribute_value(slot, attr)
        attr = 'uuid'; d[attr] = _get_attribute_value(slot, attr)
        slots_list.append(d)
    return slots_list
