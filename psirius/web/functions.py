import time as _time
import datetime as _datetime
import urllib.request as _urllib_request
import numpy as _numpy

SERVER_URL = 'http://10.0.7.55'

def magnets_excitation_data_get_filenames_list():
    """Get list of filenames in magnet excitation data folder at web server."""

    url = SERVER_URL + '/magnets-excitation-data/'
    response = _urllib_request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    words = text.split('"[TXT]"></td><td><a href="./')
    exc_list = []
    for word in words[1:]:
        exc = word.split('.txt">')[1].split('</a></td>')[0]
        exc_list.append(exc)
    return exc_list

def magnets_excitation_data_read(filename):
    """Return a MagnetExcitationData object corresponding to data in passed filename."""

    url = SERVER_URL + '/magnets-excitation-data/' + filename
    response = _urllib_request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    return text
