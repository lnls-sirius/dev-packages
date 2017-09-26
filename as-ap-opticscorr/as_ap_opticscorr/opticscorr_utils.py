"""Calculate Deltas in Quadrupoles and Sextupoles Strengths."""
import numpy as _np


class OpticsCorr:
    """Main class."""

    def __init__(self):
        """Class constructor."""
        self.tunecorr_mat = None
        self.tunecorr_invmat = None
        self.chromcorr_mat = None
        self.chromcorr_invmat = None
        self.chrom0 = None

    def set_corr_mat(self, optics, num_fam, corrmat):
        """Set Correction Matrix and calculate Inverse Matrix.

        Receive:
        optics  -- Optics parameter to set correction matrix.
                   Can be 'tune' or 'chrom'
        num_fam -- Number of families used in the correction
        corrmat -- List correspondent to correction matrix, in float format

        Return (in C-like format):
        corrmat     -- Flat list correspondent to correction matrix.
        corr_invmat -- Flat list correspondent to inverse of correction matrix
        """
        corr_mat = _np.array(corrmat)
        corr_mat = _np.reshape(corr_mat, [2, num_fam])

        try:
            U, S, V = _np.linalg.svd(corr_mat, full_matrices=False)
        except _np.linalg.LinAlgError():
            print('Could not calculate SVD')
            return None, None
        corr_invmat = _np.dot(_np.dot(V.T, _np.diag(1/S)), U.T)
        isNan = _np.any(_np.isnan(corr_invmat))
        isInf = _np.any(_np.isinf(corr_invmat))
        if isNan or isInf:
            print('Pseudo inverse contains nan or inf.')
            return None, None

        if optics == 'tune':
            self.tunecorr_mat = corr_mat
            self.tunecorr_invmat = corr_invmat
            # print(self.tunecorr_mat)
        elif optics == 'chrom':
            self.chromcorr_mat = corr_mat
            self.chromcorr_invmat = corr_invmat
            # print(self.chromcorr_mat)

        return (list(corr_mat.flatten()),
                list(corr_invmat.flatten()))

    def set_chrom0(self, chrom0x, chrom0y):
        """Set Initial Chromaticity.

        Receive:
        chrom0 -- List correspondent to initial chromaticity, in float format.
                  [chrom0x, chrom0y]-like
                  Considers Quadrupoles and Dipoles Multipoles.
        Return (in C-like format):
        chrom0 -- The same of the input, after convertion to numpy array and
                  convertion again to list. This operation can change precision
                  of float numbers.
        """
        chrom0 = _np.array([[chrom0x], [chrom0y]])
        chrom0 = _np.reshape(chrom0, [2, 1])
        self.chrom0 = chrom0
        return (list(chrom0.flatten()))

    def calc_deltakl(self, delta_tunex, delta_tuney):
        """Calculate delta on Quadrupoles KLs from delta tunes.

        Receive:
        delta_tunex -- Float correspondent to delta in horizontal tune
        delta_tuney -- Float correspondent to delta in vertical tune

        Return:
        qfam_delta_kl -- Flat list correspondent to delta KLs of each Booster
                         quadrupole family (same order of correction matrix).
                         To Storage Ring (that uses proportional method), it is
                         correspondent to proportional factor of each
                         quadrupole family.
        """
        delta_tune = _np.array([[delta_tunex], [delta_tuney]])

        qfam_delta_kl = _np.dot(self.tunecorr_invmat,
                                delta_tune)

        return list(qfam_delta_kl.flatten())

    def calc_sl(self, chromx, chromy):
        """Calculate Sextupoles SLs from chromaticities.

        Receive:
        chromx -- Float correspondent to final horizontal chromaticity
        chromy -- Float correspondent to final vertical chromaticity

        Return:
        sfam_sl -- Flat list correspondent to SLs of each Booster sextupole
                   family (same order of correction matrix).
                   To Storage Ring (that uses proportional method), it is
                   correspondent to (1 + proportional factor) of each sextupole
                   family.
        """
        final_chrom = _np.array([[chromx], [chromy]])
        delta_chrom = (final_chrom - self.chrom0)

        sfam_sl = _np.dot(self.chromcorr_invmat,
                          delta_chrom)

        return list(sfam_sl.flatten())
