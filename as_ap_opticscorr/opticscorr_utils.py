"""Optics correction utilities method."""

import numpy as _np


class OpticsCorr:
    """Main class for optics correction.

    Calculate Deltas in Quadrupoles and Sextupoles Integrated Strengths.
    Store all correction parameters.
    """

    def __init__(self):
        """Class constructor."""
        self.corr_mat = None
        self.corr_invmat = None
        self.nomchrom = None

    def set_nomchrom(self, nomchromx, nomchromy):
        """Set Nominal Chromaticity.

        Receive:
        nomchromx -- Value correspondent to nominal horizontal chromaticity
        nomchromy -- Value correspondent to nominal vertical chromaticity

        Return (in C-like format):
        nomchrom  -- List of correspondents nominal chromaticities
        """
        nomchrom = _np.array([[nomchromx], [nomchromy]])
        nomchrom = _np.reshape(nomchrom, [2, 1])
        self.nomchrom = nomchrom
        return (list(nomchrom.flatten()))

    def set_corr_mat(self, num_fam, corrmat):
        """Set Correction Matrix and calculate Inverse Matrix.

        Receive:
        num_fam     -- Number of families used in the correction
        corrmat     -- List correspondent to correction matrix

        Return (in C-like format):
        corrmat     -- Flat list correspondent to correction matrix
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

        self.corr_mat = corr_mat
        self.corr_invmat = corr_invmat

        return (list(corr_mat.flatten()),
                list(corr_invmat.flatten()))

    def calc_deltakl(self, delta_tunex, delta_tuney):
        """Calculate delta on Quadrupoles KLs from delta tunes.

        Receive:
        delta_tunex   -- Value correspondent to delta in horizontal tune
        delta_tuney   -- Value correspondent to delta in vertical tune

        Return:
        qfam_delta_kl -- Flat list correspondent to delta KLs of each Booster
                         quadrupole family (same order of correction matrix)
                         To Storage Ring (that uses proportional method), it is
                         correspondent to proportional factor of each
                         quadrupole family
        """
        delta_tune = _np.array([[delta_tunex], [delta_tuney]])

        qfam_delta_kl = _np.dot(self.corr_invmat,
                                delta_tune)

        return list(qfam_delta_kl.flatten())

    def calc_deltasl(self, chromx, chromy):
        """Calculate Sextupoles SLs from chromaticities.

        Receive:
        chromx       -- Value correspondent to final horizontal chromaticity
        chromy       -- Value correspondent to final vertical chromaticity

        Return:
        sfam_deltasl -- Flat list correspondent to SLs of each sextupole family
                        (same order of correction matrix)
                        To proportional method, it is correspondent to
                        proportional factor of each sextupole family
        """
        final_chrom = _np.array([[chromx], [chromy]])
        delta_chrom = (final_chrom - self.nomchrom)

        sfam_deltasl = _np.dot(self.corr_invmat, delta_chrom)

        return list(sfam_deltasl.flatten())

    def estimate_current_deltatune(self, corrmat, current_deltakl):
        """Calculate a estimative to current delta tune.

        Based on the difference between the values of KL_RB pvs and the
        reference KL values received on current_deltakl.

        Receive:
        current_deltakl -- Flat list containing current delta KL

        Return:
        deltatune       -- Flat list containing an estimative to current
                           delta tune
        """
        corrmat = _np.array(corrmat)
        corrmat = _np.reshape(corrmat, [2, len(current_deltakl)])

        current_deltakl = _np.array([current_deltakl]).transpose()

        deltatune = _np.dot(corrmat, current_deltakl)
        return list(deltatune.flatten())

    def estimate_current_chrom(self, current_deltasl):
        """Calculate a estimative to current chromaticity.

        Based on the difference between the values of SL-RB pvs and the nominal
        SL values received on current_deltasl.

        Receive:
        current_deltasl -- Flat list containing current delta SL

        Return:
        chrom           -- Flat list containing an estimative to current
                           chromaticity
        """
        current_deltasl = _np.array([current_deltasl]).transpose()

        deltachrom = _np.dot(self.corr_mat, current_deltasl)
        chrom = self.nomchrom + deltachrom

        return list(chrom.flatten())
