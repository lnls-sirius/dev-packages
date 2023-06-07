import numpy as np
import matplotlib.pyplot as mplt
from siriuspy.clientarch import PVDataSet, Time


def fit_pol(x, y, deg=1, polyfit=False):
    # handle big timestamps
    x = x - x[-1]
    # considering y = b + ax
    if polyfit:
        (a, b), cov = np.polyfit(x, y, deg=deg, cov=True)
        db_sqr, da_sqr = np.diag(cov)
    else:
        (b, a), details = np.polynomial.polynomial.polyfit(x, y, deg=deg, full=True)

        residues = details[0]

        lhs = np.polynomial.polynomial.polyvander(x, order-1)
        scale = np.sqrt((lhs*lhs).sum(axis=0))

        lhs /= scale
        lhs_inv = np.linalg.inv(np.dot(lhs.T, lhs))
        lhs_inv /= np.outer(scale, scale)

        cov = lhs_inv * (residues/(lhs.shape[0] - order))

        da_sqr, db_sqr = np.diag(cov)

    lt = - b / a
    dlt_sqr_rel = da_sqr/a/a + db_sqr/b/b
    dlt = np.sqrt(dlt_sqr_rel)*np.abs(lt)

    return a, np.sqrt(da_sqr), b, np.sqrt(db_sqr), lt, dlt


# datasets
dataset = {
    0: {
        'title': '2023-01-23, 6-8h, N~4000',
        't_start': Time(2023, 1, 23, 6, 0, 0),
        't_stop': Time(2023, 1, 23, 8, 0, 0),
        'nrpts_fit': 4000,
        'lt_ylim': [0, 100],
        'err_ylim': [0, 1.0],
    },
    1: {
        'title': '2023-01-23, 10-11h',
        't_start': Time(2023, 1, 23, 10, 0, 0),
        't_stop': Time(2023, 1, 23, 11, 0, 0),
        'nrpts_fit': 200,
        'lt_ylim': [0, 100],
        'err_ylim': [0, 1.0],
    },
    2: {
        'title': '2023-01-23, 12h30-12h35',
        't_start': Time(2023, 1, 23, 12, 30, 0),
        't_stop': Time(2023, 1, 23, 12, 35, 0),
        'nrpts_fit': 200,
        'lt_ylim': [0, 200],
        'err_ylim': [-100.0, 100.0],
    },
    3: {
        'title': '2023-01-23, 18h35-19h25',
        't_start': Time(2023, 1, 23, 18, 35, 0),
        't_stop': Time(2023, 1, 23, 19, 25, 0),
        'nrpts_fit': 4000,
        'lt_ylim': [0, 100],
        'err_ylim': [0, 1.0],
    },
    4: {
        'title': '2023-02-08 8h15-20h',
        't_start': Time(2023, 2, 8, 8, 15, 0),
        't_stop': Time(2023, 2, 8, 20, 0, 0),
        'nrpts_fit': 500,
        'lt_ylim': [0, 100],
        'err_ylim': [0, 1.0],
    },
    5: {
        'title': '2023-02-14 16h-16h30',
        't_start': Time(2023, 2, 14, 16, 0, 0),
        't_stop': Time(2023, 2, 14, 16, 30, 0),
        'nrpts_fit': 1000,
        'lt_ylim': [0, 100],
        'err_ylim': [0, 1.0],
    },
}


pvnames = [
    'SI-Glob:AP-CurrInfo:Lifetime-Mon',
    'SI-Glob:AP-CurrInfo:Current-Mon'
]
pvds = PVDataSet(pvnames)
pvds.timeout = 30

# for setid in dataset:
setid = 0

# get archiver data
pvds.time_start = dataset[setid]['t_start']
pvds.time_stop = dataset[setid]['t_stop']
pvds.update()

ycurr = np.asarray(pvds['SI-Glob:AP-CurrInfo:Current-Mon'].value)
dcurr = np.hstack([0, np.diff(ycurr)])
xcurr = np.asarray(pvds['SI-Glob:AP-CurrInfo:Current-Mon'].timestamp)
xcudt = [Time(t) for t in xcurr]
yltim = np.asarray(pvds['SI-Glob:AP-CurrInfo:Lifetime-Mon'].value)
xltim = np.asarray(pvds['SI-Glob:AP-CurrInfo:Lifetime-Mon'].timestamp)
xltdt = [Time(t) for t in xltim]
thres = 0.01

# fit lifetime and errors
lenb = dataset[setid]['nrpts_fit']  # [#]
order = 2
ltfit, lterr = [], []
for i in range(lenb, len(ycurr)):
    slc = slice(i-lenb, i)
    idx = np.where(dcurr[slc] > thres)[0]
    if idx.size:
        slc = slice(idx[-1], i)
    data = fit_pol(xcurr[slc], ycurr[slc], deg=order-1, polyfit=True)
    ltfit.append(data[4])
    lterr.append(data[5]/data[4])
ltfit, lterr = np.asarray(ltfit), np.asarray(lterr)

# plot
fig, ax = mplt.subplots()
fig.subplots_adjust(right=0.75)
tkw = dict(size=4, width=1.5)

ax.set_title(dataset[setid]['title'] + ', N~' + str(lenb))
ax.set_xlabel('Time [s]')
ax.tick_params(axis='x', **tkw)
ax.xaxis.axis_date()

ax.set_ylabel('Current [mA]')
p, = ax.plot(xcudt, ycurr, 'b', label='Current')
ax.tick_params(axis='y', colors=p.get_color(), **tkw)
ax.yaxis.label.set_color(p.get_color())

axlt = ax.twinx()
axlt.set_ylabel('Lifetime [h]')
po, = axlt.plot(xltdt, yltim/60/60, 'g', label='Lifetime Orig')
pf, = axlt.plot(xcudt[lenb:], ltfit/60/60, 'r', label='Lifetime Fit')
axlt.yaxis.label.set_color(po.get_color())
axlt.tick_params(axis='y', colors=po.get_color(), **tkw)
axlt.set_ylim(dataset[setid]['lt_ylim'])

axerr = ax.twinx()
axerr.set_ylabel('Lifetime Fit Rel. Error')
axerr.spines['right'].set_position(("axes", 1.2))
p, = axerr.plot(xcudt[lenb:], lterr, 'k', label='Lifetime Fit Error')
axerr.yaxis.label.set_color(p.get_color())
axerr.tick_params(axis='y', colors=p.get_color(), **tkw)
axerr.set_ylim(dataset[setid]['err_ylim'])

fig.legend()
fig.show()
