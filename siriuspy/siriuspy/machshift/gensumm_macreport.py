"""Test."""

from matplotlib import pyplot as plt
import numpy as np
from siriuspy.clientarch.time import Time
from siriuspy.machshift.macreport import MacReport

# failure statistics per month
intervals = [
    [Time(2023, 1, 1, 0, 0), Time(2023, 1, 31, 23, 59, 59)],
    [Time(2023, 2, 1, 0, 0), Time(2023, 2, 28, 23, 59, 59)],
    [Time(2023, 3, 1, 0, 0), Time(2023, 3, 31, 23, 59, 59)],
    [Time(2023, 4, 1, 0, 0), Time(2023, 4, 30, 23, 59, 59)],
    [Time(2023, 5, 1, 0, 0), Time(2023, 5, 31, 23, 59, 59)],
    [Time(2023, 6, 1, 0, 0), Time(2023, 6, 30, 23, 59, 59)],
    [Time(2023, 7, 1, 0, 0), Time(2023, 7, 31, 23, 59, 59)],
    [Time(2023, 8, 1, 0, 0), Time(2023, 8, 31, 23, 59, 59)],
    [Time(2023, 9, 1, 0, 0), Time(2023, 9, 30, 23, 59, 59)],
    [Time(2023, 10, 1, 0, 0), Time(2023, 10, 31, 23, 59, 59)],
    [Time(2023, 11, 1, 0, 0), Time(2023, 11, 30, 23, 59, 59)],
    [Time(2023, 12, 1, 0, 0), Time(2023, 12, 31, 23, 59, 59)],
]

macreports = dict()
for intvl in intervals:
    macreports[intvl[0]] = MacReport()
    macreports[intvl[0]].connector.timeout = 30
    macreports[intvl[0]].time_start = intvl[0]
    macreports[intvl[0]].time_stop = intvl[1]
    macreports[intvl[0]].update()

mtbfs, mttrs, reliabs = dict(), dict(), dict()
progrmd, delivd, usertot = dict(), dict(), dict()
currmean, currstd = dict(), dict()
stable, unstable, relstable = dict(), dict(), dict()
nrbeamdump = dict()
for date, macr in macreports.items():
    mtbfs[date] = macr.usershift_time_between_failures_average
    mttrs[date] = macr.usershift_time_to_recover_average
    reliabs[date] = macr.usershift_beam_reliability
    progrmd[date] = macr.usershift_progmd_time
    delivd[date] = macr.usershift_delivd_time
    usertot[date] = macr.usershift_total_time
    currmean[date] = macr.usershift_current_average
    currstd[date] = macr.usershift_current_stddev
    stable[date] = macr.usershift_total_stable_beam_time
    unstable[date] = macr.usershift_total_unstable_beam_time
    relstable[date] = macr.usershift_relative_stable_beam_time
    nrbeamdump[date] = macr.usershift_beam_dump_count

str_ = '{:<10s}' + '{:>16s}'*10 + '{:>20s}'
print(str_.format(
    'Y-M', 'MTBF', 'MTTR',
    'Reliability', 'Progrmd hours', 'Delivd hours', 'Total hours',
    '% stable hours', 'Stable hours', 'Unstable hours', '# Beam Dump',
    'Current (Avg±Std)'))
str_ = '{:<10s}' + '    {:>12.3f}'*10 + '    {:4.3f} ± {:4.3f}'
for date in macreports:
    print(str_.format(
        str(date.year)+'-'+str(date.month),
        mtbfs[date],
        mttrs[date],
        reliabs[date],
        progrmd[date],
        delivd[date],
        usertot[date],
        relstable[date],
        stable[date],
        unstable[date],
        nrbeamdump[date],
        currmean[date], currstd[date],
    ))

fig, axs = plt.subplots(3, 1, sharex=True)
fig.set_size_inches(9, 6)
fig.subplots_adjust(top=0.96, left=0.08, bottom=0.05, right=0.96)
axs[0].xaxis.axis_date()
axs[0].plot(mtbfs.keys(), mtbfs.values(), '-b')
axs[0].plot(mtbfs.keys(), mtbfs.values(), 'ob')
axs[0].set_title('MTBF')
axs[0].grid()
axs[1].xaxis.axis_date()
axs[1].plot(mttrs.keys(), mttrs.values(), '-r')
axs[1].plot(mttrs.keys(), mttrs.values(), 'or')
axs[1].set_title('MTTR')
axs[1].grid()
axs[2].xaxis.axis_date()
axs[2].plot(reliabs.keys(), reliabs.values(), '-g')
axs[2].plot(reliabs.keys(), reliabs.values(), 'og')
axs[2].set_title('Reliability')
axs[2].grid()
fig.show()

# programmed vs. delivered hours
macr = MacReport()
macr.connector.timeout = 300
macr.time_start = Time(2023, 1, 1, 0, 0)
macr.time_stop = Time(2023, 12, 31, 23, 59, 59)
macr.update()

str_ = '{:<10s}' + '{:>16s}'*10 + '{:>20s}'
print(str_.format(
    'Y-M', 'MTBF', 'MTTR',
    'Reliability', 'Progrmd hours', 'Delivd hours', 'Total hours',
    '% stable hours', 'Stable hours', 'Unstable hours', '# Beam Dump',
    'Current (Avg±Std)'))
str_ = '{:<10s}' + '    {:>12.3f}'*10 + '    {:4.3f} ± {:4.3f}'
print(
    str_.format(
        str(macr.time_start.year)+'-'+str(macr.time_start.month) + ' a ' +
        str(macr.time_stop.year)+'-'+str(macr.time_stop.month),
        macr.usershift_time_between_failures_average,
        macr.usershift_time_to_recover_average,
        macr.usershift_beam_reliability,
        macr.usershift_progmd_time,
        macr.usershift_delivd_time,
        macr.usershift_total_time,
        macr.usershift_relative_stable_beam_time,
        macr.usershift_total_stable_beam_time,
        macr.usershift_total_unstable_beam_time,
        macr.usershift_beam_dump_count,
        macr.usershift_current_average,
        macr.usershift_current_stddev,
    ))

rd = macr.raw_data
dtimes = np.diff(rd['Timestamp'])
dtimes = np.r_[dtimes, dtimes[-1]]
dtimes = dtimes/60/60

dates = [Time(d) for d in rd['Timestamp']]

dtimes_users_progmd = dtimes*rd['UserShiftProgmd']
cum_progmd = np.cumsum(dtimes_users_progmd)
dtimes_users_impltd = dtimes*rd['UserShiftDelivd']
cum_deliv = np.cumsum(dtimes_users_impltd)

fig = plt.figure()
axs = plt.gca()
axs.xaxis.axis_date()
axs.plot(dates, cum_progmd, '-', label='Programmed')
axs.plot(dates, cum_deliv, '-', label='Delivered')
axs.grid()
axs.set_ylabel('Integrated Hours')
plt.legend(loc=4)
plt.title('Integrated User Hours')
fig.show()
