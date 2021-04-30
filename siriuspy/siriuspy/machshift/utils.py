"""Machine shift utils."""

import re as _re
import copy as _copy
from datetime import datetime as _datetime

import numpy as _np
from matplotlib import pyplot as _plt

from .. import util as _util
from .. import clientweb as _web


class MacScheduleData:
    """Machine schedule data."""

    _TAG_FORMAT_BEG = r'(\d+)h(\d+)-(\w)-(\d+\.\d)'
    _TAG_FORMAT_END = r'(\d+)h(\d+)-(\w)'

    _mac_schedule_sdata = dict()
    _mac_schedule_ndata_byshift = dict()
    _mac_schedule_ndata_byday = dict()
    _mac_schedule_ndata_inicurr = dict()

    @staticmethod
    def get_mac_schedule_data(year, formating='plain'):
        """Get machine schedule data for year."""
        MacScheduleData._reload_mac_schedule_data(year)
        if formating == 'plain':
            data = MacScheduleData._mac_schedule_sdata[year]
            mac_schedule = _copy.deepcopy(data)
        elif formating == 'numeric_byshift':
            data = MacScheduleData._mac_schedule_ndata_byshift[year]
            mac_schedule = list(zip(*data))
        elif formating == 'numeric_byday':
            data = MacScheduleData._mac_schedule_ndata_byday[year]
            mac_schedule = list(zip(*data))
        else:
            raise NotImplementedError(
                "machine schedule for formating '{}' "
                "is not defined".format(formating))
        return mac_schedule

    @staticmethod
    def get_users_shift_count(begin, end):
        """Get users shift count for a period."""
        begin, end = MacScheduleData._handle_interval_data(begin, end)
        _, tags = MacScheduleData._get_numeric_data_for_interval(
            begin, end, dtype='macsched_byshift')
        return _np.sum(tags) if begin != end else 0

    @staticmethod
    def get_users_shift_day_count(begin, end):
        """Get users shift day count for a period."""
        begin, end = MacScheduleData._handle_interval_data(begin, end)
        _, tags = MacScheduleData._get_numeric_data_for_interval(
            begin, end, dtype='macsched_byday')
        return _np.sum(tags) if begin != end else 0

    @staticmethod
    def is_user_shift_programmed(
            timestamp=None, datetime=None,
            year=None, month=None, day=None, hour=0, minute=0):
        """Return whether a day is a predefined user shift."""
        timestamp, datetime, ret_uni = MacScheduleData._handle_timestamp_data(
            timestamp, datetime, year, month, day, hour, minute)
        times, tags = MacScheduleData._get_numeric_data_for_interval(
            datetime[0], datetime[-1], dtype='macsched_byshift')
        val = _interp1d_previous(times, tags, timestamp)
        return bool(val) if ret_uni else val

    @staticmethod
    def get_initial_current_programmed(
            timestamp=None, datetime=None,
            year=None, month=None, day=None, hour=0, minute=0):
        """Return initial current for shift."""
        timestamp, datetime, ret_uni = MacScheduleData._handle_timestamp_data(
            timestamp, datetime, year, month, day, hour, minute)
        times, currs = MacScheduleData._get_numeric_data_for_interval(
            datetime[0], datetime[-1], dtype='initial_current')
        val = _interp1d_previous(times, currs, timestamp)
        return val[0] if ret_uni else val

    @staticmethod
    def plot_mac_schedule(year):
        """Get machine schedule data for year."""
        MacScheduleData._reload_mac_schedule_data(year)
        times, tags = MacScheduleData.get_mac_schedule_data(
            year, formating='numeric_byshift')
        days_of_year = len(MacScheduleData._mac_schedule_sdata[year])
        new_timestamp = _np.linspace(times[0], times[-1], days_of_year*24*60)
        new_datetimes = [_datetime.fromtimestamp(ts) for ts in new_timestamp]
        new_tags = _interp1d_previous(times, tags, new_timestamp)

        fig = _plt.figure()
        _plt.plot_date(new_datetimes, new_tags, '-')
        _plt.title('Machine Schedule - ' + str(year))
        return fig

    # --- private methods ---

    @staticmethod
    def _reload_mac_schedule_data(year):
        if year in MacScheduleData._mac_schedule_sdata:
            return
        if not _web.server_online():
            raise Exception('could not connect to web server')

        try:
            data, _ = _util.read_text_data(_web.mac_schedule_read(year))
        except Exception:
            print('No data provided for year ' + str(year) + '. '
                  'Getting template data.')
            data, _ = _util.read_text_data(_web.mac_schedule_read('template'))

        databyshift = list()
        databyday = list()
        datainicurr = list()
        for datum in data:
            if len(datum) < 2:
                raise Exception(
                    'there is a date ({0}) with problem in {1} '
                    'machine schedule'.format(datum, year))

            month, day = int(datum[0]), int(datum[1])
            if len(datum) == 2:
                timestamp = _datetime(year, month, day, 0, 0).timestamp()
                databyshift.append((timestamp, 0))
                databyday.append((timestamp, 0))
                datainicurr.append((timestamp, 0.0))
            else:
                timestamp = _datetime(year, month, day, 0, 0).timestamp()
                databyday.append((timestamp, 1))
                for tag in datum[2:]:
                    if 'B' in tag:
                        hour, minute, flag, inicurr = _re.findall(
                            MacScheduleData._TAG_FORMAT_BEG, tag)[0]
                        inicurr = float(inicurr)
                    else:
                        hour, minute, flag = _re.findall(
                            MacScheduleData._TAG_FORMAT_END, tag)[0]
                        inicurr = 0.0
                    flag_bit = 0 if flag == 'E' else 1
                    hour, minute = int(hour), int(minute)
                    timestamp = _datetime(
                        year, month, day, hour, minute).timestamp()
                    databyshift.append((timestamp, flag_bit))
                    datainicurr.append((timestamp, inicurr))

        MacScheduleData._mac_schedule_sdata[year] = data
        MacScheduleData._mac_schedule_ndata_byshift[year] = databyshift
        MacScheduleData._mac_schedule_ndata_byday[year] = databyday
        MacScheduleData._mac_schedule_ndata_inicurr[year] = datainicurr

    @staticmethod
    def _handle_timestamp_data(
            timestamp=None, datetime=None, year=None,
            month=None, day=None, hour=0, minute=0):
        ret_uni = False
        if timestamp is not None:
            if not isinstance(timestamp, (list, tuple, _np.ndarray)):
                timestamp = [timestamp, ]
                ret_uni = True
            datetime = [_datetime.fromtimestamp(ts) for ts in timestamp]
        elif datetime is not None:
            if not isinstance(datetime, (list, tuple, _np.ndarray)):
                datetime = [datetime, ]
                ret_uni = True
            timestamp = [dt.timestamp() for dt in datetime]
        elif year is not None:
            ret_uni = True
            datetime = [_datetime(year, month, day, hour, minute), ]
            timestamp = [dt.timestamp() for dt in datetime]
        else:
            raise Exception(
                'Enter timestamp, datetime or datetime items data.')
        return timestamp, datetime, ret_uni

    @staticmethod
    def _handle_interval_data(begin, end):
        if isinstance(begin, float):
            begin = _datetime.fromtimestamp(begin)
            end = _datetime.fromtimestamp(end)
        elif isinstance(begin, dict):
            begin = _datetime(**begin)
            end = _datetime(**end)
        return begin, end

    @staticmethod
    def _get_numeric_data_for_interval(begin, end, dtype='macsched_byshift'):
        times, tags = list(), list()
        for y2l in _np.arange(begin.year, end.year+1):
            MacScheduleData._reload_mac_schedule_data(y2l)
            if dtype == 'macsched_byshift':
                data = MacScheduleData._mac_schedule_ndata_byshift[y2l]
            elif dtype == 'macsched_byday':
                data = MacScheduleData._mac_schedule_ndata_byday[y2l]
            elif dtype == 'initial_current':
                data = MacScheduleData._mac_schedule_ndata_inicurr[y2l]
            ytim, ytag = list(zip(*data))
            times.extend(ytim)
            tags.extend(ytag)
        times, tags = _np.array(times), _np.array(tags)
        if begin != end:
            idcs = _np.where(_np.logical_and(
                times >= begin.timestamp(), times <= end.timestamp()))[0]
            if not idcs.size:
                idcs = _np.searchsorted(times, [begin.timestamp(), ])
                idcs = idcs-1 if idcs[0] != 0 else idcs
            elif idcs[0] != 0:
                idcs = _np.r_[idcs[0]-1, idcs]
            return times[idcs], tags[idcs]
        return times, tags


# This solution is a simplified version of scipy.interpolate.interp1d for
# interpolation of kind 'previous' with fill_value='extrapolate' option
def _interp1d_previous(x_org, y_org, x_new):
    """interp1d to previous."""
    x_new = _np.asarray(x_new)
    x_org = _np.asarray(x_org).ravel()
    y_org = _np.asarray(y_org)

    # Get index of left value
    x_new_indices = _np.searchsorted(
        _np.nextafter(x_org, -_np.inf), x_new, side='left')

    # Clip x_new_indices so that they are within the range of x_org indices.
    x_new_indices = x_new_indices.clip(1, len(x_org)).astype(_np.intp)

    # Calculate the actual value for each entry in x_new.
    y_new = y_org[x_new_indices-1]

    return y_new


# Version using scipy.interpolate.interp1d
# from scipy.interpolate import interp1d as _interp1d
# def _interp1d_previous(x_org, y_org, x_new):
#     """interp1d to previous."""
#     fun = _interp1d(x_org, y_org, 'previous', fill_value='extrapolate')
#     y_new = fun(x_new)
#     return y_new
