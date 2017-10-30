"""Optics correction utilities method."""

import numpy as _np
from siriuspy import util as _util


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


def read_corrparams(filename):
    """Read correction parameters from Soft IOC local file on "filename".

    Receive:
    filename   -- complete name of the file

    Return:
    data       -- matrix containing correction parameters in the order
                  explained on the header of the file
    parameters -- parameters contained on header of the file
    """
    f = open(filename, 'r')
    text = f.read()
    f.close()
    data, parameters = _util.read_text_data(text)
    return data, parameters


def save_corrparams(filename, corrmat, num_fam,
                    nomintstren=None, nomchrom=None):
    """Generate Soft IOC correction parameters local files on "filename".

    Receive:
    filename    -- complete name of the file
    corrmat     -- correction matrix on flat list format
    num_fam     -- number of families used on correction
    nomintstren -- nominal integrated strengths on flat list format
    nomchrom    -- nominal chromaticity on flat list format

    Return:
    text     -- the text that will be written on file
    """
    name = filename.split('/')[-1].strip('.txt')
    acc = name.split('-')[0]
    opticsparam = name.split('-')[-1]
    text = ''
    header = ''
    NominalChrom = ''
    m = ''
    NominalIntStren = ''

    if opticsparam == 'tunecorr':
        if acc == 'bo':
            header = ("# Tune Correction Response Matrix for Booster\n#\n"
                      "# | DeltaTuneX |   | m11  m12 |   | KL BO-Fam:MA-QF |\n"
                      "# |            | = |          | * |                 |\n"
                      "# | DeltaTuneY |   | m21  m22 |   | KL BO-Fam:MA-QD |\n"
                      "#\n"
                      "# Correction Matrix\n"
                      "#   m11   m12\n"
                      "#   m21   m22\n\n\n")

        elif acc == 'si':
            header = ("# Tune Correction Parameters for Storage Ring\n#\n"
                      "#  | DeltaTuneX |    | m11  m12...m18 |"
                      "   | f SI QFA  |\n"
                      "#  |            | =  |                |"
                      " * |     .     |\n"
                      "#  | DeltaTuneY |    | m21  m22...m28 |"
                      "   |     .     |\n"
                      "#                                      "
                      "   |     .     |\n"
                      "#                                      "
                      "   | f SI QDP2 |\n"
                      "# Where (1+f)KL = KL + DeltaKL.\n"
                      "#\n"
                      "# Correction Matrix of Svd and Additional Method "
                      "(obtained by matlab lnls_correct_tunes routine)\n"
                      "#   m11   m12...m18\n"
                      "#   m21   m22...m28\n"
                      "#\n"
                      "# Nominals KLs\n"
                      "# [quadrupole_order"
                      "   QFA  QFB  QFP  QDA  QDB1  QDB2  QDP1  QDP2]\n\n\n)")

            if nomintstren is not None:
                for sl in range(len(nomintstren)):
                    if nomintstren[sl] < 0:
                        space = '  '
                    else:
                        space = '   '
                    NominalIntStren += space + str(nomintstren[sl])
                NominalIntStren += '\n\n'
            else:
                return False

    elif opticsparam == 'chromcorr':
        if acc == 'bo':
            header = ("# Chromaticity Correction Parameters for Booster\n#\n"
                      "# | ChromX |   | NominalChromX |   | m11  m12 |"
                      "   | SL BO-Fam:MA-SF |\n"
                      "# |        | = |               | + |          |"
                      " * |                 |\n"
                      "# | ChromY |   | NominalChromY |   | m21  m22 |"
                      "   | SL BO-Fam:MA-SD |\n"
                      "#\n"
                      "# Natural Chromaticity (considers Quadrupoles and"
                      " Dipoles Multipoles)\n"
                      "#   NaturalChromX   NaturalChromY\n"
                      "#\n"
                      "# Nominal Chromaticity\n"
                      "#   NominalChromX   NominalChromY\n"
                      "#\n"
                      "# Correction Matrix of Additional Method\n"
                      "#   m11   m12\n"
                      "#   m21   m22\n"
                      "#\n"
                      "# Nominals SLs\n"
                      "# [sextupole_order  SF  SD]\n\n\n")

        elif acc == 'si':
            header = ("# Chromaticity Correction Parameters for Storage Ring\n"
                      "#\n"
                      "# | ChromX |   | NominalChromX |   | m11  m12...m115 |"
                      "   | 1+f_SFA1 SI SFA1 |\n"
                      "# |        | = |               | + |                 |"
                      " * |          .       |\n"
                      "# | ChromY |   | NominalChromY |   | m21  m22...m215 |"
                      "   |          .       |\n"
                      "#                                                     "
                      "   |          .       |\n"
                      "#                                                     "
                      "   | 1+f_SDP3 SI SDP3 |\n"
                      "# Where (1+f)SLnom = SLnom + DeltaSLnom\n#\n"
                      "# Data ordering:\n#\n"
                      "# Nominal Chromaticity\n"
                      "#    NominalChromX    NominalChromY\n"
                      "#\n"
                      "# Correction Matrix of Additional Method\n"
                      "#   m11   m12 ... m115\n"
                      "#   m21   m22 ... m215\n"
                      "#\n"
                      "# Nominals SLs\n"
                      "# [sextupole_order  SFA1  SFA2  SDA1  SDA2  SDA3  SFB1"
                      "  SFB2  SDB1  SDB2  SDB3  SFP1  SFP2  SDP1  SDP2  SDP3]"
                      "\n\n\n")

        if nomchrom is not None:
            NominalChrom = ('   ' + str(nomchrom[0]) +
                            '   ' + str(nomchrom[1]) + '\n\n\n')
        else:
            return False

        if nomintstren is not None:
            for sl in range(len(nomintstren)):
                if nomintstren[sl] < 0:
                    space = '  '
                else:
                    space = '   '
                NominalIntStren += space + str(nomintstren[sl])
            NominalIntStren += '\n\n'
        else:
            return False

    index = 0
    for row in range(2):
        for col in range(num_fam):
            if corrmat[index] < 0:
                space = '  '
            else:
                space = '   '
            m += space + str(corrmat[index])
            index += 1
        m += '\n'
    m += '\n\n'
    m
    text = header + NominalChrom + m + NominalIntStren

    f = open(filename, 'w')
    f.write(text)
    f.close()

    return text
