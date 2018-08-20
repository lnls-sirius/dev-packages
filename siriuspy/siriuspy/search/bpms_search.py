"""Load and process BBB to PS data from static table in remote server."""

from copy import deepcopy as _dcopy
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
import siriuspy.servweb as _web

_timeout = 1.0


class BPMSearch:
    """Class with mapping BPMS.

    Data are read from the Sirius web server.
    """

    _mapping = None
    _timing_mapping = None

    # BPMsDATA API
    # ==========
    @classmethod
    def reset(cls):
        """Reload data from files."""
        cls._mapping = None
        cls._get_data()

    @classmethod
    def server_online(cls):
        """Return True/False if Sirius web server is online."""
        return _web.server_online()

    @classmethod
    def get_mapping(cls):
        """Return a dictionary with the BPMs."""
        cls._get_data()
        return _dcopy(cls._mapping)

    @classmethod
    def get_names(cls, filters=None, sorting=None):
        """Return a list with the bpm names for the given filter."""
        cls._get_data()
        return _Filter.process_filters(
                                cls._names, filters=filters, sorting=sorting)

    @classmethod
    def get_nicknames(cls, names=None, filters=None, sorting=None):
        """Return a list with BPM nicknames."""
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters, sorting=sorting)
        nicknames = len(names)*['']
        for i, bpm in enumerate(names):
            nicknames[i] = bpm.sub + ('-' + bpm.idx if bpm.idx else '')
        return nicknames

    @classmethod
    def get_positions(cls, names=None, filters=None, sorting=None):
        """Return a list with the positions along the ring."""
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters, sorting=sorting)
        return [cls._mapping[k]['position'] for k in names]

    @classmethod
    def get_timing_mapping(cls):
        """Return a dictionary with the power supply to beaglebone mapping."""
        cls._get_data()
        return _dcopy(cls._timing_mapping)

    @classmethod
    def _get_data(cls):
        if cls._mapping is not None:
            return
        if not _web.server_online():
            raise Exception('could not read data from web server!')
        text = _web.bpms_data(timeout=_timeout)
        cls._build_mapping(text)
        cls._build_timing_to_bpm_mapping()

    @classmethod
    def _build_mapping(cls, text):
        mapping = dict()
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue  # empty line
            key, pos, timing, *_ = line.split()
            key = _PVName(key)
            timing = _PVName(timing)
            if key in mapping.keys():
                raise Exception('BPM {0:s} double entry.'.format(key))
            else:
                mapping[key] = {'position': float(pos), 'timing': timing}
        cls._mapping = mapping
        cls._names = sorted(cls._mapping.keys())

    @classmethod
    def _build_timing_to_bpm_mapping(cls):
        timing_mapping = dict()
        for k, v in cls._mapping.items():
            k2 = v['timing']
            if k2 in timing_mapping.keys():
                timing_mapping[k2] += (k, )
            else:
                timing_mapping[k2] = (k, )
        cls._timing_mapping = timing_mapping


_disclaimer = """
# This file was generated automatically from the data of the files
# in the subfolder Mapeamento_placas_MicroTCA_vs_BPMs and the models
# of the accelerators in the pymodels repository by the function
# siriuspy.search.bpms_search.generate_bpm_static_table.
#
# If the data in the mentioned subfolder change, please, run the script
# again and copy the generated file to replace this one.


"""


def generate_bpm_static_table():
    import pymodels

    with open('bpms-data.txt', 'w') as f:
        f.write(_disclaimer)
        f.write('#BPMs data \n')
        f.write('#-----------')

    crates = _get_crates_mapping()
    model = pymodels.si
    acc = model.create_accelerator()
    _append_bpm_data(model, acc, crates, 'Storage Ring (SR)', 'SI')

    model = pymodels.bo
    acc = model.create_accelerator()
    _append_bpm_data(model, acc, crates, 'Booster', 'BO')

    model = pymodels.tb
    acc, *_ = model.create_accelerator()
    _append_bpm_data(model, acc, crates, 'Booster Transport Line', 'TB')

    model = pymodels.ts
    acc, *_ = model.create_accelerator()
    _append_bpm_data(model, acc, crates, 'SR Transport Line', 'TS')


def _append_bpm_data(model, acc, crates, label, section):
    import pyaccel
    from siriuspy.namesys import join_name as _join_name

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
        f.write("#{bpm:20s} {pos:<15s} {timing:20s}\n".format(
                            bpm='Name', pos='Position [m]', timing='Timing'))
        f.write('#'+57*'-' + '\n')
        for bpm in bpms:
            f.write("{bpm:20s} {pos:<15.4f} {timing:20s}\n".format(
                                bpm=bpm, **bpm_data[bpm]))


def _get_crates_mapping():
    from siriuspy.servweb import crates_mapping as _crates_mapping
    from siriuspy.namesys import SiriusPVName as _PVName

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
