"""."""

import numpy as _np


def get_matrix_ss_section(section_type):
    SS_LENGTHS = {'SA': 7.0358, 'SB': 6.1758, 'SP': 6.1758}
    length = SS_LENGTHS[section_type]
    return _np.array([
        [1, -length / 2, 0, 0],
        [1, length / 2, 0, 0],
        [0, 0, 1, -length / 2],
        [0, 0, 1, length / 2],
    ])


def si_calculate_bump(
    orbx,
    orby,
    subsec,
    agx=0,
    agy=0,
    psx=0,
    psy=0,
    n_bpms_out=3,
    minsingval=0.2,
):
    """Calculate bumps on SA, SB, SP, BC, C2 and C1 subsections.

    Inputs:
        agx, agy, psx, psy - are the desired angles and positions at the
            center of the straight section/center of BC/source point at B2/
            source point at B1. The must have the same unit as orbx and orby.
        subsec - is a 4 character string with the name of the subsection where
            the bump is to be made. Examples: '01SA', '10C1', '13BC', '02SB'
        orbx, orby - the 160-long vector related to the storage ring orbit.
            Ideally this is the reference orbit around which the bump will be
            made.

    Outputs:
        orbx, orby - The orbits with the bump applied to them
    """
    # get section and subsection
    section_nr = int(subsec[:2])
    if not 1 <= section_nr <= 20:
        raise ValueError('Section must be between 01..20.')

    section_type = subsec[2:]
    if 'S' in section_type:
        mat_s2r = get_matrix_ss_section(section_type)
        idcs = [(section_nr - 1) * 8 - 1, (section_nr - 1) * 8]
    else:
        from apsuite.orbcorr.si_bumps import SiCalcBumps

        bump = SiCalcBumps()
        _, _, mat_s2r = bump.calc_matrices(
            section_type=section_type,
            section_nr=section_nr,
            n_bpms_out=n_bpms_out,
            use_ss_tfm=False,
            minsingval=minsingval,
        )
        idcs = bump.get_bpm_indices(section_type, section_nr - 1)

    vec = _np.array([psx, agx, psy, agy])
    pos_bpm = _np.dot(mat_s2r, vec)

    bpm1 = idcs[0]
    bpm2 = idcs[1]

    orbx, orby = orbx.copy(), orby.copy()
    orbx[bpm1] += pos_bpm[0]
    orbx[bpm2] += pos_bpm[1]
    orby[bpm1] += pos_bpm[2]
    orby[bpm2] += pos_bpm[3]
    return orbx, orby
