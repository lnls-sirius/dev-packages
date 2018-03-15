#!/usr/bin/env python3

from siriuspy.pwrsupply.model import PowerSupplySync
from siriuspy.magnet.model import MagnetDipole, MagnetQuad, PowerSupplyMA


def create_ps_b1b2(current_sp=None):
    ps_b1b2 = PowerSupplySync(psnames=['SI-Fam:PS-B1B2-1','SI-Fam:PS-B1B2-2'],
                              controller_type='ControllerSim',
                              lock=True)
    ps_b1b2.pwrstate_sel = 1
    if current_sp:
        ps_b1b2.current_sp = current_sp
    return ps_b1b2

def create_ma_b1b2(current_sp=None, energy=None):
    ps_b1b2 = create_ps_b1b2(current_sp=current_sp)
    ma_b1b2 = MagnetDipole(maname='SI-Fam:MA-B1B2', psupplies=[ps_b1b2,])
    if energy:
        ma_b1b2.set_energy(energy)
    return ma_b1b2

def test_lock(ps_b1b2):
    ps_b1b2 = PowerSupplySync(psnames=['SI-Fam:PS-B1B2-1','SI-Fam:PS-B1B2-2'],
                              controller_type='ControllerSim',
                              lock=True)
    c0 = ps_b1b2._controllers[0]
    c1 = ps_b1b2._controllers[1]
    ps_b1b2.pwrstate_sel = 1
    c0.current_sp = 1.1
    print(c0.current_sp)
    print(c1.current_sp)
    ps_b1b2.current_sp = 1.2
    print(c0.current_sp)
    print(c1.current_sp)

def test_si_dipole_sim():

    ma_b1b2 = create_ma_b1b2()
    print('- turning on si dipole power supply...')
    ps_b1b2 = ma_b1b2._psupplies[0]
    ps_b1b2.pwrstate_sel = 1
    current_sp = 390.0; print('- setting current_sp to ', current_sp)
    ps_b1b2.current_sp = current_sp
    print('current_ps  : ', ps_b1b2.current_sp)
    print('current_mon : ', ps_b1b2.current_mon)
    print('energy_mon  : ', ma_b1b2.get_energy(current_attr='current_mon'))
    print('brho_mon    : ', ma_b1b2.get_brho(current_attr='current_mon'))
    energy = 3.0; print('- setting energy to ', energy)
    ma_b1b2.set_energy(energy)
    print('current_ps  : ', ps_b1b2.current_sp)
    print('current_mon : ', ps_b1b2.current_mon)
    print('energy_mon  : ', ma_b1b2.get_energy(current_attr='current_mon'))
    print('brho_mon    : ', ma_b1b2.get_brho(current_attr='current_mon'))

def test_si_qda_sim():
    ma_b1b2 = create_ma_b1b2()

    ma_b1b2.set_energy(3.0)
    
    ps_qda = PowerSupplySync(psnames=['SI-Fam:PS-QDA',],
                             controller_type='ControllerSim',
                             lock=True)
    ma_qda = MagnetQuad(maname='SI-Fam:MA-QDA', psupplies=[ps_qda,], dipole=ma_b1b2)
    print('- turning on si qda power supply...')
    ps_qda.pwrstate_sel = 1
    # current_sp = 120; print('- setting current_sp to ', current_sp)
    # ps_qda.current_sp = current_sp
    # print('current_ps  : ', ps_qda.current_sp)
    # print('current_mon : ', ps_qda.current_mon)
    # print('kl_mon      : ', ma_qda.get_kl(current_attr='current_mon'))
    # print('energy_mon  : ', ma_qda.dipole.get_energy(current_attr='current_mon'))
    # print('brho_mon    : ', ma_qda.dipole.get_brho(current_attr='current_mon'))
    kl = -0.1; print('- setting kl to ', kl)
    ma_qda.set_kl(kl)
    print('current_ps  : ', ps_qda.current_sp)
    print('current_mon : ', ps_qda.current_mon)
    print('kl_mon      : ', ma_qda.get_kl(current_attr='current_mon'))
    print('energy_mon  : ', ma_qda.dipole.get_energy(current_attr='current_mon'))
    print('brho_mon    : ', ma_qda.dipole.get_brho(current_attr='current_mon'))


def test_psma():

    b1b2 = PowerSupplyMA(maname='SI-Fam:MA-B1B2',
                         controller_type='ControllerSim',
                         lock=True,
                         enum_keys=True)

    b1b2.pwrstate_sel = 'On'
    b1b2.current_sp = 200
    print('strength sp  : ', b1b2.strength_sp)
    print('strength mon : ', b1b2.strength_mon)

#test_psma()
test_si_qda_sim()
#test_si_dipole_sim()
#test_lock(ps_b1b2)
