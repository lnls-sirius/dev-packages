"""Machine Report module."""

import sys as _sys
import time as _time
import logging as _log

import numpy as _np
from matplotlib import pyplot as _plt

from ..search import PSSearch as _PSSearch
from ..clientarch import ClientArchiver as _CltArch, Time as _Time, \
    PVData as _PVData, PVDataSet as _PVDataSet
from ..sofb.csdev import ConstTLines as _SOFBCte
from .csdev import Const as _Cte
from .macschedule import MacScheduleData as _MacScheduleData
from .utils import interp1d_previous as _interp1d_previous


class MacReport:
    """Machine reports.

    Based on archiver data and machine schedule data.

    Reports:

    - usershift_progmd_time
        Programmed time[h].
    - usershift_delivd_time
        Delivered time[h], considering current above initial
        current*THOLD_FACTOR_USERSSBEAM.
    - usershift_extra_time
        Extra time[h].
    - usershift_total_time
        Total time(delivered + extra)[h].
    - usershift_progmd_count
        Number of shifts programmed.
    - usershift_current_average
        Current average.
    - usershift_current_stddev
        Current standard deviation.
    - usershift_current_beg_average
        Current average at the beginning of the shift.
    - usershift_current_beg_stddev
        Current st.dev. at the beginning of the shift.
    - usershift_current_end_average
        Current average at the end of the shift.
    - usershift_current_end_stddev
        Current st.dev. at the end of the shift.
    - usershift_total_failures_time
        Total failures time[h].
    - usershift_failures_count
        Number of failures.
    - usershift_beam_dump_count
        Number of beam dumps.
    - usershift_time_to_recover_average
        Average time took to recover from failures[h].
    - usershift_time_to_recover_stddev
        Time std.dev. took to recover from failures[h].
    - usershift_time_between_failures_average
        Average time between failure occurrences[h].
    - usershift_beam_reliability
        Beam reliability. Ratio between delivered and programmed time.
    - usershift_total_stable_beam_time
        Total stable beam time[h].
    - usershift_total_unstable_beam_time
        Total unstable beam time[h].
    - usershift_unstable_beam_count
        Number of unstable beam occurrences.
    - usershift_time_between_unstable_beams_average
        Average time between unstable beam occurrences[h].
    - usershift_relative_stable_beam_time
        Ratio between stable + delivered and programmed time.
    - usershift_total_injection_time
        Total injection shift[h].
    - usershift_injection_count
        Number of injections.
    - usershift_injection_time_average
        Average time used for injection[h].
        (usershift_injection_time/usershift_injection_count)
    - usershift_injection_time_stddev
        Standard deviation of time used for injection[h].

    - lsusage_total_time
        Total time of Light Source Usage.
    - lsusage_machinestudy_failures_time
        Failures time in Machine Study Shift.
    - lsusage_machinestudy_failures
        Relative failures time in Machine Study Shift.
    - lsusage_machinestudy_operational_time
        Operational time in Machine Study Shift.
    - lsusage_machinestudy_operational
        Relative operational time in Machine Study Shift.
    - lsusage_machinestudy_time
        Time in Machine Study Shift.
    - lsusage_machinestudy
        Relative time in Machine Study Shift.
    - lsusage_commissioning_failures_time
        Failures time in Commissioning Shift.
    - lsusage_commissioning_failures
        Relative failures time in Commissioning Shift.
    - lsusage_commissioning_operational_time
        Operational time in Commissioning Shift.
    - lsusage_commissioning_operational
        Relative operational time in Commissioning Shift.
    - lsusage_commissioning_time
        Time in Commissioning Shift.
    - lsusage_commissioning
        Relative time in Commissioning Shift.
    - lsusage_conditioning_failures_time
        Failures time in Conditioning Shift.
    - lsusage_conditioning_failures
        Relative failures time in Conditioning Shift.
    - lsusage_conditioning_operational_time
        Operational time in Conditioning Shift.
    - lsusage_conditioning_operational
        Relative operational time in Conditioning Shift.
    - lsusage_conditioning_time
        Time in Conditioning Shift.
    - lsusage_conditioning
        Relative time in Conditioning Shift.
    - lsusage_maintenance_failures_time
        Failures time in Maintenance Shift.
    - lsusage_maintenance_failures
        Relative failures time in Maintenance Shift.
    - lsusage_maintenance_operational_time
        Operational time in Maintenance Shift.
    - lsusage_maintenance_operational
        Relative operational time in Maintenance Shift.
    - lsusage_maintenance_time
        Time in Maintenance Shift.
    - lsusage_maintenance
        Relative time in Maintenance Shift.
    - lsusage_user_failures_time
        Failures time in Users Shift.
    - lsusage_user_failures
        Relative failures time in Users Shift.
    - lsusage_user_operational_time
        Operational time in Users Shift.
    - lsusage_user_operational
        Relative operational time in Users Shift.
    - lsusage_user_time
        Time in Users Shift.
    - lsusage_user
        Relative time in Users Shift.

    - current_machinestudy_singlebunch_average
        Current average for machine study single bunch shifts.
    - current_machinestudy_singlebunch_stddev
        Current standard deviation for machine study single bunch shifts.
    - current_machinestudy_singlebunch_time
        Time of machine study single bunch shifts.
    - current_machinestudy_multibunch_average
        Current average for machine study multi bunch shifts.
    - current_machinestudy_multibunch_stddev
        Current standard deviation for machine study multi bunch shifts.
    - current_machinestudy_multibunch_time
        Time of machine study multi bunch shifts.
    - current_machinestudy_total_average
        Current average for machine study shifts.
    - current_machinestudy_total_stddev
        Current standard deviation for machine study shifts.
    - current_machinestudy_total_time
        Time of machine study shifts.
    - current_commissioning_singlebunch_average
        Current average for single bunch commissioning shifts.
    - current_commissioning_singlebunch_stddev
        Current standard deviation for single bunch commissioning shifts.
    - current_commissioning_singlebunch_time
        Time of single bunch commissioning shifts.
    - current_commissioning_multibunch_average
        Current average for multi bunch commissioning shifts.
    - current_commissioning_multibunch_stddev
        Current standard deviation for multi bunch commissioning shifts.
    - current_commissioning_multibunch_time
        Time of multi bunch commissioning shifts.
    - current_commissioning_total_average
        Current average in commissioning shifts.
    - current_commissioning_total_stddev
        Current standard deviation in commissioning shifts.
    - current_commissioning_total_time
        Time of commissioning shifts.
    - current_conditioning_singlebunch_average
        Current average for single bunch conditioning shifts.
    - current_conditioning_singlebunch_stddev
        Current standard deviation for single bunch conditioning shifts.
    - current_conditioning_singlebunch_time
        Time of single bunch conditioning shifts.
    - current_conditioning_multibunch_average
        Current average for multi bunch conditioning shifts.
    - current_conditioning_multibunch_stddev
        Current standard deviation for multi bunch conditioning shifts.
    - current_conditioning_multibunch_time
        Time of multi bunch conditioning shifts.
    - current_conditioning_total_average
        Current average in conditioning shifts.
    - current_conditioning_total_stddev
        Current standard deviation in conditioning shifts.
    - current_conditioning_total_time
        Time of conditioning shifts.
    - current_user_singlebunch_average
        Current average for single bunch user shifts.
    - current_user_singlebunch_stddev
        Current standard deviation for single bunch user shifts.
    - current_user_singlebunch_time
        Time of single bunch user shifts.
    - current_user_multibunch_average
        Current average for multi bunch user shifts.
    - current_user_multibunch_stddev
        Current standard deviation for multi bunch user shifts.
    - current_user_multibunch_time
        Time of multi bunch user shifts.
    - current_user_total_average
        Current average in all user shifts.
    - current_user_total_stddev
        Current standard deviation in all user shifts.
    - current_user_total_time
        Time of all user shifts.
    - current_ebeam_singlebunch_average
        Current average for all single bunch shifts.
    - current_ebeam_singlebunch_stddev
        Current standard deviation for all single bunch shifts.
    - current_ebeam_singlebunch_time
        Time of all single bunch shifts.
    - current_ebeam_multibunch_average
        Current average for all multi bunch shifts.
    - current_ebeam_multibunch_stddev
        Current standard deviation for all multi bunch shifts.
    - current_ebeam_multibunch_time
        Time of all multi bunch shifts.
    - current_ebeam_total_average
        Average current considering the entire time in which
        there was any current above a threshold (THOLD_STOREDBEAM)
    - current_ebeam_total_stddev
        Current standard deviation considering the entire time in which
        there was any current above a threshold (THOLD_STOREDBEAM)
    - current_ebeam_total_time
        Time in which there was stored beam, for any
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
        self._usershift_progmd_time = None
        self._usershift_delivd_time = None
        self._usershift_extra_time = None
        self._usershift_total_time = None
        self._usershift_progmd_count = None
        self._usershift_current_average = None
        self._usershift_current_stddev = None
        self._usershift_current_beg_average = None
        self._usershift_current_beg_stddev = None
        self._usershift_current_end_average = None
        self._usershift_current_end_stddev = None
        self._usershift_total_failures_time = None
        self._usershift_failures_count = None
        self._usershift_beam_dump_count = None
        self._usershift_time_to_recover_average = None
        self._usershift_time_to_recover_stddev = None
        self._usershift_time_between_failures_average = None
        self._usershift_beam_reliability = None
        self._usershift_total_stable_beam_time = None
        self._usershift_total_unstable_beam_time = None
        self._usershift_unstable_beam_count = None
        self._usershift_time_between_unstable_beams_average = None
        self._usershift_relative_stable_beam_time = None
        self._usershift_total_injection_time = None
        self._usershift_injection_count = None
        self._usershift_injection_time_average = None
        self._usershift_injection_time_stddev = None

        # light source usage stats
        self._lsusage_total_time = None
        self._lsusage_machinestudy_failures_time = None
        self._lsusage_machinestudy_failures = None
        self._lsusage_machinestudy_operational_time = None
        self._lsusage_machinestudy_operational = None
        self._lsusage_machinestudy_time = None
        self._lsusage_machinestudy = None
        self._lsusage_commissioning_failures_time = None
        self._lsusage_commissioning_failures = None
        self._lsusage_commissioning_operational_time = None
        self._lsusage_commissioning_operational = None
        self._lsusage_commissioning_time = None
        self._lsusage_commissioning = None
        self._lsusage_conditioning_failures_time = None
        self._lsusage_conditioning_failures = None
        self._lsusage_conditioning_operational_time = None
        self._lsusage_conditioning_operational = None
        self._lsusage_conditioning_time = None
        self._lsusage_conditioning = None
        self._lsusage_maintenance_failures_time = None
        self._lsusage_maintenance_failures = None
        self._lsusage_maintenance_operational_time = None
        self._lsusage_maintenance_operational = None
        self._lsusage_maintenance_time = None
        self._lsusage_maintenance = None
        self._lsusage_user_failures_time = None
        self._lsusage_user_failures = None
        self._lsusage_user_operational_time = None
        self._lsusage_user_operational = None
        self._lsusage_user_time = None
        self._lsusage_user = None

        # stored current stats
        self._current_machinestudy_singlebunch_average = None
        self._current_machinestudy_singlebunch_stddev = None
        self._current_machinestudy_singlebunch_time = None
        self._current_machinestudy_multibunch_average = None
        self._current_machinestudy_multibunch_stddev = None
        self._current_machinestudy_multibunch_time = None
        self._current_machinestudy_total_average = None
        self._current_machinestudy_total_stddev = None
        self._current_machinestudy_total_time = None
        self._current_commissioning_singlebunch_average = None
        self._current_commissioning_singlebunch_stddev = None
        self._current_commissioning_singlebunch_time = None
        self._current_commissioning_multibunch_average = None
        self._current_commissioning_multibunch_stddev = None
        self._current_commissioning_multibunch_time = None
        self._current_commissioning_total_average = None
        self._current_commissioning_total_stddev = None
        self._current_commissioning_total_time = None
        self._current_conditioning_singlebunch_average = None
        self._current_conditioning_singlebunch_stddev = None
        self._current_conditioning_singlebunch_time = None
        self._current_conditioning_multibunch_average = None
        self._current_conditioning_multibunch_stddev = None
        self._current_conditioning_multibunch_time = None
        self._current_conditioning_total_average = None
        self._current_conditioning_total_stddev = None
        self._current_conditioning_total_time = None
        self._current_user_singlebunch_average = None
        self._current_user_singlebunch_stddev = None
        self._current_user_singlebunch_time = None
        self._current_user_multibunch_average = None
        self._current_user_multibunch_stddev = None
        self._current_user_multibunch_time = None
        self._current_user_total_average = None
        self._current_user_total_stddev = None
        self._current_user_total_time = None
        self._current_ebeam_singlebunch_average = None
        self._current_ebeam_singlebunch_stddev = None
        self._current_ebeam_singlebunch_time = None
        self._current_ebeam_multibunch_average = None
        self._current_ebeam_multibunch_stddev = None
        self._current_ebeam_multibunch_time = None
        self._current_ebeam_total_average = None
        self._current_ebeam_total_stddev = None
        self._current_ebeam_total_time = None

        # auxiliary data
        self._raw_data = None
        self._curr_times = None
        self._curr_values = None
        self._ps_fail_values = None
        self._gamblk_fail_values = None
        self._sofbloop_fail_values = None
        self._mps_fail_values = None
        self._inj_shift_values = None
        self._machinestudy_shift_values = None
        self._commissioning_shift_values = None
        self._conditioning_shift_values = None
        self._maintenance_shift_values = None
        self._user_shift_values = None
        self._user_shift_act_values = None
        self._user_shift_progmd_values = None
        self._user_shift_inicurr_values = None
        self._user_shift_delivd_values = None
        self._user_shift_stable_values = None
        self._is_stored_total = None
        self._is_stored_users = None
        self._singlebunch_values = None
        self._multibunch_values = None
        self._failures_users = None
        self._distortions_users = None

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

    # user shift stats

    @property
    def usershift_progmd_time(self):
        """Programmed time [h]."""
        return self._conv_sec_2_hour(self._usershift_progmd_time)

    @property
    def usershift_delivd_time(self):
        """Delivered time [h]."""
        return self._conv_sec_2_hour(self._usershift_delivd_time)

    @property
    def usershift_extra_time(self):
        """Extra time [h]."""
        return self._conv_sec_2_hour(self._usershift_extra_time)

    @property
    def usershift_total_time(self):
        """Total time (delivered + extra) [h]."""
        return self._conv_sec_2_hour(self._usershift_total_time)

    @property
    def usershift_current_average(self):
        """Current average."""
        return self._usershift_current_average

    @property
    def usershift_current_stddev(self):
        """Current standard deviation."""
        return self._usershift_current_stddev

    @property
    def usershift_current_beg_average(self):
        """Current average at the beginning of the shift."""
        return self._usershift_current_beg_average

    @property
    def usershift_current_beg_stddev(self):
        """Current st.dev. at the beginning of the shift."""
        return self._usershift_current_beg_stddev

    @property
    def usershift_current_end_average(self):
        """Current average at the end of the shift."""
        return self._usershift_current_end_average

    @property
    def usershift_current_end_stddev(self):
        """Current st.dev. at the end of the shift."""
        return self._usershift_current_end_stddev

    @property
    def usershift_progmd_count(self):
        """Number of programmed shifts."""
        return self._usershift_progmd_count

    @property
    def usershift_total_failures_time(self):
        """Total failures time [h]."""
        return self._conv_sec_2_hour(self._usershift_total_failures_time)

    @property
    def usershift_failures_count(self):
        """Number of failures."""
        return self._usershift_failures_count

    @property
    def usershift_beam_dump_count(self):
        """Number of beam dumps."""
        return self._usershift_beam_dump_count

    @property
    def usershift_time_to_recover_average(self):
        """Average time took to recover from failures [h]."""
        return self._conv_sec_2_hour(self._usershift_time_to_recover_average)

    @property
    def usershift_time_to_recover_stddev(self):
        """Time std.dev. took to recover from failures [h]."""
        return self._conv_sec_2_hour(self._usershift_time_to_recover_stddev)

    @property
    def usershift_time_between_failures_average(self):
        """Average time between failure occurrences [h]."""
        return self._conv_sec_2_hour(
            self._usershift_time_between_failures_average)

    @property
    def usershift_beam_reliability(self):
        """Beam reliability. Ratio between delivered and programmed time."""
        return self._usershift_beam_reliability

    @property
    def usershift_total_stable_beam_time(self):
        """Total stable beam time [h]."""
        return self._conv_sec_2_hour(self._usershift_total_stable_beam_time)

    @property
    def usershift_total_unstable_beam_time(self):
        """Total unstable beam time [h]."""
        return self._conv_sec_2_hour(self._usershift_total_unstable_beam_time)

    @property
    def usershift_unstable_beam_count(self):
        """Number of unstable beam occurrences."""
        return self._usershift_unstable_beam_count

    @property
    def usershift_time_between_unstable_beams_average(self):
        """Average time between unstable beam occurrences [h]."""
        return self._conv_sec_2_hour(
            self._usershift_time_between_unstable_beams_average)

    @property
    def usershift_relative_stable_beam_time(self):
        """Ratio between stable + delivered and programmed time."""
        return self._usershift_relative_stable_beam_time

    @property
    def usershift_total_injection_time(self):
        """Total injection shift [h]."""
        return self._conv_sec_2_hour(self._usershift_total_injection_time)

    @property
    def usershift_injection_count(self):
        """Number of injections."""
        return self._usershift_injection_count

    @property
    def usershift_injection_time_average(self):
        """Average time used for injection [h]."""
        return self._conv_sec_2_hour(
            self._usershift_injection_time_average)

    @property
    def usershift_injection_time_stddev(self):
        """Standard deviation of time used for injection [h]."""
        return self._conv_sec_2_hour(self._usershift_injection_time_stddev)

    # light source usage stats

    @property
    def lsusage_total_time(self):
        """Total time of Light Source Usage."""
        return self._conv_sec_2_hour(self._lsusage_total_time)

    @property
    def lsusage_machinestudy_failures_time(self):
        """Failures time in Machine Study Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_machinestudy_failures_time)

    @property
    def lsusage_machinestudy_failures(self):
        """Relative failures time in Machine Study Shift."""
        return self._lsusage_machinestudy_failures

    @property
    def lsusage_machinestudy_operational_time(self):
        """Operational time in Machine Study Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_machinestudy_operational_time)

    @property
    def lsusage_machinestudy_operational(self):
        """Relative operational time in Machine Study Shift."""
        return self._lsusage_machinestudy_operational

    @property
    def lsusage_machinestudy_time(self):
        """Time in Machine Study Shift."""
        return self._conv_sec_2_hour(self._lsusage_machinestudy_time)

    @property
    def lsusage_machinestudy(self):
        """Relative time in Machine Study Shift."""
        return self._lsusage_machinestudy

    @property
    def lsusage_commissioning_failures_time(self):
        """Failures time in Commissioning Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_commissioning_failures_time)

    @property
    def lsusage_commissioning_failures(self):
        """Relative failures time in Commissioning Shift."""
        return self._lsusage_commissioning_failures

    @property
    def lsusage_commissioning_operational_time(self):
        """Operational time in Commissioning Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_commissioning_operational_time)

    @property
    def lsusage_commissioning_operational(self):
        """Relative operational time in Commissioning Shift."""
        return self._lsusage_commissioning_operational

    @property
    def lsusage_commissioning_time(self):
        """Time in Commissioning Shift."""
        return self._conv_sec_2_hour(self._lsusage_commissioning_time)

    @property
    def lsusage_commissioning(self):
        """Relative time in Commissioning Shift."""
        return self._lsusage_commissioning

    @property
    def lsusage_conditioning_failures_time(self):
        """Failures time in Conditioning Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_conditioning_failures_time)

    @property
    def lsusage_conditioning_failures(self):
        """Relative failures time in Conditioning Shift."""
        return self._lsusage_conditioning_failures

    @property
    def lsusage_conditioning_operational_time(self):
        """Operational time in Conditioning Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_conditioning_operational_time)

    @property
    def lsusage_conditioning_operational(self):
        """Relative operational time in Conditioning Shift."""
        return self._lsusage_conditioning_operational

    @property
    def lsusage_conditioning_time(self):
        """Time in Conditioning Shift."""
        return self._conv_sec_2_hour(self._lsusage_conditioning_time)

    @property
    def lsusage_conditioning(self):
        """Relative time in Conditioning Shift."""
        return self._lsusage_conditioning

    @property
    def lsusage_maintenance_failures_time(self):
        """Failures time in Maintenance Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_maintenance_failures_time)

    @property
    def lsusage_maintenance_failures(self):
        """Relative failures time in Maintenance Shift."""
        return self._lsusage_maintenance_failures

    @property
    def lsusage_maintenance_operational_time(self):
        """Operational time in Maintenance Shift."""
        return self._conv_sec_2_hour(
            self._lsusage_maintenance_operational_time)

    @property
    def lsusage_maintenance_operational(self):
        """Relative operational time in Maintenance Shift."""
        return self._lsusage_maintenance_operational

    @property
    def lsusage_maintenance_time(self):
        """Time in Maintenance Shift."""
        return self._conv_sec_2_hour(self._lsusage_maintenance_time)

    @property
    def lsusage_maintenance(self):
        """Relative time in Maintenance Shift."""
        return self._lsusage_maintenance

    @property
    def lsusage_user_failures_time(self):
        """Failures time in Users Shift."""
        return self._conv_sec_2_hour(self._lsusage_user_failures_time)

    @property
    def lsusage_user_failures(self):
        """Relative failures time in Users Shift."""
        return self._lsusage_user_failures

    @property
    def lsusage_user_operational_time(self):
        """Operational time in Users Shift."""
        return self._conv_sec_2_hour(self._lsusage_user_operational_time)

    @property
    def lsusage_user_operational(self):
        """Relative operational time in Users Shift."""
        return self._lsusage_user_operational

    @property
    def lsusage_user_time(self):
        """Time in Users Shift."""
        return self._conv_sec_2_hour(self._lsusage_user_time)

    @property
    def lsusage_user(self):
        """Relative time in Users Shift."""
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
    def current_machinestudy_singlebunch_time(self):
        """Time of machine study single bunch shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_machinestudy_singlebunch_time)

    @property
    def current_machinestudy_multibunch_average(self):
        """Current average for machine study multi bunch shifts."""
        return self._current_machinestudy_multibunch_average

    @property
    def current_machinestudy_multibunch_stddev(self):
        """Current standard deviation for machine study multi bunch shifts."""
        return self._current_machinestudy_multibunch_stddev

    @property
    def current_machinestudy_multibunch_time(self):
        """Time of machine study multi bunch shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_machinestudy_multibunch_time)

    @property
    def current_machinestudy_total_average(self):
        """Current average for machine study shifts."""
        return self._current_machinestudy_total_average

    @property
    def current_machinestudy_total_stddev(self):
        """Current standard deviation for machine study shifts."""
        return self._current_machinestudy_total_stddev

    @property
    def current_machinestudy_total_time(self):
        """Time of machine study shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(self._current_machinestudy_total_time)

    @property
    def current_commissioning_singlebunch_average(self):
        """Current average for single bunch commissioning shifts."""
        return self._current_commissioning_singlebunch_average

    @property
    def current_commissioning_singlebunch_stddev(self):
        """Current standard deviation for single bunch commissioning shifts."""
        return self._current_commissioning_singlebunch_stddev

    @property
    def current_commissioning_singlebunch_time(self):
        """Time of single bunch commissioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_commissioning_singlebunch_time)

    @property
    def current_commissioning_multibunch_average(self):
        """Current average for multi bunch commissioning shifts."""
        return self._current_commissioning_multibunch_average

    @property
    def current_commissioning_multibunch_stddev(self):
        """Current standard deviation for multi bunch commissioning shifts."""
        return self._current_commissioning_multibunch_stddev

    @property
    def current_commissioning_multibunch_time(self):
        """Time of multi bunch commissioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_commissioning_multibunch_time)

    @property
    def current_commissioning_total_average(self):
        """Current average in commissioning shifts."""
        return self._current_commissioning_total_average

    @property
    def current_commissioning_total_stddev(self):
        """Current standard deviation in commissioning shifts."""
        return self._current_commissioning_total_stddev

    @property
    def current_commissioning_total_time(self):
        """Time of commissioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_commissioning_total_time)

    @property
    def current_conditioning_singlebunch_average(self):
        """Current average for single bunch conditioning shifts."""
        return self._current_conditioning_singlebunch_average

    @property
    def current_conditioning_singlebunch_stddev(self):
        """Current standard deviation for single bunch conditioning shifts."""
        return self._current_conditioning_singlebunch_stddev

    @property
    def current_conditioning_singlebunch_time(self):
        """Time of single bunch conditioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_conditioning_singlebunch_time)

    @property
    def current_conditioning_multibunch_average(self):
        """Current average for multi bunch conditioning shifts."""
        return self._current_conditioning_multibunch_average

    @property
    def current_conditioning_multibunch_stddev(self):
        """Current standard deviation for multi bunch conditioning shifts."""
        return self._current_conditioning_multibunch_stddev

    @property
    def current_conditioning_multibunch_time(self):
        """Time of multi bunch conditioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(
            self._current_conditioning_multibunch_time)

    @property
    def current_conditioning_total_average(self):
        """Current average in conditioning shifts."""
        return self._current_conditioning_total_average

    @property
    def current_conditioning_total_stddev(self):
        """Current standard deviation in conditioning shifts."""
        return self._current_conditioning_total_stddev

    @property
    def current_conditioning_total_time(self):
        """Time of conditioning shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(self._current_conditioning_total_time)

    @property
    def current_user_singlebunch_average(self):
        """Current average for single bunch user shifts."""
        return self._current_user_singlebunch_average

    @property
    def current_user_singlebunch_stddev(self):
        """Current standard deviation for single bunch user shifts."""
        return self._current_user_singlebunch_stddev

    @property
    def current_user_singlebunch_time(self):
        """Time of single bunch user shifts.
        Consider any stored current."""
        return self._conv_sec_2_hour(self._current_user_singlebunch_time)

    @property
    def current_user_multibunch_average(self):
        """Current average for multi bunch user shifts."""
        return self._current_user_multibunch_average

    @property
    def current_user_multibunch_stddev(self):
        """Current standard deviation for multi bunch user shifts."""
        return self._current_user_multibunch_stddev

    @property
    def current_user_multibunch_time(self):
        """Time of multi bunch user shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_user_multibunch_time)

    @property
    def current_user_total_average(self):
        """Current average in all user shifts."""
        return self._current_user_total_average

    @property
    def current_user_total_stddev(self):
        """Current standard deviation in all user shifts."""
        return self._current_user_total_stddev

    @property
    def current_user_total_time(self):
        """Time of user shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_user_total_time)

    @property
    def current_ebeam_singlebunch_average(self):
        """Current average for all single bunch shifts."""
        return self._current_ebeam_singlebunch_average

    @property
    def current_ebeam_singlebunch_stddev(self):
        """Current standard deviation for all single bunch shifts."""
        return self._current_ebeam_singlebunch_stddev

    @property
    def current_ebeam_singlebunch_time(self):
        """Time of all single bunch shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_ebeam_singlebunch_time)

    @property
    def current_ebeam_multibunch_average(self):
        """Current average for all multi bunch shifts."""
        return self._current_ebeam_multibunch_average

    @property
    def current_ebeam_multibunch_stddev(self):
        """Current standard deviation for all multi bunch shifts."""
        return self._current_ebeam_multibunch_stddev

    @property
    def current_ebeam_multibunch_time(self):
        """Time of all multi bunch shifts. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_ebeam_multibunch_time)

    @property
    def current_ebeam_total_average(self):
        """Current average for all stored beam time."""
        return self._current_ebeam_total_average

    @property
    def current_ebeam_total_stddev(self):
        """Current standard deviation for all stored beam time."""
        return self._current_ebeam_total_stddev

    @property
    def current_ebeam_total_time(self):
        """Stored beam time [h]. Consider any stored current."""
        return self._conv_sec_2_hour(self._current_ebeam_total_time)

    @property
    def raw_data(self):
        """Shift data and failures details."""
        return self._raw_data

    def update(self):
        """Update."""
        if self._time_start >= self._time_stop:
            raise ValueError('Invalid time interval.')

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
        self._pvdata[self._current_pv].parallel_query_bin_interval = 60*60*6
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

        fig, axs = _plt.subplots(14, 1, sharex=True)
        fig.set_size_inches(9, 10)
        fig.subplots_adjust(top=0.96, left=0.08, bottom=0.05, right=0.96)
        axs[0].set_title('Raw data', fontsize=12)

        axs[0].xaxis.axis_date()
        axs[0].plot(
            datetimes, self._raw_data['Current'], '-',
            color='blue', label='Current')
        axs[0].legend(loc='upper left', fontsize=9)
        axs[0].grid()

        axs[1].xaxis.axis_date()
        axs[1].plot(
            datetimes, self._raw_data['UserShiftInitCurr'], '-',
            color='blue', label='User Shifts - Initial Current')
        axs[1].legend(loc='upper left', fontsize=9)
        axs[1].grid()

        axs[2].xaxis.axis_date()
        axs[2].plot(
            datetimes, self._raw_data['UserShiftProgmd'], '-',
            color='gold', label='User Shifts - Programmed')
        axs[2].legend(loc='upper left', fontsize=9)
        axs[2].grid()

        axs[3].xaxis.axis_date()
        axs[3].plot(
            datetimes, self._raw_data['UserShiftDelivd'], '-',
            color='gold', label='User Shifts - Delivered')
        axs[3].legend(loc='upper left', fontsize=9)
        axs[3].grid()

        axs[4].xaxis.axis_date()
        axs[4].plot(
            datetimes, self._raw_data['UserShiftStable'], '-',
            color='gold', label='User Shifts - Delivered Without Distortions')
        axs[4].legend(loc='upper left', fontsize=9)
        axs[4].grid()

        axs[5].xaxis.axis_date()
        axs[5].plot(
            datetimes, self._raw_data['UserShiftTotal'], '-',
            color='gold', label='User Shifts - Total')
        axs[5].legend(loc='upper left', fontsize=9)
        axs[5].grid()

        axs[6].xaxis.axis_date()
        axs[6].plot(
            datetimes, self._raw_data['Failures']['NoEBeam'], '-',
            color='red', label='Failures - NoEBeam')
        axs[6].legend(loc='upper left', fontsize=9)
        axs[6].grid()

        axs[7].xaxis.axis_date()
        axs[7].plot(
            datetimes, self._raw_data['GammaShutter'], '-',
            color='red', label='Failures - Gamma Shutter Closed')
        axs[7].legend(loc='upper left', fontsize=9)
        axs[7].grid()

        axs[8].xaxis.axis_date()
        axs[8].plot(
            datetimes, self._raw_data['Failures']['WrongShift'], '-',
            color='red', label='Failures - WrongShift')
        axs[8].legend(loc='upper left', fontsize=9)
        axs[8].grid()

        axs[9].xaxis.axis_date()
        axs[9].plot(
            datetimes, self._raw_data['Failures']['SubsystemsNOk'], '-',
            color='red', label='Failures - PS, RF and MPS')
        axs[9].legend(loc='upper left', fontsize=9)
        axs[9].grid()

        axs[10].xaxis.axis_date()
        axs[10].plot(
            datetimes, self._raw_data['Distortions']['SOFBLoop'], '-',
            color='orangered', label='Distortions - SOFB Loop Open')
        axs[10].legend(loc='upper left', fontsize=9)
        axs[10].grid()

        axs[11].xaxis.axis_date()
        axs[11].plot(
            datetimes, self._raw_data['Shift']['Injection'], '-',
            color='lightsalmon', label='Injection Shifts')
        axs[11].legend(loc='upper left', fontsize=9)
        axs[11].grid()

        shift2color = {
            'MachineStudy': ['MacStudy', 'skyblue'],
            'Commissioning': ['Commi', 'royalblue'],
            'Conditioning': ['Condit', 'orchid'],
            'Maintenance': ['Maint', 'green']}
        for shift, auxdata in shift2color.items():
            ydata = self._raw_data['Shift'][shift]

            axs[12].xaxis.axis_date()
            axs[12].plot(
                datetimes, ydata, '-',
                color=auxdata[1], label=auxdata[0])
        axs[12].legend(loc='upper left', ncol=4, fontsize=9)
        axs[12].set_ylim(0.0, 2.0)
        axs[12].grid()

        egmodes2color = {
            'MultiBunch': 'orangered', 'SingleBunch': 'orange'}
        for egmode, color in egmodes2color.items():
            ydata = self._raw_data['EgunModes'][egmode]

            axs[13].xaxis.axis_date()
            axs[13].plot(
                datetimes, ydata, '-',
                color=color, label=egmode)
        axs[13].legend(loc='upper left', ncol=2, fontsize=9)
        axs[13].set_ylim(0.0, 2.0)
        axs[13].grid()

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
        dtimes_users_delivd = dtimes*self._raw_data['UserShiftDelivd']
        cum_deliv = _np.cumsum(dtimes_users_delivd)

        fig = _plt.figure()
        axs = _plt.gca()
        axs.xaxis.axis_date()
        axs.plot(datetimes, cum_progmd, '-', label='Programmed')
        axs.plot(datetimes, cum_deliv, '-', label='Delivered')
        axs.grid()
        axs.set_ylabel('Integrated Hours')
        _plt.legend(loc=4)
        _plt.title('Integrated User Hours')
        return fig

    # ----- auxiliary methods -----

    def _init_connectors(self):
        self._current_pv = 'SI-Glob:AP-CurrInfo:Current-Mon'
        self._macshift_pv = 'AS-Glob:AP-MachShift:Mode-Sts'
        self._egtrgen_pv = 'LI-01:EG-TriggerPS:enablereal'
        self._egpusel_pv = 'LI-01:EG-PulsePS:singleselstatus'
        self._injevt_pv = 'AS-RaMO:TI-EVG:InjectionEvt-Sts'
        self._gammashutt_pv = 'AS-Glob:PP-GammaShutter:Status-Mon'
        self._siintlk_pv = 'RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon'
        self._sisofbloop_pv = 'SI-Glob:AP-SOFB:LoopState-Sts'
        self._pvnames = [
            self._current_pv, self._macshift_pv,
            self._egtrgen_pv, self._egpusel_pv, self._injevt_pv,
            self._gammashutt_pv, self._siintlk_pv,
            self._sisofbloop_pv]

        self._pvdata = dict()
        self._pv2default = dict()
        for pvname in self._pvnames:
            self._pvdata[pvname] = _PVData(pvname, self._connector)
            self._pv2default[pvname] = 0.0 if pvname != self._macshift_pv\
                else _Cte.MachShift.Commissioning

        self._si_fams_psnames = _PSSearch.get_psnames(
            {'sec': 'SI', 'sub': 'Fam', 'dev': '(B|Q|S).*'})
        self._psgroup2psname = {'fams': self._si_fams_psnames}
        groups = {'corrs': '(CH|CV)',
                  'trims': 'Q(F|D|[1-4]).*',
                  'skews': 'QS'}
        subs = ['(0[1-5]).*', '(0[6-9]|10).*',
                '(1[1-5]).*', '(1[6-9]|20).*']
        for psdesc, psreg in groups.items():
            for idx, sub in enumerate(subs):
                key = psdesc+' ('+str(idx+1)+'/'+str(len(subs))+')'
                value = _PSSearch.get_psnames(
                    {'sec': 'SI', 'sub': sub, 'dev': psreg})
                self._psgroup2psname[key] = value

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
        _curr_times, _curr_values = \
            self._get_pv_data('SI-Glob:AP-CurrInfo:Current-Mon')
        _curr_values[_curr_values < 0] = 0
        _curr_values[_curr_values > 500] = 0

        # resample current data, from 1 pt in 60s, to 1pt in 5s
        new_len = (len(_curr_times)-1)*12 + 1
        new_times = _np.linspace(_curr_times[0], _curr_times[-1], new_len)
        self._curr_times = new_times
        self._curr_values = _np.interp(
            new_times, _curr_times, _curr_values)

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

        sofbloop_times, sofbloop_values = \
            self._get_pv_data('SI-Glob:AP-SOFB:LoopState-Sts')
        sofbloop_fail_rawvalues = _np.array(
            [1*(v == _SOFBCte.LoopState.Open) for v in sofbloop_values])
        self._sofbloop_fail_values = _interp1d_previous(
            sofbloop_times, sofbloop_fail_rawvalues, self._curr_times)

        # rf and mps status data
        siintlk_times, siintlk_values = \
            self._get_pv_data('RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon')
        self._mps_fail_values = _interp1d_previous(
            siintlk_times, siintlk_values, self._curr_times)

        # delivered shift data
        shift_times, shift_values = \
            self._get_pv_data('AS-Glob:AP-MachShift:Mode-Sts')

        self._raw_data['Shift'] = dict()

        inj_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Injection) for v in shift_values])
        self._inj_shift_values = _interp1d_previous(
            shift_times, inj_shift_values, self._curr_times)
        self._raw_data['Shift']['Injection'] = self._inj_shift_values

        stdy_shift_values = _np.array(
            [1*(v == _Cte.MachShift.MachineStudy) for v in shift_values])
        self._machinestudy_shift_values = _interp1d_previous(
            shift_times, stdy_shift_values, self._curr_times)
        self._raw_data['Shift']['MachineStudy'] = \
            self._machinestudy_shift_values

        cmm_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Commissioning) for v in shift_values])
        self._commissioning_shift_values = _interp1d_previous(
            shift_times, cmm_shift_values, self._curr_times)
        self._raw_data['Shift']['Commissioning'] = \
            self._commissioning_shift_values

        cdt_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Conditioning) for v in shift_values])
        self._conditioning_shift_values = _interp1d_previous(
            shift_times, cdt_shift_values, self._curr_times)
        self._raw_data['Shift']['Conditioning'] = \
            self._conditioning_shift_values

        mtn_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Maintenance) for v in shift_values])
        self._maintenance_shift_values = _interp1d_previous(
            shift_times, mtn_shift_values, self._curr_times)
        self._raw_data['Shift']['Maintenance'] = self._maintenance_shift_values

        user_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Users) for v in shift_values])
        self._user_shift_values = _interp1d_previous(
            shift_times, user_shift_values, self._curr_times)

        # desired shift data
        _t0 = _time.time()
        self._user_shift_progmd_values = \
            _MacScheduleData.is_user_shift_programmed(
                timestamp=self._curr_times)
        self._user_shift_inicurr_values = \
            _MacScheduleData.get_initial_current_programmed(
                timestamp=self._curr_times)
        self._usershift_progmd_count = \
            _MacScheduleData.get_users_shift_count(
                self._curr_times[0], self._curr_times[-1])
        self._update_log(
            'Query for machine schedule data took {0:.3f}s'.format(
                _time.time()-_t0))
        self._raw_data['UserShiftProgmd'] = self._user_shift_progmd_values
        self._raw_data['UserShiftInitCurr'] = self._user_shift_inicurr_values

        # single/multi bunch mode data
        inj_ts, inj_vs = self._get_pv_data('AS-RaMO:TI-EVG:InjectionEvt-Sts')
        inj_vs = _interp1d_previous(inj_ts, inj_vs, self._curr_times)
        trig_ts, trig_vs = self._get_pv_data('LI-01:EG-TriggerPS:enablereal')
        trig_vs = _interp1d_previous(trig_ts, trig_vs, self._curr_times)
        sb_ts, sb_vs = self._get_pv_data('LI-01:EG-PulsePS:singleselstatus')
        sb_vs = _interp1d_previous(sb_ts, sb_vs, self._curr_times)
        idcs1 = _np.where(inj_vs*trig_vs*sb_vs)[0]
        mode_ts = self._curr_times[idcs1]
        mode_vs = [1]*len(idcs1)
        idcs2 = _np.where(inj_vs*trig_vs*1*_np.logical_not(sb_vs))[0]
        mode_ts = _np.r_[mode_ts, self._curr_times[idcs2]]
        mode_vs = _np.r_[mode_vs, [0]*len(idcs2)]
        ind = mode_ts.argsort()
        mode_ts, mode_vs = mode_ts[ind], mode_vs[ind]
        mode_vs = _interp1d_previous(mode_ts, mode_vs, self._curr_times)
        self._singlebunch_values = mode_vs
        self._multibunch_values = _np.logical_not(mode_vs)
        self._raw_data['EgunModes'] = dict()
        self._raw_data['EgunModes']['SingleBunch'] = self._singlebunch_values
        self._raw_data['EgunModes']['MultiBunch'] = self._multibunch_values

        # is stored data
        self._is_stored_total = self._curr_values > MacReport.THOLD_STOREDBEAM
        self._is_stored_users = self._curr_values >= \
            self._user_shift_inicurr_values*MacReport.THOLD_FACTOR_USERSSBEAM

        # auxiliary time vectors
        dtimes = _np.diff(self._curr_times)
        dtimes = _np.r_[dtimes, dtimes[-1]]

        dtimes_users_progmd = dtimes*self._user_shift_progmd_values
        dtimes_injection = dtimes*self._inj_shift_values
        dtimes_machinestudy = dtimes*self._machinestudy_shift_values
        dtimes_commissioning = dtimes*self._commissioning_shift_values
        dtimes_conditioning = dtimes*self._conditioning_shift_values
        dtimes_maintenance = dtimes*self._maintenance_shift_values

        # failures
        self._raw_data['Failures'] = dict()
        self._raw_data['Failures']['SubsystemsNOk'] = _np.logical_or(
            self._ps_fail_values, self._mps_fail_values)
        self._raw_data['Failures']['GammaShutter'] = \
            self._gamblk_fail_values.astype(int)
        self._raw_data['Failures']['NoEBeam'] = \
            _np.logical_not(self._is_stored_users)

        # # # ignore wrong shift failures shorter than 60s
        wrong_shift = \
            1 * ((self._user_shift_progmd_values-self._user_shift_values) > 0)
        ignore_wrong_shift = _np.zeros(wrong_shift.shape)
        for i, val in enumerate(wrong_shift):
            if i >= len(wrong_shift)-12:
                break
            if val == 1 and not _np.sum(wrong_shift[(i-12):(i+12)]) >= 12:
                ignore_wrong_shift[i] = 1
        consider_wrong_shift = wrong_shift - ignore_wrong_shift
        self._raw_data['Failures']['WrongShift'] = consider_wrong_shift

        self._failures_users = 1 * _np.logical_or.reduce(
            [value for value in self._raw_data['Failures'].values()]) * \
            self._user_shift_progmd_values
        dtimes_failures_users = dtimes*self._failures_users

        self._user_shift_delivd_values = self._user_shift_progmd_values * \
            _np.logical_not(self._failures_users)
        self._raw_data['UserShiftDelivd'] = self._user_shift_delivd_values
        dtimes_users_delivd = dtimes*self._user_shift_delivd_values

        # distortions
        self._raw_data['Distortions'] = dict()
        self._raw_data['Distortions']['SOFBLoop'] = \
            self._sofbloop_fail_values

        self._distortions_users = 1 * _np.logical_or.reduce(
            [value for value in self._raw_data['Distortions'].values()]) * \
            self._user_shift_delivd_values
        dtimes_distortions_users = dtimes*self._distortions_users

        self._user_shift_stable_values = self._user_shift_delivd_values * \
            _np.logical_not(self._distortions_users)
        self._raw_data['UserShiftStable'] = self._user_shift_stable_values
        dtimes_users_stable = dtimes*self._user_shift_stable_values

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
        self._usershift_progmd_time = _np.sum(dtimes_users_progmd)

        self._usershift_delivd_time = _np.sum(dtimes_users_delivd)

        self._usershift_extra_time = _np.sum(dtimes_users_extra)

        self._usershift_total_time = _np.sum(dtimes_users_total)

        self._usershift_current_average, self._usershift_current_stddev = \
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
            self._usershift_current_beg_average = _np.mean(stats_vals)
            self._usershift_current_beg_stddev = _np.std(stats_vals)
        else:
            self._usershift_current_beg_average = 0
            self._usershift_current_beg_stddev = 0

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
            self._usershift_current_end_average = _np.mean(stats_vals)
            self._usershift_current_end_stddev = _np.std(stats_vals)
        else:
            self._usershift_current_end_average = 0
            self._usershift_current_end_stddev = 0

        # # # ----- failures -----
        self._usershift_total_failures_time = _np.sum(dtimes_failures_users)

        beam_dump_values = _np.logical_not(
            self._raw_data['Failures']['WrongShift']) * \
            self._raw_data['Failures']['NoEBeam']
        self._usershift_beam_dump_count = _np.sum(
            _np.diff(beam_dump_values) > 0)

        ave, std, count = self._calc_interval_stats(
            self._failures_users, dtimes_failures_users)
        self._usershift_time_to_recover_average = ave
        self._usershift_time_to_recover_stddev = std
        self._usershift_failures_count = count

        self._usershift_time_between_failures_average = \
            _np.inf if not self._usershift_failures_count\
            else self._usershift_progmd_time/self._usershift_failures_count

        # # # ----- distortions -----
        self._usershift_total_unstable_beam_time = _np.sum(
            dtimes_distortions_users)

        _, _, count = self._calc_interval_stats(
            self._distortions_users, dtimes_distortions_users)
        self._usershift_unstable_beam_count = count

        self._usershift_time_between_unstable_beams_average = \
            _np.inf if not self._usershift_unstable_beam_count\
            else self._usershift_progmd_time / \
            self._usershift_unstable_beam_count

        self._usershift_total_stable_beam_time = _np.sum(dtimes_users_stable)
        self._usershift_relative_stable_beam_time = \
            0.0 if not self._usershift_progmd_time else 100 * \
            self._usershift_total_stable_beam_time/self._usershift_progmd_time

        # # # ----- reliability -----
        self._usershift_beam_reliability = \
            0.0 if not self._usershift_progmd_time else 100 * \
            self._usershift_delivd_time/self._usershift_progmd_time

        # # # ----- injection shift -----
        self._usershift_total_injection_time = _np.sum(dtimes_injection)

        ave, std, count = self._calc_interval_stats(
            self._inj_shift_values, dtimes_injection)
        self._usershift_injection_time_average = ave
        self._usershift_injection_time_stddev = std
        self._usershift_injection_count = count

        # # light source usage stats
        self._lsusage_machinestudy_time = _np.sum(dtimes_machinestudy)

        self._lsusage_commissioning_time = _np.sum(dtimes_commissioning)

        self._lsusage_conditioning_time = _np.sum(dtimes_conditioning)

        self._lsusage_maintenance_time = _np.sum(dtimes_maintenance)

        self._lsusage_user_time = self._usershift_progmd_time + \
            self._usershift_extra_time

        self._lsusage_total_time = \
            self._lsusage_machinestudy_time + \
            self._lsusage_commissioning_time + \
            self._lsusage_conditioning_time + \
            self._lsusage_maintenance_time + \
            self._lsusage_user_time

        self._lsusage_machinestudy_failures_time = _np.sum(
            dtimes_machinestudy*self._raw_data['Failures']['SubsystemsNOk'])

        self._lsusage_commissioning_failures_time = _np.sum(
            dtimes_commissioning*self._raw_data['Failures']['SubsystemsNOk'])

        self._lsusage_conditioning_failures_time = _np.sum(
            dtimes_conditioning*self._raw_data['Failures']['SubsystemsNOk'])

        self._lsusage_maintenance_failures_time = 0.0

        dtimes_failures_users_oper = dtimes*self._failures_users
        self._lsusage_user_failures_time = _np.sum(
            dtimes_failures_users_oper)

        for usage in ['machinestudy', 'commissioning', 'conditioning',
                      'maintenance', 'user']:
            fail_intvl = getattr(self, '_lsusage_'+usage+'_failures_time')
            total_intvl = getattr(self, '_lsusage_'+usage+'_time')
            oper_intvl = total_intvl - fail_intvl
            if total_intvl:
                setattr(self, '_lsusage_'+usage+'_operational_time',
                        oper_intvl)
                setattr(self, '_lsusage_'+usage+'_failures',
                        100*fail_intvl/total_intvl)
                setattr(self, '_lsusage_'+usage+'_operational',
                        100*oper_intvl/total_intvl)
            else:
                setattr(self, '_lsusage_'+usage+'_operational_time', 0.0)
                setattr(self, '_lsusage_'+usage+'_failures', 0.0)
                setattr(self, '_lsusage_'+usage+'_operational', 0.0)
            setattr(self, '_lsusage_'+usage,
                    100*total_intvl/self._lsusage_total_time)

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

                setattr(self, pname+'_time', _np.sum(dtimes_select))

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
            ['usershift_progmd_time', 'h'],
            ['usershift_delivd_time', 'h'],
            ['usershift_total_time', 'h'],
            ['usershift_extra_time', 'h'],
            ['usershift_progmd_count', ''],
            ['usershift_current_average', 'mA'],
            ['usershift_current_stddev', 'mA'],
            ['usershift_current_beg_average', 'mA'],
            ['usershift_current_beg_stddev', 'mA'],
            ['usershift_current_end_average', 'mA'],
            ['usershift_current_end_stddev', 'mA'],
            ['usershift_total_failures_time', 'h'],
            ['usershift_failures_count', ''],
            ['usershift_beam_dump_count', ''],
            ['usershift_time_to_recover_average', 'h'],
            ['usershift_time_to_recover_stddev', 'h'],
            ['usershift_time_between_failures_average', 'h'],
            ['usershift_beam_reliability', '%'],
            ['usershift_total_stable_beam_time', 'h'],
            ['usershift_total_unstable_beam_time', 'h'],
            ['usershift_unstable_beam_count', ''],
            ['usershift_time_between_unstable_beams_average', 'h'],
            ['usershift_relative_stable_beam_time', '%'],
            ['usershift_total_injection_time', 'h'],
            ['usershift_injection_count', ''],
            ['usershift_injection_time_average', 'h'],
            ['usershift_injection_time_stddev', 'h'],
        ]
        ppties_lsusage = [
            ['lsusage_total_time', 'h'],
            ['lsusage_machinestudy_failures_time', 'h'],
            ['lsusage_machinestudy_failures', '%'],
            ['lsusage_machinestudy_operational_time', 'h'],
            ['lsusage_machinestudy_operational', '%'],
            ['lsusage_machinestudy_time', 'h'],
            ['lsusage_machinestudy', '%'],
            ['lsusage_commissioning_failures_time', 'h'],
            ['lsusage_commissioning_failures', '%'],
            ['lsusage_commissioning_operational_time', 'h'],
            ['lsusage_commissioning_operational', '%'],
            ['lsusage_commissioning_time', 'h'],
            ['lsusage_commissioning', '%'],
            ['lsusage_conditioning_failures_time', 'h'],
            ['lsusage_conditioning_failures', '%'],
            ['lsusage_conditioning_operational_time', 'h'],
            ['lsusage_conditioning_operational', '%'],
            ['lsusage_conditioning_time', 'h'],
            ['lsusage_conditioning', '%'],
            ['lsusage_maintenance_failures_time', 'h'],
            ['lsusage_maintenance_failures', '%'],
            ['lsusage_maintenance_operational_time', 'h'],
            ['lsusage_maintenance_operational', '%'],
            ['lsusage_maintenance_time', 'h'],
            ['lsusage_maintenance', '%'],
            ['lsusage_user_failures_time', 'h'],
            ['lsusage_user_failures', '%'],
            ['lsusage_user_operational_time', 'h'],
            ['lsusage_user_operational', '%'],
            ['lsusage_user_time', 'h'],
            ['lsusage_user', '%'],
        ]
        ppties_storedcurrent = [
            ['current_machinestudy_singlebunch_average', 'mA'],
            ['current_machinestudy_singlebunch_stddev', 'mA'],
            ['current_machinestudy_singlebunch_time', 'h'],
            ['current_machinestudy_multibunch_average', 'mA'],
            ['current_machinestudy_multibunch_stddev', 'mA'],
            ['current_machinestudy_multibunch_time', 'h'],
            ['current_machinestudy_total_average', 'mA'],
            ['current_machinestudy_total_stddev', 'mA'],
            ['current_machinestudy_total_time', 'h'],
            ['current_commissioning_singlebunch_average', 'mA'],
            ['current_commissioning_singlebunch_stddev', 'mA'],
            ['current_commissioning_singlebunch_time', 'h'],
            ['current_commissioning_multibunch_average', 'mA'],
            ['current_commissioning_multibunch_stddev', 'mA'],
            ['current_commissioning_multibunch_time', 'h'],
            ['current_commissioning_total_average', 'mA'],
            ['current_commissioning_total_stddev', 'mA'],
            ['current_commissioning_total_time', 'h'],
            ['current_conditioning_singlebunch_average', 'mA'],
            ['current_conditioning_singlebunch_stddev', 'mA'],
            ['current_conditioning_singlebunch_time', 'h'],
            ['current_conditioning_multibunch_average', 'mA'],
            ['current_conditioning_multibunch_stddev', 'mA'],
            ['current_conditioning_multibunch_time', 'h'],
            ['current_conditioning_total_average', 'mA'],
            ['current_conditioning_total_stddev', 'mA'],
            ['current_conditioning_total_time', 'h'],
            ['current_user_singlebunch_average', 'mA'],
            ['current_user_singlebunch_stddev', 'mA'],
            ['current_user_singlebunch_time', 'h'],
            ['current_user_multibunch_average', 'mA'],
            ['current_user_multibunch_stddev', 'mA'],
            ['current_user_multibunch_time', 'h'],
            ['current_user_total_average', 'mA'],
            ['current_user_total_stddev', 'mA'],
            ['current_user_total_time', 'h'],
            ['current_ebeam_singlebunch_average', 'mA'],
            ['current_ebeam_singlebunch_stddev', 'mA'],
            ['current_ebeam_singlebunch_time', 'h'],
            ['current_ebeam_multibunch_average', 'mA'],
            ['current_ebeam_multibunch_stddev', 'mA'],
            ['current_ebeam_multibunch_time', 'h'],
            ['current_ebeam_total_average', 'mA'],
            ['current_ebeam_total_stddev', 'mA'],
            ['current_ebeam_total_time', 'h'],
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
