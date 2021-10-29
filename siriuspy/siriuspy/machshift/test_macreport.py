"""Test."""

from matplotlib import pyplot as plt
import numpy as np
from siriuspy.clientarch.time import Time
from siriuspy.machshift.utils import MacReport

# failure statistics per month
intervals = [
    [Time(2020, 7, 1, 0, 0), Time(2020, 7, 30, 23, 59)],
    [Time(2020, 8, 1, 0, 0), Time(2020, 8, 31, 23, 59)],
    [Time(2020, 9, 1, 0, 0), Time(2020, 9, 30, 23, 59)],
    [Time(2020, 10, 1, 0, 0), Time(2020, 10, 31, 23, 59)],
    [Time(2020, 11, 1, 0, 0), Time(2020, 11, 30, 23, 59)],
    [Time(2020, 12, 1, 0, 0), Time(2020, 12, 31, 23, 59)],
    [Time(2021, 1, 1, 0, 0), Time(2021, 1, 31, 23, 59)],
    [Time(2021, 2, 1, 0, 0), Time(2021, 2, 28, 23, 59)],
    [Time(2021, 3, 1, 0, 0), Time(2021, 3, 31, 23, 59)],
    [Time(2021, 4, 1, 0, 0), Time(2021, 4, 30, 23, 59)],
    [Time(2021, 5, 1, 0, 0), Time(2021, 5, 31, 23, 59)],
    [Time(2021, 6, 1, 0, 0), Time(2021, 6, 30, 23, 59)],
]

macreports = dict()
for intvl in intervals:
    macreports[intvl[0]] = MacReport()
    macreports[intvl[0]].connector.timeout = 30
    macreports[intvl[0]].time_start = intvl[0]
    macreports[intvl[0]].time_stop = intvl[1]
    macreports[intvl[0]].update()

mtbfs, mttrs, reliabs = dict(), dict(), dict()
for date, macr in macreports.items():
    mtbfs[date] = macr.time_between_failures_average
    mttrs[date] = macr.time_to_recover_average
    reliabs[date] = macr.beam_reliability

str_ = '{:<10s}    {:<7s}    {:<7s}    {:<7s}'
print(str_.format('M/Y', 'MTBF', 'MTTR', 'Reliability'))
str_ = '{:<10s}    {:<3.3f}    {:<3.3f}    {:<3.3f}'
for date in macreports:
    print(str_.format(str(date.year)+'-'+str(date.month),
                      mtbfs[date],
                      mttrs[date],
                      reliabs[date]))

fig, axs = plt.subplots(3, 1, sharex=True)
fig.set_size_inches(9, 6)
fig.subplots_adjust(top=0.96, left=0.08, bottom=0.05, right=0.96)
axs[0].plot_date(mtbfs.keys(), mtbfs.values(), '-b')
axs[0].plot_date(mtbfs.keys(), mtbfs.values(), 'ob')
axs[0].set_title('MTBF')
axs[0].grid()
axs[1].plot_date(mttrs.keys(), mttrs.values(), '-r')
axs[1].plot_date(mttrs.keys(), mttrs.values(), 'or')
axs[1].set_title('MTTR')
axs[1].grid()
axs[2].plot_date(reliabs.keys(), reliabs.values(), '-g')
axs[2].plot_date(reliabs.keys(), reliabs.values(), 'og')
axs[2].set_title('Reliability')
axs[2].grid()
fig.show()

# programmed vs. delivered hours
macr = MacReport()
macr.connector.timeout = 120
macr.time_start = Time(2020, 7, 1, 0, 0)
macr.time_stop = Time(2021, 6, 30, 23, 59)
macr.update()

rd = macr.raw_data
dtimes = np.diff(rd['Timestamp'])
dtimes = np.r_[dtimes, dtimes[-1]]
dtimes = dtimes/60/60

dates = [Time(d) for d in rd['Timestamp']]

dtimes_users_progmd = dtimes*rd['UserShiftProgmd']
cum_progmd = np.cumsum(dtimes_users_progmd)
dtimes_users_impltd = dtimes*rd['UserShiftImpltd']
cum_deliv = np.cumsum(dtimes_users_impltd)

fig = plt.figure()
axs = plt.gca()
axs.plot_date(dates, cum_progmd, '-', label='Programmed')
axs.plot_date(dates, cum_deliv, '-', label='Delivered')
axs.grid()
axs.set_ylabel('Integrated Hours')
plt.legend(loc=4)
plt.title('Integrated User Hours')
fig.show()

new_dates, new_dtimes_progmd, new_dtimes_deliv = [], [], []
for i, d in enumerate(dates):
    if not new_dates or d.date() != new_dates[-1].date():
        new_dates.append(d)
        new_dtimes_progmd.append(dtimes_users_progmd[i])
        new_dtimes_deliv.append(dtimes_users_impltd[i])
    else:
        new_dtimes_progmd[-1] += dtimes_users_progmd[i]
        new_dtimes_deliv[-1] += dtimes_users_impltd[i]
new_cum_progmd = np.cumsum(new_dtimes_progmd)
new_cum_deliv = np.cumsum(new_dtimes_deliv)

fig = plt.figure()
axs = plt.gca()
axs.plot_date(new_dates, new_cum_progmd, '-', label='Programmed')
axs.plot_date(new_dates, new_cum_deliv, '-', label='Delivered')
axs.grid()
axs.set_ylabel('Integrated Hours')
plt.legend(loc=4)
plt.title('Integrated User Hours')
fig.show()

np.savetxt('integrated_user_hours_2021.txt', np.c_[[d.timestamp() for d in new_dates], new_cum_progmd, new_cum_deliv])
