import pyaccel
import pymodels
from siriuspy.namesys import join_name as _join_name, SiriusPVName as _PVName
from siriuspy.clientweb import crates_mapping as _crates_mapping


def run_all():
    generate_bpm_static_table()
    generate_model_static_table()


def generate_model_static_table():
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
    _append_mag_data(filename, model, acc, 'Storage Ring (SR)', 'SI')

    model = pymodels.bo
    acc = model.create_accelerator()
    ind = pyaccel.lattice.find_indices(acc, 'fam_name', 'InjSept')
    acc = pyaccel.lattice.shift(acc, ind[0])
    _append_mag_data(filename, model, acc, 'Booster', 'BO')

    model = pymodels.tb
    acc, *_ = model.create_accelerator()
    _append_mag_data(filename, model, acc, 'Booster Transport Line', 'TB')

    model = pymodels.ts
    acc, *_ = model.create_accelerator()
    _append_mag_data(filename, model, acc, 'SR Transport Line', 'TS')


def _append_mag_data(filename, model, acc, label, section):
    fam_data = model.get_family_data(acc)
    pos = pyaccel.lattice.find_spos(acc)

    mag_tps = []
    mag_tps.extend(model.families.families_dipoles())
    mag_tps.extend(model.families.families_pulsed_magnets())
    mag_tps.extend(model.families.families_quadrupoles())
    mag_tps.extend(model.families.families_horizontal_correctors())
    mag_tps.extend(model.families.families_vertical_correctors())
    mag_tps.extend(model.families.families_sextupoles())
    mag_tps.extend(model.families.families_skew_correctors())

    mag_data = dict()
    for mag_tp in mag_tps:
        inds = fam_data[mag_tp]['index']
        subs = fam_data[mag_tp]['subsection']
        insts = fam_data[mag_tp]['instance']
        for ind, inst, sub in zip(inds, insts, subs):
            name = _join_name(
                sec=section, dis='MA', dev=mag_tp, sub=sub, idx=inst)
            val = (pos[ind[-1]+1] + pos[ind[0]]) / 2
            mag_data[name] = {'pos': val}

    mags = sorted(mag_data.keys())
    with open(filename, 'a') as f:
        f.write('\n\n\n# '+label+'\n')
        f.write('#'+57*'-' + '\n')
        f.write("#{mag:20s} {pos:^20s}\n".format(
            mag='Name', pos='Position @ center [m]'))
        f.write('#'+57*'-' + '\n')
        for mag in mags:
            f.write("{mag:20s} {pos:^20.4f}\n".format(
                mag=mag, **mag_data[mag]))


def generate_bpm_static_table():
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

    crates = _get_crates_mapping()
    model = pymodels.si
    acc = model.create_accelerator()
    _append_bpm_data(filename, model, acc, crates, 'Storage Ring (SR)', 'SI')

    model = pymodels.bo
    acc = model.create_accelerator()
    _append_bpm_data(filename, model, acc, crates, 'Booster (BO)', 'BO')

    model = pymodels.tb
    acc, *_ = model.create_accelerator()
    _append_bpm_data(filename, model, acc, crates, 'BO Transport Line', 'TB')

    model = pymodels.ts
    acc, *_ = model.create_accelerator()
    _append_bpm_data(filename, model, acc, crates, 'SR Transport Line', 'TS')


def _append_bpm_data(filename, model, acc, crates, label, section):
    fam_data = model.get_family_data(acc)
    pos = pyaccel.lattice.find_spos(acc)

    inds = [i[0] for i in fam_data['BPM']['index']]
    subs = fam_data['BPM']['subsection']
    insts = fam_data['BPM']['instance']
    bpm_data = dict()
    for ind, inst, sub in zip(inds, insts, subs):
        name = _join_name(sec=section, dis='DI', dev='BPM', sub=sub, idx=inst)
        bpm_data[name] = {'pos': pos[ind], 'timing': crates[name]}

    bpms = sorted(bpm_data.keys())
    with open('bpms-data.txt', 'a') as f:
        f.write('\n\n\n# '+label+'\n')
        f.write('#'+57*'-' + '\n')
        f.write("#{bpm:20s} {pos:^15s} {timing:20s}\n".format(
                            bpm='Name', pos='Position [m]', timing='Timing'))
        f.write('#'+57*'-' + '\n')
        for bpm in bpms:
            f.write("{bpm:20s} {pos:^15.4f} {timing:20s}\n".format(
                                bpm=bpm, **bpm_data[bpm]))


def _get_crates_mapping():
    data = _crates_mapping()
    crates = dict()
    mapping = dict()
    for line in data.splitlines():
        line = line.strip()
        if not line or line[0] == '#':
            continue  # empty line
        crate, dev, *_ = line.split()
        dev = _PVName(dev)
        if crate not in mapping and dev.dev == 'AMCFPGAEVR':
            crates[crate] = dev
            mapping[crates[crate]] = list()
        else:
            mapping[crates[crate]].append(dev)

    inv_mapping = dict()
    for k, vs in mapping.items():
        for v in vs:
            inv_mapping[v] = k
    return inv_mapping
