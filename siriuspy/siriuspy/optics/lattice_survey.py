"""Lattice survey module."""

import pyaccel
import pymodels
from ..namesys import join_name as _join_name, SiriusPVName as _PVName
from ..clientweb import crates_mapping as _crates_mapping


def run_all():
    """."""
    generate_bpm_static_table()
    generate_model_static_table()


def generate_model_static_table():
    """."""
    disclaimer = \
        "# This file was generated automatically from the data of the \n"\
        "# models of the accelerators in the pymodels repository by the \n"\
        "# function: \n"\
        "#    siriuspy.optics.lattice_survey.generate_model_static_table.\n"\
        "#\n"\
        "# If any model change, please, run the script\n"\
        "# again and copy the generated file to replace this one.\n"

    filename = 'magnets-model-data.txt'

    with open(filename, 'w') as f:
        f.write(disclaimer)
        f.write('\n\n#Magnets data \n')
        f.write('#-----------')

    model = pymodels.si
    acc = model.create_accelerator()
    _append_mag_data(filename, model, acc, 'Storage Ring (SI)', 'SI')

    model = pymodels.bo
    acc = model.create_accelerator()
    ind = pyaccel.lattice.find_indices(acc, 'fam_name', 'InjSept')
    acc = pyaccel.lattice.shift(acc, ind[0])
    _append_mag_data(filename, model, acc, 'Booster (BO)', 'BO')

    model = pymodels.tb
    acc, *_ = model.create_accelerator(add_from_li_triplets=False)
    _append_mag_data(
        filename, model, acc, 'Booster Transport Line (TB)', 'TB')

    model = pymodels.ts
    acc, *_ = model.create_accelerator()
    _append_mag_data(filename, model, acc, 'SR Transport Line (TS)', 'TS')


def _conv_dev_inst(section, sub, mag_tp, inst):
    inst_conv = {
        # additional correctors were added in TS
        'TS-01': {
            'CV': {'2': ('CV', '1E2'), '3': ('CV', '2')},
            },
        'TS-02': {
            'CV': {'1': ('CV', '0'), '2': ('CV', '')},
            },
        'TS-04': {
            'CV': {
                '1': ('CV', '0'), '2': ('CV', '1'),
                '3': ('CV', '1E2'), '4': ('CV', '2')},
            },
        # TB skew quad in the model converted to ch
        'TB-04': {
            'CH': {'1': ('CH', '')},
            'CH': {'2': ('QS', '')},
            },
        'TB-04': {
            'CH': {'': ('CH', '1')},
            'QS': {'': ('CH', '2')},
            },
        }
    secsub = section + '-' + sub
    inst_conv_ = inst_conv
    if secsub in inst_conv_:
        inst_conv_ = inst_conv_[secsub]
        if mag_tp in inst_conv_:
            inst_conv_ = inst_conv_[mag_tp]
            if inst in inst_conv_:
                return inst_conv_[inst]
    return mag_tp, inst


def _conv_id_correctors(mag_tp):
    if mag_tp in ('IDCH', 'IDCV', 'IDQS'):
        # NOTE: this would issue wrong instances if there were
        # other CH or CV magnets in insertion device straights, which
        # is not the case.
        mag_tp = mag_tp[2:]
    return mag_tp


def _conv_pulsed_magnets(mag_tp, dis):
    if 'Inj' in mag_tp or 'Eje' in mag_tp or 'Ping' in mag_tp:
        dis = 'PM'
    return dis


def _append_mag_data(filename, model, acc, label, section):
    fam_data = model.get_family_data(acc)
    pos = pyaccel.lattice.find_spos(acc)

    args = (acc, ) if model == pymodels.tb else ()
    mag_tps = []
    mag_tps.extend(model.families.families_dipoles(*args))
    mag_tps.extend(model.families.families_pulsed_magnets(*args))
    mag_tps.extend(model.families.families_quadrupoles(*args))
    mag_tps.extend(model.families.families_horizontal_correctors(*args))
    mag_tps.extend(model.families.families_vertical_correctors(*args))
    mag_tps.extend(model.families.families_sextupoles(*args))
    mag_tps.extend(model.families.families_skew_correctors(*args))

    mag_data = dict()
    for mag_tp in mag_tps:
        inds = fam_data[mag_tp]['index']
        subs = fam_data[mag_tp]['subsection']
        insts = fam_data[mag_tp]['instance']
        for ind, inst, sub in zip(inds, insts, subs):
            val = (pos[ind[-1]+1] + pos[ind[0]]) / 2  # elem position
            # special conversions
            mag_tp_, inst_, dis_ = mag_tp, inst, 'MA'
            mag_tp_ = _conv_id_correctors(mag_tp_)
            dis_ = _conv_pulsed_magnets(mag_tp_, dis_)
            mag_tp_, inst_ = _conv_dev_inst(section, sub, mag_tp_, inst_)
            name = _join_name(
                sec=section, dis=dis_, dev=mag_tp_, sub=sub, idx=inst_)
            mag_data[name] = val

    # order by spos
    mags = list(mag_data.keys())
    mpos = list(mag_data.values())
    mpos, mags = zip(*sorted(zip(mpos, mags)))

    with open(filename, 'a') as f:
        f.write('\n\n\n# '+label+'\n')
        f.write('#'+57*'-' + '\n')
        f.write("#{mag:20s} {pos:^20s}\n".format(
            mag='Name', pos='Position @ center [m]'))
        f.write('#'+57*'-' + '\n')
        for mag, pos in zip(mags, mpos):
            f.write(f'{mag:20s} {pos:>20.4f}\n')


def generate_bpm_static_table():
    """."""
    disclaimer = \
        "# This file was generated automatically from the data of the files\n"\
        "# in the subfolder Mapeamento_placas_MicroTCA_vs_BPMs and the\n"\
        "# models of the accelerators in the pymodels repository by the\n"\
        "# function: \n"\
        "#      siriuspy.optics.lattice_survey.generate_bpm_static_table.\n"\
        "#\n"\
        "# If the data in the mentioned subfolder change, please, run the\n"\
        "# script again and copy the generated file to replace this one.\n"

    filename = 'bpms-data.txt'
    with open(filename, 'w') as f:
        f.write(disclaimer)
        f.write('\n\n#BPMs data \n')
        f.write('#-----------')

    all_bpms = _get_all_bpms()

    model = pymodels.si
    acc = model.create_accelerator()
    _append_bpm_data_bl(filename, acc, all_bpms, 'Beam Lines (BL)')
    label = 'Storage Ring (SR)'
    _append_bpm_data(filename, model, acc, label, 'SI', fam='BPM')
    label = 'Storage Ring IDs (SR)'
    _append_bpm_data(filename, model, acc, label, 'SI', fam='IDBPM')

    model = pymodels.bo
    acc = model.create_accelerator()
    _append_bpm_data(filename, model, acc, 'Booster (BO)', 'BO')

    model = pymodels.tb
    acc, *_ = model.create_accelerator()
    idx = pyaccel.lattice.find_indices(acc, 'fam_name', 'Spect')[0]
    acc = acc[idx+1:]
    _append_bpm_data(filename, model, acc, 'BO Transport Line', 'TB')

    model = pymodels.ts
    acc, *_ = model.create_accelerator()
    _append_bpm_data(filename, model, acc, 'SR Transport Line', 'TS')


def _append_bpm_data(filename, model, acc, label, section, fam='BPM'):
    fam_data = model.get_family_data(acc)
    pos = pyaccel.lattice.find_spos(acc)

    bpm_data = fam_data[fam]
    inds = [i[0] for i in bpm_data['index']]
    subs = bpm_data['subsection']
    insts = bpm_data['instance']
    bpms, bpos = [], []
    for ind, inst, sub in zip(inds, insts, subs):
        name = _join_name(sec=section, dis='DI', dev='BPM', sub=sub, idx=inst)
        bpms.append(name)
        bpos.append(pos[ind])
    _write_to_file(filename, bpms, bpos, label)


def _append_bpm_data_bl(filename, acc, all_bpms, label):
    pos = pyaccel.lattice.find_spos(acc)

    mcs = pyaccel.lattice.find_indices(acc, 'fam_name', 'mc')

    bpms_bc = [bpm for bpm in all_bpms if bpm.sub.endswith('BCFE')]
    secs = [int(bpm.sub[:2]) for bpm in bpms_bc]
    bpos_bc = [pos[mcs[ss-1]] for ss in secs]

    mia = pyaccel.lattice.find_indices(acc, 'fam_name', 'mia')
    mib = pyaccel.lattice.find_indices(acc, 'fam_name', 'mib')
    mip = pyaccel.lattice.find_indices(acc, 'fam_name', 'mip')
    mis = sorted(mia + mib + mip)

    end = ('SAFE', 'SBFE', 'SPFE')
    bpms_mi = sorted([bpm for bpm in all_bpms if bpm.sub.endswith(end)])
    secs = [int(bpm.sub[:2]) for bpm in bpms_mi]
    bpos_mi = [pos[mis[ss-1]] for ss in secs]

    bpms = bpms_mi + bpms_bc
    bpos = bpos_mi + bpos_bc
    data = sorted(zip(bpos, bpms))
    bpos, bpms = list(zip(*data))
    _write_to_file(filename, bpms, bpos, label)


def _get_all_bpms():
    data = _crates_mapping()
    bpms = set()
    for line in data.splitlines():
        line = line.strip()
        if not line or line[0] == '#':
            continue  # empty line
        dev, *_ = line.split()
        dev = _PVName(dev)
        if dev.dev in ('BPM', 'PBPM'):
            bpms.add(dev)
    return bpms


def _write_to_file(fname, bpms, pos, label):
    with open(fname, 'a') as fil:
        fil.write('\n\n\n# '+label+'\n')
        fil.write('#'+57*'-' + '\n')
        fil.write("#{bpm:20s} {pos:^15s}\n".format(
            bpm='Name', pos='Position [m]'))
        fil.write('#'+57*'-' + '\n')
        for bpm, p in zip(bpms, pos):
            fil.write(f"{bpm:20s} {p:^15.4f}\n")
