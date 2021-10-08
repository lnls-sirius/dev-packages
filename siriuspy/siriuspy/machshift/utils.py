"""Machine shift utils."""

import sys as _sys
import re as _re
import copy as _copy
import time as _time
import logging as _log

import numpy as _np
from matplotlib import pyplot as _plt

from ..search import PSSearch as _PSSearch
from .. import util as _util
from .. import clientweb as _web
from ..clientarch import ClientArchiver as _CltArch, Time as _Time, \
    PVData as _PVData, PVDataSet as _PVDataSet
from .csdev import Const as _Cte


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
        new_datetimes = [_Time(ts) for ts in new_timestamp]
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
                timestamp = _Time(year, month, day, 0, 0).timestamp()
                databyshift.append((timestamp, 0))
                databyday.append((timestamp, 0))
                datainicurr.append((timestamp, 0.0))
            else:
                timestamp = _Time(year, month, day, 0, 0).timestamp()
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
                    timestamp = _Time(
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
            datetime = [_Time(ts) for ts in timestamp]
        elif datetime is not None:
            if not isinstance(datetime, (list, tuple, _np.ndarray)):
                datetime = [datetime, ]
                ret_uni = True
            timestamp = [dt.timestamp() for dt in datetime]
        elif year is not None:
            ret_uni = True
            datetime = [_Time(year, month, day, hour, minute), ]
            timestamp = [dt.timestamp() for dt in datetime]
        else:
            raise Exception(
                'Enter timestamp, datetime or datetime items data.')
        return timestamp, datetime, ret_uni

    @staticmethod
    def _handle_interval_data(begin, end):
        if isinstance(begin, float):
            begin = _Time(begin)
            end = _Time(end)
        elif isinstance(begin, dict):
            begin = _Time(**begin)
            end = _Time(**end)
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


class MacReport:
    """Machine reports.

    Based on archiver data and machine schedule data.

    Reports:

    - user_shift_progmd_interval
        Time interval programmed to be user shift.
    - user_shift_delivd_interval
        Time interval delivered as programmed user shift, considering
        right shift and current above initial current*THOLD_FACTOR_USERSSBEAM.
    - user_shift_extra_interval
        Extra user shift time interval.
    - user_shift_total_interval
        Total user shift time interval (delivered + extra).
    - user_shift_progmd_count
        Number of user shifts programmed.
    - user_shift_current_average
        Average current in the total user shift time interval.
    - user_shift_current_stddev
        Current standard deviation in the total user shift time interval.
    - user_shift_current_beg_average
        User shift current average at the beginning of the shift.
    - user_shift_current_beg_stddev
        User shift current st.dev. at the beginning of the shift.
    - user_shift_current_end_average
        User shift current average at the end of the shift.
    - user_shift_current_end_stddev
        User shift current st.dev. at the end of the shift.
    - failures_interval
        Total failure duration.
    - failures_count
        Count of failures occurred.
    - beam_dump_count
        Number of beam dumps occurred.
    - time_to_recover_average
        Average time interval took to recover from failures.
    - time_to_recover_stddev
        Time interval standard deviation took to recover from failures.
    - time_between_failures_average
        Average time interval between failure occurrences.
    - beam_reliability
        Ratio between delivered and programmed user shift time interval.
    - inj_shift_interval
        Time interval in injection shift
    - inj_shift_count
        Number of injections occurred
    - inj_shift_interval_average
        Average time interval in injection shift
        (inj_shift_interval/inj_shift_count)
    - inj_shift_interval_stddev
        Time interval standard deviation in injection shift

    - lsusage_total_interval
        Total interval of Light Source Usage.
    - lsusage_machinestudy_failures_interval
        Interval of Light Source Usage for Study in Failure.
    - lsusage_machinestudy_failures
        Percentage of Light Source Usage for Study in Failure.
    - lsusage_machinestudy_operational_interval
        Operational Interval of Light Source Usage for Study.
    - lsusage_machinestudy_operational
        Operational Percentage of Light Source Usage for Study.
    - lsusage_machinestudy_interval
        Interval of Light Source Usage for Study.
    - lsusage_machinestudy
        Percentage of Light Source Usage for Study.
    - lsusage_commissioning_failures_interval
        Interval of Light Source Usage for Commissioning in Failure.
    - lsusage_commissioning_failures
        Percentage of Light Source Usage for Commissioning in Failure.
    - lsusage_commissioning_operational_interval
        Operational Interval of Light Source Usage for Commissioning.
    - lsusage_commissioning_operational
        Operational Percentage of Light Source Usage for Commissioning.
    - lsusage_commissioning_interval
        Interval of Light Source Usage for Commissioning.
    - lsusage_commissioning
        Percentage of Light Source Usage for Commissioning.
    - lsusage_conditioning_failures_interval
        Interval of Light Source Usage for Conditioning in Failure.
    - lsusage_conditioning_failures
        Percentage of Light Source Usage for Conditioning in Failure.
    - lsusage_conditioning_operational_interval
        Operational Interval of Light Source Usage for Conditioning.
    - lsusage_conditioning_operational
        Operational Percentage of Light Source Usage for Conditioning.
    - lsusage_conditioning_interval
        Interval of Light Source Usage for Conditioning.
    - lsusage_conditioning
        Percentage of Light Source Usage for Conditioning.
    - lsusage_maintenance_failures_interval
        Interval of Light Source Usage for Maintenance in Failure.
    - lsusage_maintenance_failures
        Percentage of Light Source Usage for Maintenance in Failure.
    - lsusage_maintenance_operational_interval
        Operational Interval of Light Source Usage for Maintenance.
    - lsusage_maintenance_operational
        Operational Percentage of Light Source Usage for Maintenance.
    - lsusage_maintenance_interval
        Interval of Light Source Usage for Maintenance.
    - lsusage_maintenance
        Percentage of Light Source Usage for Maintenance.
    - lsusage_user_failures_interval
        Interval of Light Source Usage for Users in Failure.
    - lsusage_user_failures
        Percentage of Light Source Usage for Users in Failure.
    - lsusage_user_operational_interval
        Operational Interval of Light Source Usage for Users.
    - lsusage_user_operational
        Operational Percentage of Light Source Usage for Users.
    - lsusage_user_interval
        Interval of Light Source Usage for Users.
    - lsusage_user
        Percentage of Light Source Usage for Users.

    - current_machinestudy_singlebunch_average
        Current average for machine study single bunch shifts.
    - current_machinestudy_singlebunch_stddev
        Current standard deviation for machine study single bunch shifts.
    - current_machinestudy_singlebunch_interval
        Interval of machine study single bunch shifts.
    - current_machinestudy_multibunch_average
        Current average for machine study multi bunch shifts.
    - current_machinestudy_multibunch_stddev
        Current standard deviation for machine study multi bunch shifts.
    - current_machinestudy_multibunch_interval
        Interval of machine study multi bunch shifts.
    - current_machinestudy_total_average
        Current average for machine study shifts.
    - current_machinestudy_total_stddev
        Current standard deviation for machine study shifts.
    - current_machinestudy_total_interval
        Interval of machine study shifts.
    - current_commissioning_singlebunch_average
        Current average for single bunch commissioning shifts.
    - current_commissioning_singlebunch_stddev
        Current standard deviation for single bunch commissioning shifts.
    - current_commissioning_singlebunch_interval
        Interval of single bunch commissioning shifts.
    - current_commissioning_multibunch_average
        Current average for multi bunch commissioning shifts.
    - current_commissioning_multibunch_stddev
        Current standard deviation for multi bunch commissioning shifts.
    - current_commissioning_multibunch_interval
        Interval of multi bunch commissioning shifts.
    - current_commissioning_total_average
        Current average in commissioning shifts.
    - current_commissioning_total_stddev
        Current standard deviation in commissioning shifts.
    - current_commissioning_total_interval
        Interval of commissioning shifts.
    - current_conditioning_singlebunch_average
        Current average for single bunch conditioning shifts.
    - current_conditioning_singlebunch_stddev
        Current standard deviation for single bunch conditioning shifts.
    - current_conditioning_singlebunch_interval
        Interval of single bunch conditioning shifts.
    - current_conditioning_multibunch_average
        Current average for multi bunch conditioning shifts.
    - current_conditioning_multibunch_stddev
        Current standard deviation for multi bunch conditioning shifts.
    - current_conditioning_multibunch_interval
        Interval of multi bunch conditioning shifts.
    - current_conditioning_total_average
        Current average in conditioning shifts.
    - current_conditioning_total_stddev
        Current standard deviation in conditioning shifts.
    - current_conditioning_total_interval
        Interval of conditioning shifts.
    - current_user_singlebunch_average
        Current average for single bunch user shifts.
    - current_user_singlebunch_stddev
        Current standard deviation for single bunch user shifts.
    - current_user_singlebunch_interval
        Interval of single bunch user shifts.
    - current_user_multibunch_average
        Current average for multi bunch user shifts.
    - current_user_multibunch_stddev
        Current standard deviation for multi bunch user shifts.
    - current_user_multibunch_interval
        Interval of multi bunch user shifts.
    - current_user_total_average
        Current average in all user shifts.
    - current_user_total_stddev
        Current standard deviation in all user shifts.
    - current_user_total_interval
        Interval of all user shifts.
    - current_ebeam_singlebunch_average
        Current average for all single bunch shifts.
    - current_ebeam_singlebunch_stddev
        Current standard deviation for all single bunch shifts.
    - current_ebeam_singlebunch_interval
        Interval of all single bunch shifts.
    - current_ebeam_multibunch_average
        Current average for all multi bunch shifts.
    - current_ebeam_multibunch_stddev
        Current standard deviation for all multi bunch shifts.
    - current_ebeam_multibunch_interval
        Interval of all multi bunch shifts.
    - current_ebeam_total_average
        Average current considering the entire interval in which
        there was any current above a threshold (THOLD_STOREDBEAM)
    - current_ebeam_total_stddev
        Current standard deviation considering the entire interval in which
        there was any current above a threshold (THOLD_STOREDBEAM)
    - current_ebeam_total_interval
        Time interval in which there was stored beam, for any
        current value above a threshold (THOLD_STOREDBEAM)
    """

    THOLD_STOREDBEAM = 0.008  # [mA]
    THOLD_FACTOR_USERSSBEAM = 0.5  # 50%
    QUERY_AVG_TIME = 60  # [s]

    def __init__(self, connector=None, logger=None):
        """Initialize object."""
        # client archiver connector
        self._connector = connector or _CltArch()

        # auxiliary logger
        self.logger = logger

        # create pv connectors
        self._init_connectors()

        # query data
        self._time_start = None
        self._time_stop = None

        # user shift stats
        self._user_shift_progmd_interval = None
        self._user_shift_delivd_interval = None
        self._user_shift_extra_interval = None
        self._user_shift_total_interval = None
        self._user_shift_progmd_count = None
        self._user_shift_current_average = None
        self._user_shift_current_stddev = None
        self._user_shift_current_beg_average = None
        self._user_shift_current_beg_stddev = None
        self._user_shift_current_end_average = None
        self._user_shift_current_end_stddev = None
        self._failures_interval = None
        self._failures_count = None
        self._beam_dump_count = None
        self._time_to_recover_average = None
        self._time_to_recover_stddev = None
        self._time_between_failures_average = None
        self._beam_reliability = None
        self._inj_shift_interval = None
        self._inj_shift_count = None
        self._inj_shift_interval_average = None
        self._inj_shift_interval_stddev = None

        # light source usage stats
        self._lsusage_total_interval = None
        self._lsusage_machinestudy_failures_interval = None
        self._lsusage_machinestudy_failures = None
        self._lsusage_machinestudy_operational_interval = None
        self._lsusage_machinestudy_operational = None
        self._lsusage_machinestudy_interval = None
        self._lsusage_machinestudy = None
        self._lsusage_commissioning_failures_interval = None
        self._lsusage_commissioning_failures = None
        self._lsusage_commissioning_operational_interval = None
        self._lsusage_commissioning_operational = None
        self._lsusage_commissioning_interval = None
        self._lsusage_commissioning = None
        self._lsusage_conditioning_failures_interval = None
        self._lsusage_conditioning_failures = None
        self._lsusage_conditioning_operational_interval = None
        self._lsusage_conditioning_operational = None
        self._lsusage_conditioning_interval = None
        self._lsusage_conditioning = None
        self._lsusage_maintenance_failures_interval = None
        self._lsusage_maintenance_failures = None
        self._lsusage_maintenance_operational_interval = None
        self._lsusage_maintenance_operational = None
        self._lsusage_maintenance_interval = None
        self._lsusage_maintenance = None
        self._lsusage_user_failures_interval = None
        self._lsusage_user_failures = None
        self._lsusage_user_operational_interval = None
        self._lsusage_user_operational = None
        self._lsusage_user_interval = None
        self._lsusage_user = None

        # stored current stats
        self._current_machinestudy_singlebunch_average = None
        self._current_machinestudy_singlebunch_stddev = None
        self._current_machinestudy_singlebunch_interval = None
        self._current_machinestudy_multibunch_average = None
        self._current_machinestudy_multibunch_stddev = None
        self._current_machinestudy_multibunch_interval = None
        self._current_machinestudy_total_average = None
        self._current_machinestudy_total_stddev = None
        self._current_machinestudy_total_interval = None
        self._current_commissioning_singlebunch_average = None
        self._current_commissioning_singlebunch_stddev = None
        self._current_commissioning_singlebunch_interval = None
        self._current_commissioning_multibunch_average = None
        self._current_commissioning_multibunch_stddev = None
        self._current_commissioning_multibunch_interval = None
        self._current_commissioning_total_average = None
        self._current_commissioning_total_stddev = None
        self._current_commissioning_total_interval = None
        self._current_conditioning_singlebunch_average = None
        self._current_conditioning_singlebunch_stddev = None
        self._current_conditioning_singlebunch_interval = None
        self._current_conditioning_multibunch_average = None
        self._current_conditioning_multibunch_stddev = None
        self._current_conditioning_multibunch_interval = None
        self._current_conditioning_total_average = None
        self._current_conditioning_total_stddev = None
        self._current_conditioning_total_interval = None
        self._current_user_singlebunch_average = None
        self._current_user_singlebunch_stddev = None
        self._current_user_singlebunch_interval = None
        self._current_user_multibunch_average = None
        self._current_user_multibunch_stddev = None
        self._current_user_multibunch_interval = None
        self._current_user_total_average = None
        self._current_user_total_stddev = None
        self._current_user_total_interval = None
        self._current_ebeam_singlebunch_average = None
        self._current_ebeam_singlebunch_stddev = None
        self._current_ebeam_singlebunch_interval = None
        self._current_ebeam_multibunch_average = None
        self._current_ebeam_multibunch_stddev = None
        self._current_ebeam_multibunch_interval = None
        self._current_ebeam_total_average = None
        self._current_ebeam_total_stddev = None
        self._current_ebeam_total_interval = None

        # auxiliary data
        self._raw_data = None
        self._failures_users = None
        self._curr_times = None
        self._curr_values = None
        self._inj_shift_values = None
        self._user_shift_values = None
        self._user_shift_progmd_values = None
        self._user_shift_inicurr_values = None
        self._is_stored_total = None
        self._is_stored_users = None

    @property
    def connector(self):
        """Client archiver connector."""
        return self._connector

    @property
    def logger(self):
        """Logger."""
        return self._logger

    @logger.setter
    def logger(self, new_logger):
        self._logger = new_logger
        self._logger_message = ''
        if not new_logger:
            _log.basicConfig(format='%(asctime)s | %(message)s',
                             datefmt='%F %T', level=_log.INFO,
                             stream=_sys.stdout)

    @property
    def timestamp_start(self):
        """Query interval start timestamp."""
        if not self._time_start:
            return None
        return self._time_start.timestamp()

    @timestamp_start.setter
    def timestamp_start(self, new_timestamp):
        if not isinstance(new_timestamp, (float, int)):
            raise TypeError('expected argument of type float or int')
        self._time_start = _Time(timestamp=new_timestamp)

    @property
    def time_start(self):
        """Time start."""
        return self._time_start

    @time_start.setter
    def time_start(self, new_time):
        if not isinstance(new_time, _Time):
            raise TypeError('expected argument of type Time')
        self._time_start = new_time

    @property
    def timestamp_stop(self):
        """Query interval stop timestamp."""
        if not self._time_stop:
            return None
        return self._time_stop.timestamp()

    @timestamp_stop.setter
    def timestamp_stop(self, new_timestamp):
        if not isinstance(new_timestamp, (float, int)):
            raise TypeError('expected argument of type float or int')
        self._time_stop = _Time(timestamp=new_timestamp)

    @property
    def time_stop(self):
        """Time stop."""
        return self._time_stop

    @time_stop.setter
    def time_stop(self, new_time):
        if not isinstance(new_time, _Time):
            raise TypeError('expected argument of type Time')
        self._time_stop = new_time

    # beam for users stats

    @property
    def user_shift_progmd_interval(self):
        """User shift interval programmed, in hours."""
        return self._conv_sec_2_hour(self._user_shift_progmd_interval)

    @property
    def user_shift_delivd_interval(self):
        """User shift interval delivered, in hours."""
        return self._conv_sec_2_hour(self._user_shift_delivd_interval)

    @property
    def user_shift_extra_interval(self):
        """User shift interval extra, in hours."""
        return self._conv_sec_2_hour(self._user_shift_extra_interval)

    @property
    def user_shift_total_interval(self):
        """User shift interval total (delivered + extra), in hours."""
        return self._conv_sec_2_hour(self._user_shift_total_interval)

    @property
    def user_shift_current_average(self):
        """User shift current average."""
        return self._user_shift_current_average

    @property
    def user_shift_current_stddev(self):
        """User shift current standard deviation."""
        return self._user_shift_current_stddev

    @property
    def user_shift_current_beg_average(self):
        """User shift current average at the beginning of the shift."""
        return self._user_shift_current_beg_average

    @property
    def user_shift_current_beg_stddev(self):
        """User shift current st.dev. at the beginning of the shift."""
        return self._user_shift_current_beg_stddev

    @property
    def user_shift_current_end_average(self):
        """User shift current average at the end of the shift."""
        return self._user_shift_current_end_average

    @property
    def user_shift_current_end_stddev(self):
        """User shift current st.dev. at the end of the shift."""
        return self._user_shift_current_end_stddev

    @property
    def user_shift_progmd_count(self):
        """Number of user shift programmed."""
        return self._user_shift_progmd_count

    @property
    def failures_interval(self):
        """Failures interval, in hours."""
        return self._conv_sec_2_hour(self._failures_interval)

    @property
    def failures_count(self):
        """Number of failures."""
        return self._failures_count

    @property
    def beam_dump_count(self):
        """Number of beam dumps."""
        return self._beam_dump_count

    @property
    def time_to_recover_average(self):
        """Average time interval took to recover from failures, in hours."""
        return self._conv_sec_2_hour(self._time_to_recover_average)

    @property
    def time_to_recover_stddev(self):
        """Time interval std.dev. took to recover from failures, in hours."""
        return self._conv_sec_2_hour(self._time_to_recover_stddev)

    @property
    def time_between_failures_average(self):
        """Average time interval between failure occurrences, in hours."""
        return self._conv_sec_2_hour(self._time_between_failures_average)

    @property
    def beam_reliability(self):
        """Beam reliability.

        Ratio between delivered and programmed user shift time interval."""
        return self._beam_reliability

    @property
    def inj_shift_interval(self):
        """Injection shift interval, in hours."""
        return self._conv_sec_2_hour(self._inj_shift_interval)

    @property
    def inj_shift_count(self):
        """Number of injection shifts."""
        return self._inj_shift_count

    @property
    def inj_shift_interval_average(self):
        """Average time interval in injection shift, in hours."""
        return self._conv_sec_2_hour(self._inj_shift_interval_average)

    @property
    def inj_shift_interval_stddev(self):
        """Time interval standard deviation in injection shift, in hours."""
        return self._conv_sec_2_hour(self._inj_shift_interval_stddev)

    # light source usage stats

    @property
    def lsusage_total_interval(self):
        """Total interval of Light Source Usage."""
        return self._conv_sec_2_hour(self._lsusage_total_interval)

    @property
    def lsusage_machinestudy_failures_interval(self):
        """Interval of Light Source Usage for Study in Failure."""
        return self._conv_sec_2_hour(
            self._lsusage_machinestudy_failures_interval)

    @property
    def lsusage_machinestudy_failures(self):
        """Percentage of Light Source Usage for Study in Failure."""
        return self._lsusage_machinestudy_failures

    @property
    def lsusage_machinestudy_operational_interval(self):
        """Operational Interval of Light Source Usage for Study."""
        return self._conv_sec_2_hour(
            self._lsusage_machinestudy_operational_interval)

    @property
    def lsusage_machinestudy_operational(self):
        """Operational Percentage of Light Source Usage for Study."""
        return self._lsusage_machinestudy_operational

    @property
    def lsusage_machinestudy_interval(self):
        """Interval of Light Source Usage for Study."""
        return self._conv_sec_2_hour(self._lsusage_machinestudy_interval)

    @property
    def lsusage_machinestudy(self):
        """Percentage of Light Source Usage for Study."""
        return self._lsusage_machinestudy

    @property
    def lsusage_commissioning_failures_interval(self):
        """Interval of Light Source Usage for Commissioning in Failure."""
        return self._conv_sec_2_hour(
            self._lsusage_commissioning_failures_interval)

    @property
    def lsusage_commissioning_failures(self):
        """Percentage of Light Source Usage for Commissioning in Failure."""
        return self._lsusage_commissioning_failures

    @property
    def lsusage_commissioning_operational_interval(self):
        """Operational Interval of Light Source Usage for Commissioning."""
        return self._conv_sec_2_hour(
            self._lsusage_commissioning_operational_interval)

    @property
    def lsusage_commissioning_operational(self):
        """Operational Percentage of Light Source Usage for Commissioning."""
        return self._lsusage_commissioning_operational

    @property
    def lsusage_commissioning_interval(self):
        """Interval of Light Source Usage for Commissioning."""
        return self._conv_sec_2_hour(self._lsusage_commissioning_interval)

    @property
    def lsusage_commissioning(self):
        """Percentage of Light Source Usage for Commissioning."""
        return self._lsusage_commissioning

    @property
    def lsusage_conditioning_failures_interval(self):
        """Interval of Light Source Usage for Conditioning in Failure."""
        return self._conv_sec_2_hour(
            self._lsusage_conditioning_failures_interval)

    @property
    def lsusage_conditioning_failures(self):
        """Percentage of Light Source Usage for Conditioning in Failure."""
        return self._lsusage_conditioning_failures

    @property
    def lsusage_conditioning_operational_interval(self):
        """Operational Interval of Light Source Usage for Conditioning."""
        return self._conv_sec_2_hour(
            self._lsusage_conditioning_operational_interval)

    @property
    def lsusage_conditioning_operational(self):
        """Operational Percentage of Light Source Usage for Conditioning."""
        return self._lsusage_conditioning_operational

    @property
    def lsusage_conditioning_interval(self):
        """Interval of Light Source Usage for Conditioning."""
        return self._conv_sec_2_hour(self._lsusage_conditioning_interval)

    @property
    def lsusage_conditioning(self):
        """Percentage of Light Source Usage for Conditioning."""
        return self._lsusage_conditioning

    @property
    def lsusage_maintenance_failures_interval(self):
        """Interval of Light Source Usage for Maintenance in Failure."""
        return self._conv_sec_2_hour(
            self._lsusage_maintenance_failures_interval)

    @property
    def lsusage_maintenance_failures(self):
        """Percentage of Light Source Usage for Maintenance in Failure."""
        return self._lsusage_maintenance_failures

    @property
    def lsusage_maintenance_operational_interval(self):
        """Operational Interval of Light Source Usage for Maintenance."""
        return self._conv_sec_2_hour(
            self._lsusage_maintenance_operational_interval)

    @property
    def lsusage_maintenance_operational(self):
        """Operational Percentage of Light Source Usage for Maintenance."""
        return self._lsusage_maintenance_operational

    @property
    def lsusage_maintenance_interval(self):
        """Interval of Light Source Usage for Maintenance."""
        return self._conv_sec_2_hour(self._lsusage_maintenance_interval)

    @property
    def lsusage_maintenance(self):
        """Percentage of Light Source Usage for Maintenance."""
        return self._lsusage_maintenance

    @property
    def lsusage_user_failures_interval(self):
        """Interval of Light Source Usage for Users in Failure."""
        return self._conv_sec_2_hour(self._lsusage_user_failures_interval)

    @property
    def lsusage_user_failures(self):
        """Percentage of Light Source Usage for Users in Failure."""
        return self._lsusage_user_failures

    @property
    def lsusage_user_operational_interval(self):
        """Operational Interval of Light Source Usage for Users."""
        return self._conv_sec_2_hour(self._lsusage_user_operational_interval)

    @property
    def lsusage_user_operational(self):
        """Operational Percentage of Light Source Usage for Users."""
        return self._lsusage_user_operational

    @property
    def lsusage_user_interval(self):
        """Interval of Light Source Usage for Users."""
        return self._conv_sec_2_hour(self._lsusage_user_interval)

    @property
    def lsusage_user(self):
        """Percentage of Light Source Usage for Users."""
        return self._lsusage_user

    # stored current stats

    @property
    def current_machinestudy_singlebunch_average(self):
        """Current average for machine study single bunch shifts."""
        return self._current_machinestudy_singlebunch_average

    @property
    def current_machinestudy_singlebunch_stddev(self):
        """Current standard deviation for machine study single bunch shifts."""
        return self._current_machinestudy_singlebunch_stddev

    @property
    def current_machinestudy_singlebunch_interval(self):
        """Interval of machine study single bunch shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_machinestudy_singlebunch_interval)

    @property
    def current_machinestudy_multibunch_average(self):
        """Current average for machine study multi bunch shifts."""
        return self._current_machinestudy_multibunch_average

    @property
    def current_machinestudy_multibunch_stddev(self):
        """Current standard deviation for machine study multi bunch shifts."""
        return self._current_machinestudy_multibunch_stddev

    @property
    def current_machinestudy_multibunch_interval(self):
        """Interval of machine study multi bunch shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_machinestudy_multibunch_interval)

    @property
    def current_machinestudy_total_average(self):
        """Current average for machine study shifts."""
        return self._current_machinestudy_total_average

    @property
    def current_machinestudy_total_stddev(self):
        """Current standard deviation for machine study shifts."""
        return self._current_machinestudy_total_stddev

    @property
    def current_machinestudy_total_interval(self):
        """Interval of machine study shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(self._current_machinestudy_total_interval)

    @property
    def current_commissioning_singlebunch_average(self):
        """Current average for single bunch commissioning shifts."""
        return self._current_commissioning_singlebunch_average

    @property
    def current_commissioning_singlebunch_stddev(self):
        """Current standard deviation for single bunch commissioning shifts."""
        return self._current_commissioning_singlebunch_stddev

    @property
    def current_commissioning_singlebunch_interval(self):
        """Interval of single bunch commissioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_commissioning_singlebunch_interval)

    @property
    def current_commissioning_multibunch_average(self):
        """Current average for multi bunch commissioning shifts."""
        return self._current_commissioning_multibunch_average

    @property
    def current_commissioning_multibunch_stddev(self):
        """Current standard deviation for multi bunch commissioning shifts."""
        return self._current_commissioning_multibunch_stddev

    @property
    def current_commissioning_multibunch_interval(self):
        """Interval of multi bunch commissioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_commissioning_multibunch_interval)

    @property
    def current_commissioning_total_average(self):
        """Current average in commissioning shifts."""
        return self._current_commissioning_total_average

    @property
    def current_commissioning_total_stddev(self):
        """Current standard deviation in commissioning shifts."""
        return self._current_commissioning_total_stddev

    @property
    def current_commissioning_total_interval(self):
        """Interval of commissioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_commissioning_total_interval)

    @property
    def current_conditioning_singlebunch_average(self):
        """Current average for single bunch conditioning shifts."""
        return self._current_conditioning_singlebunch_average

    @property
    def current_conditioning_singlebunch_stddev(self):
        """Current standard deviation for single bunch conditioning shifts."""
        return self._current_conditioning_singlebunch_stddev

    @property
    def current_conditioning_singlebunch_interval(self):
        """Interval of single bunch conditioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_conditioning_singlebunch_interval)

    @property
    def current_conditioning_multibunch_average(self):
        """Current average for multi bunch conditioning shifts."""
        return self._current_conditioning_multibunch_average

    @property
    def current_conditioning_multibunch_stddev(self):
        """Current standard deviation for multi bunch conditioning shifts."""
        return self._current_conditioning_multibunch_stddev

    @property
    def current_conditioning_multibunch_interval(self):
        """Interval of multi bunch conditioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_conditioning_multibunch_interval)

    @property
    def current_conditioning_total_average(self):
        """Current average in conditioning shifts."""
        return self._current_conditioning_total_average

    @property
    def current_conditioning_total_stddev(self):
        """Current standard deviation in conditioning shifts."""
        return self._current_conditioning_total_stddev

    @property
    def current_conditioning_total_interval(self):
        """Interval of conditioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(self._current_conditioning_total_interval)

    @property
    def current_user_singlebunch_average(self):
        """Current average for single bunch user shifts."""
        return self._current_user_singlebunch_average

    @property
    def current_user_singlebunch_stddev(self):
        """Current standard deviation for single bunch user shifts."""
        return self._current_user_singlebunch_stddev

    @property
    def current_user_singlebunch_interval(self):
        """Interval of single bunch user shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(self._current_user_singlebunch_interval)

    @property
    def current_user_multibunch_average(self):
        """Current average for multi bunch user shifts."""
        return self._current_user_multibunch_average

    @property
    def current_user_multibunch_stddev(self):
        """Current standard deviation for multi bunch user shifts."""
        return self._current_user_multibunch_stddev

    @property
    def current_user_multibunch_interval(self):
        """Interval of multi bunch user shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_user_multibunch_interval)

    @property
    def current_user_total_average(self):
        """Current average in all user shifts."""
        return self._current_user_total_average

    @property
    def current_user_total_stddev(self):
        """Current standard deviation in all user shifts."""
        return self._current_user_total_stddev

    @property
    def current_user_total_interval(self):
        """Interval of user shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_user_total_interval)

    @property
    def current_ebeam_singlebunch_average(self):
        """Current average for all single bunch shifts."""
        return self._current_ebeam_singlebunch_average

    @property
    def current_ebeam_singlebunch_stddev(self):
        """Current standard deviation for all single bunch shifts."""
        return self._current_ebeam_singlebunch_stddev

    @property
    def current_ebeam_singlebunch_interval(self):
        """Interval of all single bunch shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_ebeam_singlebunch_interval)

    @property
    def current_ebeam_multibunch_average(self):
        """Current average for all multi bunch shifts."""
        return self._current_ebeam_multibunch_average

    @property
    def current_ebeam_multibunch_stddev(self):
        """Current standard deviation for all multi bunch shifts."""
        return self._current_ebeam_multibunch_stddev

    @property
    def current_ebeam_multibunch_interval(self):
        """Interval of all multi bunch shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_ebeam_multibunch_interval)

    @property
    def current_ebeam_total_average(self):
        """Current average for all stored beam interval."""
        return self._current_ebeam_total_average

    @property
    def current_ebeam_total_stddev(self):
        """Current standard deviation for all stored beam interval."""
        return self._current_ebeam_total_stddev

    @property
    def current_ebeam_total_interval(self):
        """Stored beam interval, in hours. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_ebeam_total_interval)

    @property
    def raw_data(self):
        """Shift data and failures details."""
        return self._raw_data

    def update(self):
        """Update."""
        for pvn in self._pvnames:
            self._pvdata[pvn].time_start = self._time_start
            self._pvdata[pvn].time_stop = self._time_stop
        for pvds in self._pvdataset.values():
            pvds.time_start = self._time_start
            pvds.time_stop = self._time_stop

        self._update_log('Collecting archiver data...')

        log_msg = 'Query for {0} in archiver took {1:.3f}s'

        # current
        _t0 = _time.time()
        self._pvdata[self._current_pv].update(MacReport.QUERY_AVG_TIME)
        self._update_log(log_msg.format(self._current_pv, _time.time()-_t0))

        # macshift and sirius interlock
        for pvn in self._pvnames:
            if pvn == self._current_pv:
                continue
            _t0 = _time.time()
            self._pvdata[pvn].update(parallel=False)
            self._update_log(log_msg.format(pvn, _time.time()-_t0))

        # ps
        for group, pvdataset in self._pvdataset.items():
            _t0 = _time.time()
            pvdataset.update(parallel=False)
            self._update_log(log_msg.format(
                'SI PS '+group.capitalize(), _time.time()-_t0))

        self._compute_stats()

    def plot_raw_data(self):
        """Plot raw data for period timestamp_start to timestamp_stop."""
        if not self._raw_data:
            print('No data to display. Call update() to get data.')
            return

        datetimes = _np.array([_Time(t) for t in self._raw_data['Timestamp']])

        fig, axs = _plt.subplots(11, 1, sharex=True)
        fig.set_size_inches(9, 9)
        fig.subplots_adjust(top=0.96, left=0.08, bottom=0.05, right=0.96)
        axs[0].set_title('Raw data', fontsize=12)

        axs[0].plot_date(
            datetimes, self._raw_data['Current'], '-',
            color='blue', label='Current')
        axs[0].legend(loc='upper left', fontsize=9)
        axs[0].grid()

        axs[1].plot_date(
            datetimes, self._raw_data['UserShiftInitCurr'], '-',
            color='blue', label='User Shifts - Initial Current')
        axs[1].legend(loc='upper left', fontsize=9)
        axs[1].grid()

        axs[2].plot_date(
            datetimes, self._raw_data['UserShiftProgmd'], '-',
            color='gold', label='User Shifts - Programmed')
        axs[2].legend(loc='upper left', fontsize=9)
        axs[2].grid()

        axs[3].plot_date(
            datetimes, self._raw_data['UserShiftTotal'], '-',
            color='gold', label='User Shifts - Total')
        axs[3].legend(loc='upper left', fontsize=9)
        axs[3].grid()

        axs[4].plot_date(
            datetimes, self._raw_data['Failures']['NoEBeam'], '-',
            color='red', label='Failures - NoEBeam')
        axs[4].legend(loc='upper left', fontsize=9)
        axs[4].grid()

        axs[5].plot_date(
            datetimes, self._raw_data['GammaShutter'], '-',
            color='red', label='Failures - Gamma Shutter Closed')
        axs[5].legend(loc='upper left', fontsize=9)
        axs[5].grid()

        axs[6].plot_date(
            datetimes, self._raw_data['Failures']['WrongShift'], '-',
            color='red', label='Failures - WrongShift')
        axs[6].legend(loc='upper left', fontsize=9)
        axs[6].grid()

        axs[7].plot_date(
            datetimes, self._raw_data['Failures']['SubsystemsNOk'], '-',
            color='red', label='Failures - PS, RF and MPS')
        axs[7].legend(loc='upper left', fontsize=9)
        axs[7].grid()

        axs[8].plot_date(
            datetimes, self._raw_data['Shift']['Injection'], '-',
            color='lightsalmon', label='Injection Shifts')
        axs[8].legend(loc='upper left', fontsize=9)
        axs[8].grid()

        shift2color = {
            'MachineStudy': ['MacStudy', 'skyblue'],
            'Commissioning': ['Commi', 'royalblue'],
            'Conditioning': ['Condit', 'orchid'],
            'Maintenance': ['Maint', 'green']}
        for shift, auxdata in shift2color.items():
            ydata = self._raw_data['Shift'][shift]

            axs[9].plot_date(
                datetimes, ydata, '-',
                color=auxdata[1], label=auxdata[0])
        axs[9].legend(loc='upper left', ncol=4, fontsize=9)
        axs[9].set_ylim(0.0, 2.0)
        axs[9].grid()

        egmodes2color = {
            'MultiBunch': 'orangered', 'SingleBunch': 'orange'}
        for egmode, color in egmodes2color.items():
            ydata = self._raw_data['EgunModes'][egmode]

            axs[10].plot_date(
                datetimes, ydata, '-',
                color=color, label=egmode)
        axs[10].legend(loc='upper left', ncol=2, fontsize=9)
        axs[10].set_ylim(0.0, 2.0)
        axs[10].grid()

        return fig

    def plot_progmd_vs_delivd_hours(self):
        """Plot programmed vs. delivered hours graph."""
        if not self._raw_data:
            print('No data to display. Call update() to get data.')
            return

        datetimes = [_Time(d) for d in self._raw_data['Timestamp']]

        dtimes = _np.diff(self._raw_data['Timestamp'])
        dtimes = _np.r_[dtimes, dtimes[-1]]
        dtimes = dtimes/60/60

        dtimes_users_progmd = dtimes*self._raw_data['UserShiftProgmd']
        cum_progmd = _np.cumsum(dtimes_users_progmd)
        dtimes_users_delivd = dtimes*self._raw_data['UserShiftImpltd']
        cum_deliv = _np.cumsum(dtimes_users_delivd)

        fig = _plt.figure()
        axs = _plt.gca()
        axs.plot_date(datetimes, cum_progmd, '-', label='Programmed')
        axs.plot_date(datetimes, cum_deliv, '-', label='Delivered')
        axs.grid()
        axs.set_ylabel('Integrated Hours')
        _plt.legend(loc=4)
        _plt.title('Integrated User Hours')
        return fig

    # ----- auxiliary methods -----

    def _init_connectors(self):
        self._current_pv = 'SI-Glob:AP-CurrInfo:Current-Mon'
        self._macshift_pv = 'AS-Glob:AP-MachShift:Mode-Sts'
        self._egtrigg_pv = 'LI-01:EG-TriggerPS:enablereal'
        self._egpulse_pv = 'LI-01:EG-PulsePS:singleselstatus'
        self._gammashutt_pv = 'AS-Glob:PP-GammaShutter:Status-Mon'
        self._siintlk_pv = 'RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon'
        self._pvnames = [
            self._current_pv, self._macshift_pv,
            self._egtrigg_pv, self._egpulse_pv,
            self._gammashutt_pv, self._siintlk_pv]

        self._pvdata = dict()
        self._pv2default = dict()
        for pvname in self._pvnames:
            self._pvdata[pvname] = _PVData(pvname, self._connector)
            self._pv2default[pvname] = 0.0 if pvname != self._macshift_pv\
                else _Cte.MachShift.Commissioning

        self._si_fams_psnames = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': 'Fam', 'dev': '(B|Q|S).*'})
        self._si_corr_psnames_01t10 = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '(0[1-9]|10).*', 'dev': '(CH|CV)'})
        self._si_corr_psnames_11t20 = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '(1[1-9]|20).*', 'dev': '(CH|CV)'})
        self._si_trim_psnames_01t10 = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '(0[1-9]|10).*', 'dev': 'Q(F|D|[1-4]).*'})
        self._si_trim_psnames_11t20 = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '(1[1-9]|20).*', 'dev': 'Q(F|D|[1-4]).*'})
        self._si_skew_psnames_01t10 = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '(0[1-9]|10).*', 'dev': 'QS'})
        self._si_skew_psnames_11t20 = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '(1[1-9]|20).*', 'dev': 'QS'})
        self._psgroup2psname = {
            'fams': self._si_fams_psnames,
            'corrs (1/2)': self._si_corr_psnames_01t10,
            'corrs (2/2)': self._si_corr_psnames_11t20,
            'trims (1/2)': self._si_trim_psnames_01t10,
            'trims (2/2)': self._si_trim_psnames_11t20,
            'skews (1/2)': self._si_skew_psnames_01t10,
            'skews (2/2)': self._si_skew_psnames_11t20}

        self._pvdataset = dict()
        for group, psnames in self._psgroup2psname.items():
            pvnames = [psn+':DiagStatus-Mon' for psn in psnames]
            self._pvdataset[group] = _PVDataSet(pvnames, self._connector)
            for pvn in pvnames:
                self._pvdata[pvn] = self._pvdataset[group][pvn]
                self._pv2default[pvn] = 0.0

    def _compute_stats(self):
        self._raw_data = dict()

        # current data
        self._curr_times, self._curr_values = \
            self._get_pv_data('SI-Glob:AP-CurrInfo:Current-Mon')
        self._curr_values[self._curr_values < 0] = 0
        self._curr_values[self._curr_values > 500] = 0
        self._raw_data['Timestamp'] = self._curr_times
        self._raw_data['Current'] = self._curr_values

        # ps status data
        psfail_all = [0] * len(self._curr_times)
        for psnames in self._psgroup2psname.values():
            for psn in psnames:
                psfail_times, psfail_values = \
                    self._get_pv_data(psn+':DiagStatus-Mon')
                psfail_values = _np.bitwise_and(  # disregard alarms
                    psfail_values.astype(int), 0b1101111)

                psfail = 1 * (_interp1d_previous(
                    psfail_times, psfail_values, self._curr_times) > 0)

                psfail_all = _np.logical_or(psfail_all, psfail)
        self._ps_fail_values = 1 * psfail_all

        gamblk_times, gamblk_values = \
            self._get_pv_data('AS-Glob:PP-GammaShutter:Status-Mon')
        self._gamblk_fail_values = _interp1d_previous(
            gamblk_times, gamblk_values, self._curr_times)
        self._raw_data['GammaShutter'] = self._gamblk_fail_values

        # rf and mps status data
        siintlk_times, siintlk_values = \
            self._get_pv_data('RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon')
        self._mps_fail_values = _interp1d_previous(
            siintlk_times, siintlk_values, self._curr_times)

        # delivered shift data
        ishift_times, ishift_values = \
            self._get_pv_data('AS-Glob:AP-MachShift:Mode-Sts')

        self._raw_data['Shift'] = dict()

        inj_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Injection) for v in ishift_values])
        self._inj_shift_values = _interp1d_previous(
            ishift_times, inj_shift_values, self._curr_times)
        self._raw_data['Shift']['Injection'] = self._inj_shift_values

        stdy_shift_values = _np.array(
            [1*(v == _Cte.MachShift.MachineStudy) for v in ishift_values])
        self._machinestudy_shift_values = _interp1d_previous(
            ishift_times, stdy_shift_values, self._curr_times)
        self._raw_data['Shift']['MachineStudy'] = \
            self._machinestudy_shift_values

        cmm_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Commissioning) for v in ishift_values])
        self._commissioning_shift_values = _interp1d_previous(
            ishift_times, cmm_shift_values, self._curr_times)
        self._raw_data['Shift']['Commissioning'] = \
            self._commissioning_shift_values

        cdt_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Conditioning) for v in ishift_values])
        self._conditioning_shift_values = _interp1d_previous(
            ishift_times, cdt_shift_values, self._curr_times)
        self._raw_data['Shift']['Conditioning'] = \
            self._conditioning_shift_values

        mtn_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Maintenance) for v in ishift_values])
        self._maintenance_shift_values = _interp1d_previous(
            ishift_times, mtn_shift_values, self._curr_times)
        self._raw_data['Shift']['Maintenance'] = self._maintenance_shift_values

        user_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Users) for v in ishift_values])
        self._user_shift_values = _interp1d_previous(
            ishift_times, user_shift_values, self._curr_times)

        # desired shift data
        _t0 = _time.time()
        self._user_shift_progmd_values = \
            MacScheduleData.is_user_shift_programmed(
                timestamp=self._curr_times)
        self._user_shift_inicurr_values = \
            MacScheduleData.get_initial_current_programmed(
                timestamp=self._curr_times)
        self._user_shift_progmd_count = \
            MacScheduleData.get_users_shift_count(
                self._curr_times[0], self._curr_times[-1])
        self._update_log(
            'Query for machine schedule data took {0:.3f}s'.format(
                _time.time()-_t0))
        self._raw_data['UserShiftProgmd'] = self._user_shift_progmd_values
        self._raw_data['UserShiftInitCurr'] = self._user_shift_inicurr_values

        # single/multi bunch mode data
        egtrig_times, _ = self._get_pv_data('LI-01:EG-TriggerPS:enablereal')
        egmode_times, egmode_values = \
            self._get_pv_data('LI-01:EG-PulsePS:singleselstatus')
        egmode_values = _interp1d_previous(
            egmode_times, egmode_values, egtrig_times)
        egmode_values = _interp1d_previous(
            egtrig_times, egmode_values, self._curr_times)
        self._singlebunch_values = egmode_values
        self._multibunch_values = _np.logical_not(egmode_values)
        self._raw_data['EgunModes'] = dict()
        self._raw_data['EgunModes']['SingleBunch'] = self._singlebunch_values
        self._raw_data['EgunModes']['MultiBunch'] = self._multibunch_values

        # is stored data
        self._is_stored_total = self._curr_values > MacReport.THOLD_STOREDBEAM
        self._is_stored_users = self._curr_values >= \
            self._user_shift_inicurr_values*MacReport.THOLD_FACTOR_USERSSBEAM

        # time vectors and failures
        dtimes = _np.diff(self._curr_times)
        dtimes = _np.r_[dtimes, dtimes[-1]]

        dtimes_users_progmd = dtimes*self._user_shift_progmd_values
        dtimes_injection = dtimes*self._inj_shift_values
        dtimes_machinestudy = dtimes*self._machinestudy_shift_values
        dtimes_commissioning = dtimes*self._commissioning_shift_values
        dtimes_conditioning = dtimes*self._conditioning_shift_values
        dtimes_maintenance = dtimes*self._maintenance_shift_values

        self._raw_data['Failures'] = dict()
        self._raw_data['Failures']['SubsystemsNOk'] = _np.logical_or(
            self._ps_fail_values, self._mps_fail_values)
        self._raw_data['Failures']['GammaShutter'] = \
            self._gamblk_fail_values.astype(int)
        self._raw_data['Failures']['NoEBeam'] = \
            _np.logical_not(self._is_stored_users)
        self._raw_data['Failures']['WrongShift'] = \
            1 * ((self._user_shift_progmd_values-self._user_shift_values) > 0)

        self._failures_users = 1 * _np.logical_or.reduce(
            [value for value in self._raw_data['Failures'].values()]) * \
            self._user_shift_progmd_values
        dtimes_failures_users = dtimes*self._failures_users
        self._user_shift_delivd_values = self._user_shift_progmd_values * \
            _np.logical_not(self._failures_users)
        self._raw_data['UserShiftImpltd'] = self._user_shift_delivd_values
        dtimes_users_delivd = dtimes*self._user_shift_delivd_values
        self._failures_users_operat = 1 * _np.logical_or.reduce(
            [self._raw_data['Failures']['SubsystemsNOk'],
             self._raw_data['Failures']['NoEBeam']]) * \
            self._user_shift_progmd_values
        dtimes_failures_users_oper = dtimes*self._failures_users_operat

        # user total and extra shift
        self._user_shift_act_values = \
            self._user_shift_values*_np.logical_not(self._failures_users)
        self._raw_data['UserShiftTotal'] = self._user_shift_act_values
        dtimes_users_total = dtimes*self._user_shift_act_values
        dtimes_users_extra = dtimes_users_total*_np.logical_not(
            self._user_shift_progmd_values)

        # calculate stats

        # # beam for users stats
        # # # ----- users shift -----
        self._user_shift_progmd_interval = _np.sum(dtimes_users_progmd)

        self._user_shift_delivd_interval = _np.sum(dtimes_users_delivd)

        self._user_shift_extra_interval = _np.sum(dtimes_users_extra)

        self._user_shift_total_interval = _np.sum(dtimes_users_total)

        self._user_shift_current_average, self._user_shift_current_stddev = \
            self._calc_current_stats(dtimes_users_total)

        transit = _np.diff(self._user_shift_delivd_values)
        beg_idcs = _np.where(transit == 1)[0]
        end_idcs = _np.where(transit == -1)[0]

        if beg_idcs.size:
            beg_val = [i for i in range(beg_idcs.size-1) if
                       beg_idcs[i+1]-beg_idcs[i] > 15]
            beg_val += [beg_idcs.size-1]
            beg1, beg2 = beg_idcs[beg_val], beg_idcs[beg_val] + 15
            if beg2[-1] > self._user_shift_delivd_values.size-1:
                beg1.pop()
                beg2.pop()
            beg_val = [i for i in range(beg1.size) if not
                       any([beg1[i] < e < beg2[i] for e in end_idcs])]
            beg1, beg2 = beg1[beg_val], beg2[beg_val]
            stats_vals = [_np.mean(self._curr_values[beg1[i]:beg2[i]])
                          for i in range(beg1.size)]
            self._user_shift_current_beg_average = _np.mean(stats_vals)
            self._user_shift_current_beg_stddev = _np.std(stats_vals)
        else:
            self._user_shift_current_beg_average = 0
            self._user_shift_current_beg_stddev = 0

        if end_idcs.size:
            end_val = [0] + [i for i in range(end_idcs.size)
                             if end_idcs[i]-end_idcs[i-1] > 15]
            end1, end2 = end_idcs[end_val] - 15, end_idcs[end_val]
            if end1[0] < 0:
                end1.pop(0)
                end2.pop(0)
            end_val = [i for i in range(end1.size-1) if not
                       any([end1[i] < b < end2[i] for b in beg_idcs])]
            end1, end2 = end1[end_val], end2[end_val]
            stats_vals = [_np.mean(self._curr_values[end1[i]:end2[i]])
                          for i in range(end1.size)]
            self._user_shift_current_end_average = _np.mean(stats_vals)
            self._user_shift_current_end_stddev = _np.std(stats_vals)
        else:
            self._user_shift_current_end_average = 0
            self._user_shift_current_end_stddev = 0

        # # # ----- failures -----
        self._failures_interval = _np.sum(dtimes_failures_users)

        beam_dump_values = _np.logical_not(
            self._raw_data['Failures']['WrongShift']) * \
            self._raw_data['Failures']['NoEBeam']
        self._beam_dump_count = _np.sum(_np.diff(beam_dump_values) > 0)

        ave, std, count = self._calc_interval_stats(
            self._failures_users, dtimes_failures_users)
        self._time_to_recover_average = ave
        self._time_to_recover_stddev = std
        self._failures_count = count

        self._time_between_failures_average = \
            _np.inf if not self._failures_count\
            else self._user_shift_progmd_interval/self._failures_count

        # # # ----- reliability -----
        self._beam_reliability = \
            0.0 if not self._user_shift_progmd_interval else 100 * \
            self._user_shift_delivd_interval/self._user_shift_progmd_interval

        # # # ----- injection shift -----
        self._inj_shift_interval = _np.sum(dtimes_injection)

        ave, std, count = self._calc_interval_stats(
            self._inj_shift_values, dtimes_injection)
        self._inj_shift_interval_average = ave
        self._inj_shift_interval_stddev = std
        self._inj_shift_count = count

        # # light source usage stats
        self._lsusage_machinestudy_interval = _np.sum(dtimes_machinestudy)

        self._lsusage_commissioning_interval = _np.sum(dtimes_commissioning)

        self._lsusage_conditioning_interval = _np.sum(dtimes_conditioning)

        self._lsusage_maintenance_interval = _np.sum(dtimes_maintenance)

        self._lsusage_user_interval = self._user_shift_progmd_interval + \
            self._user_shift_extra_interval

        self._lsusage_total_interval = \
            self._lsusage_machinestudy_interval + \
            self._lsusage_commissioning_interval + \
            self._lsusage_conditioning_interval + \
            self._lsusage_maintenance_interval + \
            self._lsusage_user_interval

        self._lsusage_machinestudy_failures_interval = _np.sum(
            dtimes_machinestudy*self._raw_data['Failures']['SubsystemsNOk'])

        self._lsusage_commissioning_failures_interval = _np.sum(
            dtimes_commissioning*self._raw_data['Failures']['SubsystemsNOk'])

        self._lsusage_conditioning_failures_interval = _np.sum(
            dtimes_conditioning*self._raw_data['Failures']['SubsystemsNOk'])

        self._lsusage_maintenance_failures_interval = 0.0

        self._lsusage_user_failures_interval = _np.sum(
            dtimes_failures_users_oper)

        for usage in ['machinestudy', 'commissioning', 'conditioning',
                      'maintenance', 'user']:
            fail_intvl = getattr(self, '_lsusage_'+usage+'_failures_interval')
            total_intvl = getattr(self, '_lsusage_'+usage+'_interval')
            oper_intvl = total_intvl - fail_intvl
            if total_intvl:
                setattr(self, '_lsusage_'+usage+'_operational_interval',
                        oper_intvl)
                setattr(self, '_lsusage_'+usage+'_failures',
                        100*fail_intvl/total_intvl)
                setattr(self, '_lsusage_'+usage+'_operational',
                        100*oper_intvl/total_intvl)
            else:
                setattr(self, '_lsusage_'+usage+'_operational_interval', 0.0)
                setattr(self, '_lsusage_'+usage+'_failures', 0.0)
                setattr(self, '_lsusage_'+usage+'_operational', 0.0)
            setattr(self, '_lsusage_'+usage,
                    100*total_intvl/self._lsusage_total_interval)

        # # stored current stats
        for shifttype in ['machinestudy', 'commissioning', 'conditioning',
                          'user', 'ebeam']:
            for fillmode in ['singlebunch', 'multibunch', 'total']:

                select = self._is_stored_total
                if fillmode != 'total':
                    fillmode_values = getattr(self, '_'+fillmode+'_values')
                    select = select*fillmode_values
                if shifttype != 'ebeam':
                    shift_values = getattr(self, '_'+shifttype+'_shift_values')
                    select = select*shift_values

                dtimes_select = dtimes*select

                pname = '_current_'+shifttype+'_'+fillmode

                setattr(self, pname+'_interval', _np.sum(dtimes_select))

                avg, sdv = self._calc_current_stats(dtimes_select)
                setattr(self, pname+'_average', avg)
                setattr(self, pname+'_stddev', sdv)

    def _get_pv_data(self, pvname):
        t_start = self._time_start.timestamp()
        data = self._pvdata[pvname]
        defv = self._pv2default[pvname]
        if data.timestamp is None:
            times = _np.array([t_start, ])
            values = _np.array([defv, ])
        else:
            times = _np.array(data.timestamp)
            values = _np.array(data.value)
            if times[0] > t_start + MacReport.QUERY_AVG_TIME:
                times = _np.r_[t_start, times]
                values = _np.r_[defv, values]
        return times, values

    def _calc_current_stats(self, dtimes):
        interval = _np.sum(dtimes)
        if not interval:
            average = 0.0
            stddev = 0.0
        else:
            average = _np.sum(self._curr_values*dtimes)/interval

            aux = (self._curr_values - average)
            stddev = _np.sqrt(_np.sum(aux*aux*dtimes)/interval)
        return average, stddev

    def _calc_interval_stats(self, values, dtimes):
        transit = _np.diff(values)
        beg_idcs = _np.where(transit == 1)[0]
        end_idcs = _np.where(transit == -1)[0]
        if beg_idcs.size and end_idcs.size:
            if beg_idcs[0] > end_idcs[0]:
                end_idcs = end_idcs[1:]
            if beg_idcs.size > end_idcs.size:
                end_idcs = _np.r_[end_idcs, values.size-1]
            stats_vals = [_np.sum(dtimes[beg_idcs[i]:end_idcs[i]])
                          for i in range(beg_idcs.size)]
            avg = _np.mean(stats_vals)
            std = _np.std(stats_vals)
            return avg, std, beg_idcs.size
        return 0, 0, 0

    def _conv_sec_2_hour(self, seconds):
        if seconds is None:
            return None
        return seconds/60/60

    def _update_log(self, message=''):
        self._logger_message = message
        if self._logger:
            self._logger.update(message)
        _log.info(message)

    # ----- magic methods -----

    def __getitem__(self, pvname):
        return self._pvdata[pvname]

    def __str__(self):
        ppties_userbeam = [
            ['user_shift_progmd_interval', 'h'],
            ['user_shift_delivd_interval', 'h'],
            ['user_shift_total_interval', 'h'],
            ['user_shift_extra_interval', 'h'],
            ['user_shift_progmd_count', ''],
            ['user_shift_current_average', 'mA'],
            ['user_shift_current_stddev', 'mA'],
            ['user_shift_current_beg_average', 'mA'],
            ['user_shift_current_beg_stddev', 'mA'],
            ['user_shift_current_end_average', 'mA'],
            ['user_shift_current_end_stddev', 'mA'],
            ['failures_interval', 'h'],
            ['failures_count', ''],
            ['beam_dump_count', ''],
            ['time_to_recover_average', 'h'],
            ['time_to_recover_stddev', 'h'],
            ['time_between_failures_average', 'h'],
            ['beam_reliability', '%'],
            ['inj_shift_interval', 'h'],
            ['inj_shift_count', ''],
            ['inj_shift_interval_average', 'h'],
            ['inj_shift_interval_stddev', 'h'],
        ]
        ppties_lsusage = [
            ['lsusage_total_interval', 'h'],
            ['lsusage_machinestudy_failures_interval', 'h'],
            ['lsusage_machinestudy_failures', '%'],
            ['lsusage_machinestudy_operational_interval', 'h'],
            ['lsusage_machinestudy_operational', '%'],
            ['lsusage_machinestudy_interval', 'h'],
            ['lsusage_machinestudy', '%'],
            ['lsusage_commissioning_failures_interval', 'h'],
            ['lsusage_commissioning_failures', '%'],
            ['lsusage_commissioning_operational_interval', 'h'],
            ['lsusage_commissioning_operational', '%'],
            ['lsusage_commissioning_interval', 'h'],
            ['lsusage_commissioning', '%'],
            ['lsusage_conditioning_failures_interval', 'h'],
            ['lsusage_conditioning_failures', '%'],
            ['lsusage_conditioning_operational_interval', 'h'],
            ['lsusage_conditioning_operational', '%'],
            ['lsusage_conditioning_interval', 'h'],
            ['lsusage_conditioning', '%'],
            ['lsusage_maintenance_failures_interval', 'h'],
            ['lsusage_maintenance_failures', '%'],
            ['lsusage_maintenance_operational_interval', 'h'],
            ['lsusage_maintenance_operational', '%'],
            ['lsusage_maintenance_interval', 'h'],
            ['lsusage_maintenance', '%'],
            ['lsusage_user_failures_interval', 'h'],
            ['lsusage_user_failures', '%'],
            ['lsusage_user_operational_interval', 'h'],
            ['lsusage_user_operational', '%'],
            ['lsusage_user_interval', 'h'],
            ['lsusage_user', '%'],
        ]
        ppties_storedcurrent = [
            ['current_machinestudy_singlebunch_average', 'mA'],
            ['current_machinestudy_singlebunch_stddev', 'mA'],
            ['current_machinestudy_singlebunch_interval', 'h'],
            ['current_machinestudy_multibunch_average', 'mA'],
            ['current_machinestudy_multibunch_stddev', 'mA'],
            ['current_machinestudy_multibunch_interval', 'h'],
            ['current_machinestudy_total_average', 'mA'],
            ['current_machinestudy_total_stddev', 'mA'],
            ['current_machinestudy_total_interval', 'h'],
            ['current_commissioning_singlebunch_average', 'mA'],
            ['current_commissioning_singlebunch_stddev', 'mA'],
            ['current_commissioning_singlebunch_interval', 'h'],
            ['current_commissioning_multibunch_average', 'mA'],
            ['current_commissioning_multibunch_stddev', 'mA'],
            ['current_commissioning_multibunch_interval', 'h'],
            ['current_commissioning_total_average', 'mA'],
            ['current_commissioning_total_stddev', 'mA'],
            ['current_commissioning_total_interval', 'h'],
            ['current_conditioning_singlebunch_average', 'mA'],
            ['current_conditioning_singlebunch_stddev', 'mA'],
            ['current_conditioning_singlebunch_interval', 'h'],
            ['current_conditioning_multibunch_average', 'mA'],
            ['current_conditioning_multibunch_stddev', 'mA'],
            ['current_conditioning_multibunch_interval', 'h'],
            ['current_conditioning_total_average', 'mA'],
            ['current_conditioning_total_stddev', 'mA'],
            ['current_conditioning_total_interval', 'h'],
            ['current_user_singlebunch_average', 'mA'],
            ['current_user_singlebunch_stddev', 'mA'],
            ['current_user_singlebunch_interval', 'h'],
            ['current_user_multibunch_average', 'mA'],
            ['current_user_multibunch_stddev', 'mA'],
            ['current_user_multibunch_interval', 'h'],
            ['current_user_total_average', 'mA'],
            ['current_user_total_stddev', 'mA'],
            ['current_user_total_interval', 'h'],
            ['current_ebeam_singlebunch_average', 'mA'],
            ['current_ebeam_singlebunch_stddev', 'mA'],
            ['current_ebeam_singlebunch_interval', 'h'],
            ['current_ebeam_multibunch_average', 'mA'],
            ['current_ebeam_multibunch_stddev', 'mA'],
            ['current_ebeam_multibunch_interval', 'h'],
            ['current_ebeam_total_average', 'mA'],
            ['current_ebeam_total_stddev', 'mA'],
            ['current_ebeam_total_interval', 'h'],
        ]
        rst = 'User Beam Statistics\n'
        for ppty, unit in ppties_userbeam:
            ppty_text = ppty + ('' if not unit else ' ('+unit+')')
            rst += '{0:>46s}: {1:>8.3f}\n'.format(
                ppty_text, getattr(self, ppty))
        rst += 'Light Source Usage Statistics\n'
        for ppty, unit in ppties_lsusage:
            ppty_text = ppty.split('lsusage_')[1] + \
                ('' if not unit else ' ('+unit+')')
            rst += '{0:>46s}: {1:>8.3f}\n'.format(
                ppty_text, getattr(self, ppty))
        rst += 'Stored Current Statistics\n'
        for ppty, unit in ppties_storedcurrent:
            ppty_text = ppty.split('current_')[1] + \
                ('' if not unit else ' ('+unit+')')
            rst += '{0:>46s}: {1:>8.3f}\n'.format(
                ppty_text, getattr(self, ppty))
        return rst


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
