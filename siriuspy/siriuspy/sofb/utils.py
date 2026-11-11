"""."""

import numpy as _np

SS_LENGTHS = {'SA': 7.0358, 'SB': 6.1758, 'SP': 6.1758}
BPM_SEC_IDCS = {
    'C1': [0, 1],
    'C2': [2, 3],
    'BC': [3, 4],
    'SA': [-1, 0],
    'SB': [-1, 0],
    'SP': [-1, 0],
}


def get_matrix_ss_section(section_type):
    length = SS_LENGTHS[section_type]
    return _np.array([
        [1, -length / 2, 0, 0],
        [1, length / 2, 0, 0],
        [0, 0, 1, -length / 2],
        [0, 0, 1, length / 2],
    ])


def get_bpm_indices(section_type=None, section_nr=None):
    """Get BPMs indices to set orbit for bump.

    Args:
        section_type (str): Bump section (C1, C2, BC, SA, SB, SP).
        Defaults to None.
        section_nr (int): Section number. Defaults to None.

    Returns:
        1d numpy array: Indices of the BPMs where orbit bump will
          be applied.

    """
    bdict = BPM_SEC_IDCS
    sidx = section_nr - 1
    bpm1_sec_index, bpm2_sec_index = (
        bdict[section_type][0],
        bdict[section_type][1],
    )
    idcs = _np.array([bpm1_sec_index, bpm2_sec_index]) + 8 * sidx
    idcs = _np.r_[idcs, idcs + 160]
    return idcs


def si_calculate_bump(
    orbx, orby, subsec, agx=0, agy=0, psx=0, psy=0, bump_mat=None
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
    elif bump_mat is None:
        raise ValueError(
            'Bump matrix must be provided for BC, C1 and C2 sections.'
        )
    idcs = get_bpm_indices(section_type, section_nr)

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


def find_closest_corrs_ss(ss, nr_ch, nr_cv, inc_rf=False):
    """Find the closest correctors indices to a given sector indices in SOFB matrix."""
    nch = 6
    ncv = 8
    nss = 20
    ss = (ss-1) % 20

    def get_idcs_plane(nr_keep, nr_corr):
        idx_upstream = ss * nr_corr - 1
        idx_downstream = ss * nr_corr
        idcs_up = idx_upstream - _np.arange(int(nr_keep / 2))
        idcs_dw = idx_downstream + _np.arange(int(nr_keep / 2))
        idcs = _np.concatenate((idcs_up, idcs_dw))
        idcs = _np.mod(idcs, nr_corr * nss)
        return _np.sort(_np.unique(idcs))

    idcs_ch = get_idcs_plane(nr_ch, nch)
    idcs_cv = get_idcs_plane(nr_cv, ncv)
    idcs_corrs = _np.concatenate((idcs_ch, idcs_cv + nch * nss))
    if inc_rf:
        idcs_corrs = _np.r_[idcs_corrs, (nch + ncv) * nss]
    return idcs_corrs


def filter_local_distortions(corr_idcs, dorb=None, respmat=None):
    """Filter local orbit distortions.

    Args:
        corr_idcs (numpy 1D array or list): Indices of correctors to use.
        dorb (2D or 1D numpy array, optional): array containing orbit
         distortions x and y, in the case of a 2D array,
          the second dimension must have length 320,
           ie. (npts, 320). Defaults to None.
        respmat (2D numpy array, optional): Orbit response matrix.
         Defaults to None.

    Returns:
        (2D or 1D numpy array): Returns the orbit distortion filtered
        in an array with the same chape as the dorb array, ie (npts, 320).
    """
    kicks = _np.linalg.lstsq(respmat, dorb.T, rcond=None)[0]
    sel = _np.zeros(respmat.shape[1], dtype=bool)
    sel[corr_idcs] = True
    kicks[~sel] = 0
    dorb_filt = respmat @ kicks
    return dorb_filt.T
