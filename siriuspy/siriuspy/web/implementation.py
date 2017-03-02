import urllib.request as _urllib_request
import siriuspy.envars as _envars


_excdat_folder = '/magnets/excitation-data/'


def magnets_excitation_data_get_filenames_list(timeout=1):
    """Get list of filenames in magnet excitation data folder at web server."""

    url = _envars.server_url_web + _excdat_folder
    response = _urllib_request.urlopen(url, timeout=timeout)
    data = response.read()
    text = data.decode('utf-8')
    words = text.split('"[TXT]"></td><td><a href="./')
    fname_list = []
    for word in words[1:]:
        fname = word.split('.txt">')[1].split('</a></td>')[0]
        fname_list.append(fname)
    return fname_list


def magnets_excitation_data_read(filename, timeout=1):
    """Return the text of the corresponding retrived from the web server."""

    url = _envars.server_url_web + _excdat_folder + filename
    response = _urllib_request.urlopen(url, timeout=timeout)
    data = response.read()
    text = data.decode('utf-8')
    return text
