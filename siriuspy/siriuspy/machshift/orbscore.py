"""Orbit Score."""

import sys as _sys
import time as _time
import logging as _log

import numpy as _np
import numpy.polynomial.polynomial as _nppol
from matplotlib import pyplot as _plt

from ..clientarch import ClientArchiver as _CltArch, Time as _Time, \
    PVData as _PVData
from .csdev import Const as _Cte
from .macschedule import MacScheduleData as _MacScheduleData
from .utils import interp1d_previous as _interp1d_previous


class OrbitScore:
    """Orbit Score."""

    def __init__(self, connector=None, logger=None,
                 thold_isstored=None,
                 slowdrift_polyfit_deg=None,
                 slowdrift_tottime_goal=None,
                 slowdrift_conttime_goal=None,
                 slowdrift_thold=None,
                 slowdrift_ampli_goal=None,
                 meanpos_goal=None,
                 meanpos_thold=None,
                 slowdrift_tottime_weight=None,
                 slowdrift_conttime_weight=None,
                 slowdrift_ampli_weight=None,
                 meanpos_weight=None):
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

        # default params
        self._params = dict()
        self._params['thold_isstored'] = thold_isstored or 0.020  # [mA]
        self._params['slowdrift_polyfit_deg'] = slowdrift_polyfit_deg or 4
        self._params['slowdrift_thold'] = slowdrift_thold or 25000  # [counts]
        self._params['slowdrift_tottime_goal'] = \
            slowdrift_tottime_goal or 0.98  # [%]
        self._params['slowdrift_conttime_goal'] = \
            slowdrift_conttime_goal or 0.95  # [%]
        self._params['slowdrift_ampli_goal'] = \
            slowdrift_ampli_goal or 200000  # [counts]
        self._params['meanpos_goal'] = meanpos_goal or 4550000  # [counts]
        self._params['meanpos_thold'] = meanpos_thold or 100000  # [counts]

        # achieved
        self._achieved = dict()
        self._achieved['slowdrift_tottime'] = None
        self._achieved['slowdrift_conttime'] = None
        self._achieved['slowdrift_ampli'] = None
        self._achieved['meanpos'] = None

        # weights
        self._weights = dict()
        self._weights['slowdrift_tottime'] = slowdrift_tottime_weight or 5
        self._weights['slowdrift_conttime'] = slowdrift_conttime_weight or 5
        self._weights['slowdrift_ampli'] = slowdrift_ampli_weight or 2
        self._weights['meanpos'] = meanpos_weight or 1

        # scores
        self._scores = dict()
        self._scores['slowdrift_tottime'] = None
        self._scores['slowdrift_conttime'] = None
        self._scores['slowdrift_ampli'] = None
        self._scores['meanpos'] = None
        self._scores['total'] = None

        # aux vars
        self._raw_data = dict()
        self._curr_times = None
        self._curr_values = None
        self._user_shift_values = None
        self._pbpm_pos_values = None
        self._progmd_values = None
        self._is_stored_total = None
        self._valid_indices = None
        self._valid_values = None
        self._valid_times = None
        self._score_values = None

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

    # ----- parameters -----

    @property
    def thold_isstored(self):
        """Current threshold to check whether beam is stored."""
        return self._params['thold_isstored']

    @thold_isstored.setter
    def thold_isstored(self, value):
        self._params['thold_isstored'] = value
        self.calc_score()

    @property
    def slowdrift_polyfit_deg(self):
        """Slow drift polynomial fit degree."""
        return self._params['slowdrift_polyfit_deg']

    @slowdrift_polyfit_deg.setter
    def slowdrift_polyfit_deg(self, value):
        self._params['slowdrift_polyfit_deg'] = abs(int(value))
        self.calc_score()

    @property
    def slowdrift_thold(self):
        """Threshold to check whether orbit transients around
        slow drift are within tolerance."""
        return self._params['slowdrift_thold']

    @slowdrift_thold.setter
    def slowdrift_thold(self, value):
        self._params['slowdrift_thold'] = value
        self.calc_score()

    @property
    def slowdrift_tottime_goal(self):
        """Total relative time within a threshold window around
        slow drift [%] goal."""
        return self._params['slowdrift_tottime_goal']

    @slowdrift_tottime_goal.setter
    def slowdrift_tottime_goal(self, value):
        self._params['slowdrift_tottime_goal'] = value
        self.calc_score()

    @property
    def slowdrift_conttime_goal(self):
        """Max. cont. relative time within a threshold window around
        slow drift [%] goal."""
        return self._params['slowdrift_conttime_goal']

    @slowdrift_conttime_goal.setter
    def slowdrift_conttime_goal(self, value):
        self._params['slowdrift_conttime_goal'] = value
        self.calc_score()

    @property
    def slowdrift_ampli_goal(self):
        """Maximum slow drift threshold."""
        return self._params['slowdrift_ampli_goal']

    @slowdrift_ampli_goal.setter
    def slowdrift_ampli_goal(self, value):
        self._params['slowdrift_ampli_goal'] = value
        self.calc_score()

    @property
    def meanpos_goal(self):
        """Reference for orbit mean position."""
        return self._params['meanpos_goal']

    @meanpos_goal.setter
    def meanpos_goal(self, value):
        self._params['meanpos_goal'] = value
        self.calc_score()

    @property
    def meanpos_thold(self):
        """Threshold for orbit mean position around reference."""
        return self._params['meanpos_thold']

    @meanpos_thold.setter
    def meanpos_thold(self, value):
        self._params['meanpos_thold'] = value
        self.calc_score()

    # ----- scores weights -----

    @property
    def slowdrift_tottime_weight(self):
        """Weight of total relative time within a threshold window around
        slow drift [%]."""
        return self._weights['slowdrift_tottime']

    @slowdrift_tottime_weight.setter
    def slowdrift_tottime_weight(self, value):
        self._weights['slowdrift_tottime'] = abs(int(value))
        self.calc_score()

    @property
    def slowdrift_conttime_weight(self):
        """Weight of max. cont. relative time within a threshold window around
        slow drift [%]."""
        return self._weights['slowdrift_conttime']

    @slowdrift_conttime_weight.setter
    def slowdrift_conttime_weight(self, value):
        self._weights['slowdrift_conttime'] = abs(int(value))
        self.calc_score()

    @property
    def slowdrift_ampli_weight(self):
        """Slow drift amplitude score weight to calculate total score."""
        return self._weights['slowdrift_ampli']

    @slowdrift_ampli_weight.setter
    def slowdrift_ampli_weight(self, value):
        self._weights['slowdrift_ampli'] = abs(int(value))
        self.calc_score()

    @property
    def meanpos_weight(self):
        """Mean position score weight to calculate total score."""
        return self._weights['meanpos']

    @meanpos_weight.setter
    def meanpos_weight(self, value):
        self._weights['meanpos'] = abs(int(value))
        self.calc_score()

    # ----- achieved -----

    @property
    def slowdrift_tottime_achieved(self):
        """Total relative time within a threshold window around
        slow drift [%] achieved."""
        return self._achieved['slowdrift_tottime']

    @property
    def slowdrift_conttime_achieved(self):
        """Max. cont. relative time within a threshold window around
        slow drift [%] achieved."""
        return self._achieved['slowdrift_conttime']

    @property
    def slowdrift_ampli_achieved(self):
        """Value achieved for Slow Drift Amplitude score."""
        return self._achieved['slowdrift_ampli']

    @property
    def meanpos_achieved(self):
        """Value achieved for Mean Position score."""
        return self._achieved['meanpos']

    # ----- scores -----

    @property
    def slowdrift_tottime_score(self):
        """Total relative time within a threshold window around
        slow drift [%] score."""
        return self._scores['slowdrift_tottime']

    @property
    def slowdrift_conttime_score(self):
        """Max. cont. relative time within a threshold window around
        slow drift [%] score."""
        return self._scores['slowdrift_conttime']

    @property
    def slowdrift_ampli_score(self):
        """Slow Drift Amplitude score."""
        return self._scores['slowdrift_ampli']

    @property
    def meanpos_score(self):
        """Mean Position score."""
        return self._scores['meanpos']

    @property
    def total_score(self):
        """Total score."""
        return self._scores['total']

    def update(self):
        """Get data."""
        if self._time_start >= self._time_stop:
            raise ValueError('Invalid time interval.')

        for pvn in self._pvnames:
            self._pvdata[pvn].time_start = self._time_start
            self._pvdata[pvn].time_stop = self._time_stop

        self._update_log('Collecting archiver data...')

        log_msg = 'Query for {0} in archiver took {1:.3f}s'

        for pvn in self._pvnames:
            _t0 = _time.time()
            self._pvdata[pvn].update(parallel=False)
            self._update_log(log_msg.format(pvn, _time.time()-_t0))

        # current data
        self._curr_times, self._curr_values = \
            self._get_pv_data(self._current_pv)
        self._curr_values[self._curr_values < 0] = 0
        self._curr_values[self._curr_values > 500] = 0
        self._raw_data['Timestamp'] = self._curr_times
        self._raw_data['Current'] = self._curr_values

        # mac. schedule data
        self._progmd_values = _MacScheduleData.is_user_shift_programmed(
            timestamp=self._curr_times)
        self._raw_data['ProgmdShift'] = self._progmd_values

        # shift data
        shift_times, shift_values = \
            self._get_pv_data(self._macshft_pv)
        user_shift_values = _np.array(
            [1*(v == _Cte.MachShift.Users) for v in shift_values])
        self._user_shift_values = _interp1d_previous(
            shift_times, user_shift_values, self._curr_times)
        self._raw_data['IsUserShift'] = self._user_shift_values

        # pbpm pos data
        pbpm_times, pbpm_values = \
            self._get_pv_data(self._pbpmpos_pv)
        self._pbpm_pos_values = _interp1d_previous(
            pbpm_times, pbpm_values, self._curr_times)
        self._raw_data['PBPMPos'] = self._pbpm_pos_values

        self.calc_score()

    def calc_score(self):
        """Calculate scores using parameters."""
        if not self._raw_data:
            return

        # valid data
        self._raw_data['ValidData'] = dict()
        self._is_stored_total = \
            1*(self._curr_values > self._params['thold_isstored'])
        self._valid_indices = _np.where(
            self._user_shift_values * self._progmd_values *
            self._is_stored_total > 0)[0]
        self._valid_values = self._pbpm_pos_values[self._valid_indices]
        self._valid_times = self._curr_times[self._valid_indices]
        self._raw_data['ValidData']['Value'] = self._valid_values
        self._raw_data['ValidData']['Timestamp'] = self._valid_times

        if not self._valid_times.size:
            self._scores['slowdrift_tottime'] = 0.0
            self._achieved['slowdrift_tottime'] = 0.0
            self._achieved['slowdrift_conttime'] = 0.0
            self._scores['slowdrift_conttime'] = 0.0
            self._scores['slowdrift_ampli'] = 0.0
            self._achieved['slowdrift_ampli'] = 0.0
            self._achieved['meanpos'] = 0.0
            self._scores['meanpos'] = 0.0
            self._scores['total'] = 0.0
            return

        # fit
        self._raw_data['FitData'] = dict()
        fit_times = self._valid_times - self._valid_times[0]
        fit_poly = _nppol.polyfit(
            fit_times, self._valid_values,
            deg=self._params['slowdrift_polyfit_deg'])
        self._fit_values = _nppol.polyval(fit_times, fit_poly)
        self._raw_data['FitData']['Value'] = self._fit_values
        self._raw_data['FitData']['Timestamp'] = self._valid_times

        # score data
        self._raw_data['ScoreData'] = dict()
        self._score_values = self._valid_values - self._fit_values
        self._raw_data['ScoreData']['Value'] = self._score_values
        self._raw_data['ScoreData']['Timestamp'] = self._valid_times

        in_window = _np.zeros(self._curr_times.size)
        in_window[self._valid_indices] = 1*(
            abs(self._score_values) < self._params['slowdrift_thold'])

        tot_in_thold = _np.sum(in_window)/len(in_window)
        self._scores['slowdrift_tottime'] = tot_in_thold if \
            tot_in_thold < self._params['slowdrift_tottime_goal'] else 1.0
        self._achieved['slowdrift_tottime'] = tot_in_thold

        transitions = _np.diff(in_window)
        beg_idcs = _np.where(transitions == 1)[0]
        end_idcs = _np.where(transitions == -1)[0]
        if beg_idcs.size and end_idcs.size:
            if beg_idcs[0] > end_idcs[0]:
                end_idcs = end_idcs[1:]
            if beg_idcs.size > end_idcs.size:
                end_idcs = _np.r_[end_idcs, in_window.size-1]
            sts_values = [
                _np.sum(in_window[beg_idcs[i]:end_idcs[i]])
                for i in range(beg_idcs.size)]
            cont_in_thold = _np.max(sts_values)/len(in_window)
            self._achieved['slowdrift_conttime'] = cont_in_thold
            self._scores['slowdrift_conttime'] = cont_in_thold \
                if cont_in_thold < self._params['slowdrift_conttime_goal']\
                else 1.0
        else:
            self._achieved['slowdrift_conttime'] = tot_in_thold
            self._scores['slowdrift_conttime'] = \
                self._scores['slowdrift_tottime']

        slowdrift = self._fit_values.max() - self._fit_values.min()
        maxi = self._params['slowdrift_ampli_goal']
        self._scores['slowdrift_ampli'] = 1.0 if slowdrift <= maxi else \
            0.0 if slowdrift > 2*maxi else 2 - slowdrift/maxi
        self._achieved['slowdrift_ampli'] = slowdrift

        self._achieved['meanpos'] = self._valid_values.mean()
        diff = abs(self._achieved['meanpos'] - self._params['meanpos_goal'])
        maxi = self._params['meanpos_thold']
        self._scores['meanpos'] = 1.0 if diff <= maxi else \
            0.0 if diff > 2*maxi else 2 - diff/maxi

        scores_times_weights = [
            self._scores[k]*self._weights[k] for k in self._weights]
        self._scores['total'] = \
            _np.sum(scores_times_weights)/_np.sum(list(self._weights.values()))

    @property
    def raw_data(self):
        """Return raw data."""
        return self._raw_data.copy()

    def plot_raw_data(self):
        """Plot raw data for period timestamp_start to timestamp_stop."""
        if not self._raw_data:
            print('No data to display. Call update() to get data.')
            return

        datetimes = _np.array([_Time(t) for t in self._raw_data['Timestamp']])

        fig, axs = _plt.subplots(4, 1, sharex=True)
        fig.set_size_inches(9, 4)
        fig.subplots_adjust(top=0.92, left=0.08, bottom=0.08, right=0.92)
        axs[0].set_title('Raw data', fontsize=12)

        axs[0].plot_date(
            datetimes, self._raw_data['Current'], '-',
            color='blue', label='Current')
        axs[0].legend(loc='upper left', fontsize=9)
        axs[0].grid()

        axs[1].plot_date(
            datetimes, self._raw_data['ProgmdShift'], '-',
            color='gold', label='Programmed Shift')
        axs[1].legend(loc='upper left', fontsize=9)
        axs[1].grid()

        axs[2].plot_date(
            datetimes, self._raw_data['IsUserShift'], '-',
            color='gold', label='Delivered Shift')
        axs[2].legend(loc='upper left', fontsize=9)
        axs[2].grid()

        axs[3].plot_date(
            datetimes, self._raw_data['PBPMPos'], '-',
            color='green', label='PBPM Position')
        axs[3].legend(loc='upper left', fontsize=9)
        axs[3].grid()
        return fig, axs

    def plot_score_data(self):
        """Plot score data for period timestamp_start to timestamp_stop."""
        if not self._raw_data:
            print('No data to display. Call update() to get data.')
            return

        fig, axs = _plt.subplots(2, 1, sharex=True)
        fig.set_size_inches(9, 3)
        fig.subplots_adjust(top=0.92, left=0.08, bottom=0.08, right=0.92)
        axs[0].set_title('Score data', fontsize=12)

        dtval = _np.array(
            [_Time(t) for t in self._raw_data['ValidData']['Timestamp']])
        axs[0].plot_date(
            dtval, self._raw_data['ValidData']['Value'], '-',
            color='cyan', label='Valid Data')
        axs[0].plot_date(
            dtval, self._raw_data['FitData']['Value'], '-', linewidth=2,
            color='black', label='Slow Drift Fit')
        axs[0].axhline(
            y=self._params['meanpos_goal'], color='black', linestyle=':',
            label='Mean Pos. Goal')
        axs[0].axhline(
            y=self._achieved['meanpos'], color='blue', linestyle='--',
            label='Mean Pos. Achieved')
        axs[0].legend(loc='upper left', fontsize=9, ncol=2)
        axs[0].grid()

        dtval = _np.array(
            [_Time(t) for t in self._raw_data['ScoreData']['Timestamp']])
        axs[1].plot_date(
            dtval, self._raw_data['ScoreData']['Value'], '-',
            color='cyan', label='Valid Data - Slow Drift Fit')
        axs[1].axhline(
            y=-self._params['slowdrift_thold'], color='black', linestyle='--')
        axs[1].axhline(
            y=self._params['slowdrift_thold'], color='black', linestyle='--')
        axs[1].legend(loc='upper left', fontsize=9)
        axs[1].grid()
        return fig, axs

    # ----- auxiliary methods -----

    def _init_connectors(self):
        self._pbpmpos_pv = 'SI-10BCFE:DI-PBPM-1:PosY-Mon'
        self._current_pv = 'SI-Glob:AP-CurrInfo:Current-Mon'
        self._macshft_pv = 'AS-Glob:AP-MachShift:Mode-Sts'
        self._pvnames = [
            self._pbpmpos_pv, self._current_pv, self._macshft_pv]

        self._pvdata = dict()
        self._pv2default = dict()

        for pvname in self._pvnames:
            self._pvdata[pvname] = _PVData(pvname, self._connector)
            self._pv2default[pvname] = 0.0 if 'MachShift' in pvname \
                else _Cte.MachShift.Commissioning

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
            if times[0] > t_start:
                times = _np.r_[t_start, times]
                values = _np.r_[defv, values]
        return times, values

    def _update_log(self, message=''):
        self._logger_message = message
        if self._logger:
            self._logger.update(message)
        _log.info(message)

    # ----- magic methods -----

    def __getitem__(self, pvname):
        return self._pvdata[pvname]

    def __str__(self):
        rst = ''
        rst += 'Parameters\n'
        params = [
            ['Description', 'Value'],
            ['Stored beam threshold current [mA]',
             self._params['thold_isstored']],
            ['Slow Drift polynomial fit degree',
             self._params['slowdrift_polyfit_deg']],
        ]
        for desc, value in params:
            if isinstance(value, str):
                fst = '{0:35s}| {1:5s}\n'
            else:
                fst = '{0:>35s}| {1:>5.3f}\n'
            rst += fst.format(desc, value)
        rst += '\n'
        rst += 'Scores\n'
        scores = [
            ['Weight', 'Description', 'Goal', 'Achieved', 'Score'],
            ['{}'.format(self._weights['slowdrift_tottime']),
             'Total time in a ±{}counts window around '
             'slow drift [%]'.format(self._params['slowdrift_thold']),
             '{:>2.2f}'.format(100*self._params['slowdrift_tottime_goal']),
             100*self._achieved['slowdrift_tottime'],
             self._scores['slowdrift_tottime']],
            ['{}'.format(self._weights['slowdrift_conttime']),
             'Max.cont. time in a ±{}counts window around '
             'slow drift [%]'.format(self._params['slowdrift_thold']),
             '{:>2.2f}'.format(100*self._params['slowdrift_conttime_goal']),
             100*self._achieved['slowdrift_conttime'],
             self._scores['slowdrift_conttime']],
            ['{}'.format(self._weights['slowdrift_ampli']),
             'Slow Drift Amplitude [counts]',
             '{}'.format(self._params['slowdrift_ampli_goal']),
             self._achieved['slowdrift_ampli'],
             self._scores['slowdrift_ampli']],
            ['{}'.format(self._weights['meanpos']),
             'Mean Orbit Position (threshold {}) [counts]'.format(
                 self._params['meanpos_thold']),
             '{}'.format(self._params['meanpos_goal']),
             self._achieved['meanpos'],
             self._scores['meanpos']],
        ]
        for weight, desc, goal, achieved, value in scores:
            if isinstance(value, str):
                fst = '{0:<6s} | {1:<62s} | {2:7s} | {3:10s} | {4:5s}\n'
            else:
                fst = '{0:<6s} | {1:>62s} | {2:>7s} | {3:>10.2f} | {4:>5.2f}\n'
            rst += fst.format(weight, desc, goal, achieved, value)
        rst += '\n'
        rst += 'Total: {}'.format(self._scores['total'])
        return rst
