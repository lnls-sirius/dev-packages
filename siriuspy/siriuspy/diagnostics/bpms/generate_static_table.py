from siriuspy.namesys import join_name
from siriuspy.diagnostics import cratesdata
import pymodels
import pyaccel

def func(model, acc, label, section):
    fam_data = model.get_family_data(acc)
    pos = pyaccel.lattice.find_spos(acc)

    inds  = [ i[0] for i in fam_data['BPM']['index']]
    subs  = fam_data['BPM']['subsection']
    insts = fam_data['BPM']['instance']
    bpm_data = dict()
    for ind,inst,sub in zip(inds,insts,subs):
        name = join_name(section=section,discipline='DI',device='BPM',subsection=sub, instance=inst)
        bpm_data[name] = {'pos':pos[ind], 'crate':crates[name]}

    bpms = sorted(bpm_data.keys())
    with open('bpms-data.txt','a') as f:
        f.write('\n\n\n# '+label+'\n')
        f.write('#'+57*'-' + '\n')
        f.write("#{bpm:20s} {pos:<15s} {crate:20s}\n".format(bpm='Name',pos='Position [m]', crate='Crate'))
        f.write('#'+57*'-' + '\n')
        for bpm in bpms:
            f.write("{bpm:20s} {pos:<15.4f} {crate:20s}\n".format(bpm=bpm,**bpm_data[bpm]))


with open('bpms-data.txt','w') as f:
    f.write('#BPMs data \n')
    f.write('#-----------')

crates = cratesdata.get_inverse_mapping()
model = pymodels.si
acc = model.create_accelerator()
func(model,acc,'Sirius','SI')

crates = cratesdata.get_inverse_mapping()
model = pymodels.bo
acc = model.create_accelerator()
func(model,acc,'Booster','BO')
