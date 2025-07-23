
import numpy as np
import pandas as pd
from siriuspy.clientarch.time import Time
from siriuspy.machshift.macreport import MacReport

# determine interval
time_start = Time(2023, 1, 1, 0, 0)
time_stop = Time(2023, 12, 31, 23, 59, 59)

# get data from interval
macr = MacReport()
macr.connector.timeout = 300
macr.time_start = time_start
macr.time_stop = time_stop
macr.update()

# print small report
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

# get data of interest
raw_data = macr.raw_data.copy()
raw_data.pop('Shift')
raw_data.pop('EgunModes')
raw_data.pop('Distortions')
raw_data.pop('UserShiftTotal')
raw_data.pop('UserShiftStable')
failures = raw_data.pop('Failures')
raw_data['Failures - SubsystemsNOk'] = np.asarray(failures['SubsystemsNOk'], dtype=int)
raw_data['Failures - NoEBeam'] = np.asarray(failures['NoEBeam'], dtype=int)
raw_data['Failures - WrongShift'] = np.asarray(failures['WrongShift'], dtype=int)
raw_data['Failures - ManualAnnotated'] = np.asarray(failures['ManualAnnotated'], dtype=int)
raw_data['TimeDate'] = [Time(t).get_iso8601() for t in raw_data['Timestamp']]

# stored data in specific order
order = [
    'Timestamp', 'TimeDate', 'Current',
    'Failures - SubsystemsNOk', 'Failures - NoEBeam',
    'Failures - WrongShift', 'Failures - ManualAnnotated',
    'UserShiftProgmd', 'UserShiftInitCurr', 'UserShiftDelivd']
data = {k: raw_data[k] for k in order}

# save data to csv
df = pd.DataFrame.from_dict(data)
df.to_csv('raw_data_machine_report_2023.csv', index=False, header=True)

# check hour numbers: each point is equivalent to 5s, converting to hours
programmed = sum(data['UserShiftProgmd'])*5/60/60
delivered = sum(data['UserShiftDelivd'])*5/60/60
print('Programmed hours:', programmed)
print('Delivered hours:', delivered)
