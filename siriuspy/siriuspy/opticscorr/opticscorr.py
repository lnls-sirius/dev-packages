"""Optics correction module."""


import numpy as _np
from ..clientconfigdb import ConfigDBDocument as _ConfigDBDocument
from .csdev import Const as _Const


class OpticsCorr:
    """Main class for optics correction.

    Calculate Deltas in Quadrupoles and Sextupoles Integrated Strengths.
    Store all correction parameters.
    """

    def __init__(self, magnetfams_ordering,
                 nominal_matrix, nominal_intstrengths, nominal_opticsparam,
                 magnetfams_focusing, magnetfams_defocusing):
        """Class constructor."""
        # declaration of attributes (as pylint requires)
        self._nominal_matrix = None
        self._initialized = False
        self._nominal_intstrengths = None
        self._matrix_prop_svd = None
        self._matrix_prop_2knobs = None
        self._inverse_matrix_prop_svd = None
        self._inverse_matrix_prop_2knobs = None
        self._nominal_opticsparam = None
        self._magnetfams_focusing = None
        self._magnetfams_defocusing = None

        # initialization of attributes
        self._set_magnetfams_ordering(magnetfams_ordering)
        self.nominal_matrix = nominal_matrix
        self.nominal_intstrengths = nominal_intstrengths
        self.nominal_opticsparam = nominal_opticsparam
        self.magnetfams_focusing = magnetfams_focusing
        self.magnetfams_defocusing = magnetfams_defocusing

        self._calculate_matrices()
        self._initialized = True

    @property
    def magnetfams_ordering(self):
        """List of strings of the order of magnet families used on correction.

        Correction matrix and nominal integrated strengths must be coherent to
        this property.
        """
        return self._magnetfams_ordering

    def _set_magnetfams_ordering(self, value):
        """Set magnetfams_ordering_svd property."""
        if not isinstance(value, tuple):
            raise TypeError("Value must be a tuple.")
        for item in value:
            if not isinstance(item, str):
                raise TypeError("List elements must be strings.")
        if len(value) < 2:
            raise ValueError("At least 2 magnet families are necessary to "
                             "correction!")

        self._magnetfams_ordering = value

    @property
    def nominal_matrix(self):
        """Nominal matrix, correspondent to add method and multiple knobs.

        Considers all knobs listed in 'magnetfams_ordering' property.
        """
        return self._nominal_matrix

    @nominal_matrix.setter
    def nominal_matrix(self, value):
        if not isinstance(value, list):
            raise TypeError("Value must be a flat list (C-like format.")
        for item in value:
            if not isinstance(item, float):
                raise TypeError("List elements must be floats.")

        matrix = _np.array(value)
        matrix = _np.reshape(matrix, [2, len(self._magnetfams_ordering)])

        self._nominal_matrix = matrix

        if self._initialized:
            self._calculate_matrices()

    @property
    def nominal_intstrengths(self):
        """Nominal integrated strengths."""
        return self._nominal_intstrengths

    @nominal_intstrengths.setter
    def nominal_intstrengths(self, value):
        if not isinstance(value, list):
            raise TypeError("Value must be a flat list (C-like format.")
        for item in value:
            if not isinstance(item, float):
                raise TypeError("List elements must be floats.")

        intstrengths = _np.array(value)
        intstrengths = _np.reshape(intstrengths,
                                   [1, len(self._magnetfams_ordering)])

        self._nominal_intstrengths = intstrengths

        if self._initialized:
            self._matrix_prop_svd = self._calculate_matrix_svd(method=0)
            self._matrix_prop_2knobs = self._calculate_matrix_2knobs(method=0)
            self._inverse_matrix_prop_svd = (
                self._calculate_inverse(method=0, grouping='svd'))
            self._inverse_matrix_prop_2knobs = (
                self._calculate_inverse(method=0, grouping='2knobs'))

    @property
    def nominal_opticsparam(self):
        """Nominal optics parameter."""
        return self._nominal_opticsparam

    @nominal_opticsparam.setter
    def nominal_opticsparam(self, value):
        if not isinstance(value, list):
            raise TypeError("Value must be a flat list (C-like format.")
        for item in value:
            if not isinstance(item, float):
                raise TypeError("List elements must be floats.")

        opticsparam = _np.array(value)
        opticsparam = _np.reshape(opticsparam, [2, 1])

        self._nominal_opticsparam = opticsparam

    @property
    def magnetfams_focusing(self):
        """List of strings of focusing magnet families used on correction.

        It corresponds to the first correction knob magnet families.
        """
        return self._magnetfams_focusing

    @magnetfams_focusing.setter
    def magnetfams_focusing(self, value):
        if not isinstance(value, tuple):
            raise TypeError("Value must be a tuple.")
        for item in value:
            if not isinstance(item, str):
                raise TypeError("List elements must be strings.")
        if not value:
            raise ValueError("At least one focusing magnet family is "
                             "necessary to correction!")
        if not all(item in self._magnetfams_ordering for item in value):
            raise ValueError("Focusing magnet families must be part of the "
                             "'magnetfams_ordering' property!")

        self._magnetfams_focusing = tuple(sorted(
            value, key=self.magnetfams_ordering.index))

        if self._initialized:
            self._calculate_matrices()

    @property
    def magnetfams_defocusing(self):
        """List of strings of defocusing magnet families used on correction.

        It corresponds to the second correction knob magnet families.
        """
        return self._magnetfams_defocusing

    @magnetfams_defocusing.setter
    def magnetfams_defocusing(self, value):
        if not isinstance(value, tuple):
            raise TypeError("Value must be a tuple.")
        for item in value:
            if not isinstance(item, str):
                raise TypeError("List elements must be strings.")
        if not value:
            raise ValueError("At least one defocusing magnet family is "
                             "necessary to correction!")
        if not all(item in self._magnetfams_ordering for item in value):
            raise ValueError("Defocusing magnet families must be part of the "
                             "'magnetfams_ordering_svd' property!")

        self._magnetfams_defocusing = tuple(sorted(
            value, key=self.magnetfams_ordering.index))

        if self._initialized:
            self._calculate_matrices()

    @property
    def matrix_add_svd(self):
        """Matrix of additional method and multiple knobs."""
        return self._matrix_add_svd

    @property
    def matrix_prop_svd(self):
        """Matrix of proportional method and multiple knobs."""
        return self._matrix_prop_svd

    @property
    def matrix_add_2knobs(self):
        """Matrix of additional method and 2 knobs."""
        return self._matrix_add_2knobs

    @property
    def matrix_prop_2knobs(self):
        """Matrix of proportional method and 2 knobs."""
        return self._matrix_prop_2knobs

    @property
    def inverse_matrix_add_svd(self):
        """Inverse matrix of additional method and multiple knobs."""
        return self._inverse_matrix_add_svd

    @property
    def inverse_matrix_prop_svd(self):
        """Inverse matrix of proportional method and multiple knobs."""
        return self._inverse_matrix_prop_svd

    @property
    def inverse_matrix_add_2knobs(self):
        """Inverse matrix of additional method and 2 knobs."""
        return self._inverse_matrix_add_2knobs

    @property
    def inverse_matrix_prop_2knobs(self):
        """Inverse matrix of proportional method and 2 knobs."""
        return self._inverse_matrix_prop_2knobs

    def calculate_delta_intstrengths(self, method, grouping,
                                     delta_opticsparam):
        """Calculate the delta on integrated strengths.

        Based on the required optics parameter delta (tune or chromaticity).

        Return a flat numpy.array of deltas of all magnet families of
        'magnetfams_ordering' property. Deltas will only be calculated for
        families listed on 'magnetfams_focusing' and 'magnetfams_defocusing'
        properties. The rest of the families will have null deltas.
        """
        inv = self._choose_inverse_matrix(method, grouping)
        delta_opticsparam = _np.array([[delta_opticsparam[0]],
                                       [delta_opticsparam[1]]])
        magnetfams_delta_intstrengths = _np.zeros(
            len(self.magnetfams_ordering))

        delta = _np.dot(inv, delta_opticsparam).T.flatten()

        foc = len(self.magnetfams_focusing)
        defoc = len(self.magnetfams_defocusing)
        if method == 0:
            if grouping == 'svd':
                for i in range(foc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_focusing[i])
                    magnetfams_delta_intstrengths[index] = (
                        self.nominal_intstrengths[0, index] * delta[i])
                for i in range(defoc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_defocusing[i])
                    magnetfams_delta_intstrengths[index] = (
                        self.nominal_intstrengths[0, index] * delta[i+foc])
            elif grouping == '2knobs':
                for i in range(foc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_focusing[i])
                    magnetfams_delta_intstrengths[index] = (
                        self.nominal_intstrengths[0, index] * delta[0])
                for i in range(defoc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_defocusing[i])
                    magnetfams_delta_intstrengths[index] = (
                        self.nominal_intstrengths[0, index] * delta[1])
        elif method == 1:
            if grouping == 'svd':
                for i in range(foc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_focusing[i])
                    magnetfams_delta_intstrengths[index] = delta[i]
                for i in range(defoc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_defocusing[i])
                    magnetfams_delta_intstrengths[index] = delta[i+foc]
            elif grouping == '2knobs':
                for i in range(foc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_focusing[i])
                    magnetfams_delta_intstrengths[index] = delta[0]
                for i in range(defoc):
                    index = self.magnetfams_ordering.index(
                        self.magnetfams_defocusing[i])
                    magnetfams_delta_intstrengths[index] = delta[1]

        return magnetfams_delta_intstrengths.flatten()

    def calculate_opticsparam(self, delta_intstrengths):
        """Calculate the optics parameter (tune or chromaticity).

        Based on the required integrated strengths.
        """
        delta_intstrengths = _np.array([delta_intstrengths]).transpose()

        delta_opticsparam = _np.dot(self.nominal_matrix, delta_intstrengths)
        opticsparam = self.nominal_opticsparam + delta_opticsparam

        return opticsparam.flatten()

    # Private methods

    def _calculate_matrices(self):
        """Recalculate all matrices and their ineverse matrices."""
        self._matrix_add_svd = self._calculate_matrix_svd(method=1)
        self._matrix_prop_svd = self._calculate_matrix_svd(method=0)
        self._matrix_add_2knobs = self._calculate_matrix_2knobs(method=1)
        self._matrix_prop_2knobs = self._calculate_matrix_2knobs(method=0)
        self._inverse_matrix_add_svd = self._calculate_inverse(
            method=1, grouping='svd')
        self._inverse_matrix_prop_svd = self._calculate_inverse(
            method=0, grouping='svd')
        self._inverse_matrix_add_2knobs = self._calculate_inverse(
            method=1, grouping='2knobs')
        self._inverse_matrix_prop_2knobs = self._calculate_inverse(
            method=0, grouping='2knobs')

    def _calculate_matrix_svd(self, method):
        """Calculate matrix of multiple knobs (svd)."""
        if method == 0:  # proportional method
            matrix = self.nominal_matrix*self.nominal_intstrengths
        elif method == 1:  # additional method
            matrix = self.nominal_matrix

        foc = len(self.magnetfams_focusing)
        defoc = len(self.magnetfams_defocusing)
        mat_svd = _np.zeros([2, foc+defoc])

        for i in range(foc):
            idxc = self.magnetfams_ordering.index(self.magnetfams_focusing[i])
            mat_svd[0, i] = matrix[0, idxc]
            mat_svd[1, i] = matrix[1, idxc]
        for i in range(defoc):
            idxc = self.magnetfams_ordering.index(
                self.magnetfams_defocusing[i])
            mat_svd[0, i+foc] = matrix[0, idxc]
            mat_svd[1, i+foc] = matrix[1, idxc]

        return mat_svd

    def _calculate_matrix_2knobs(self, method):
        """Calculate matrices of 2 knobs."""
        if method == 0:  # proportional method
            matrix = self.nominal_matrix*self.nominal_intstrengths
        elif method == 1:  # additional method
            matrix = self.nominal_matrix

        mat_2knobs = _np.array([[0.0, 0.0], [0.0, 0.0]])
        # matrix indices are organized like:
        # [focusing magnet fams, X plan    defocusing magnet fams, X plan]
        # [focusing magnet fams, Y plan    defocusing magnet fams, Y plan]

        for fam in self.magnetfams_focusing:
            index = self.magnetfams_ordering.index(fam)
            mat_2knobs[0, 0] += matrix[0, index]
            mat_2knobs[1, 0] += matrix[1, index]

        for fam in self.magnetfams_defocusing:
            index = self.magnetfams_ordering.index(fam)
            mat_2knobs[0, 1] += matrix[0, index]
            mat_2knobs[1, 1] += matrix[1, index]

        return mat_2knobs

    def _calculate_inverse(self, method, grouping):
        """Calculate inverse of a matrix using SVD."""
        matrix = self._choose_matrix(method, grouping)

        try:
            umat, smat, vmat = _np.linalg.svd(matrix, full_matrices=False)
        except _np.linalg.LinAlgError():
            raise Exception("Could not calculate SVD.")
        inv = _np.dot(_np.dot(vmat.T, _np.diag(1/smat)), umat.T)
        isnan = _np.any(_np.isnan(inv))
        isinf = _np.any(_np.isinf(inv))
        if isnan or isinf:
            raise Exception("Pseudo inverse contains nan or inf.")

        return inv

    def _choose_matrix(self, method, grouping):
        if method == 0:
            if grouping == 'svd':
                matrix = self.matrix_prop_svd
            elif grouping == '2knobs':
                matrix = self.matrix_prop_2knobs
        elif method == 1:
            if grouping == 'svd':
                matrix = self.matrix_add_svd
            elif grouping == '2knobs':
                matrix = self.matrix_add_2knobs
        return matrix

    def _choose_inverse_matrix(self, method, grouping):
        if method == 0:
            if grouping == 'svd':
                matrix = self.inverse_matrix_prop_svd
            elif grouping == '2knobs':
                matrix = self.inverse_matrix_prop_2knobs
        elif method == 1:
            if grouping == 'svd':
                matrix = self.inverse_matrix_add_svd
            elif grouping == '2knobs':
                matrix = self.inverse_matrix_add_2knobs
        return matrix


class BOTuneCorr(OpticsCorr, _ConfigDBDocument):
    """Auxiliar class to handle Booster tune correction."""

    def __init__(self, name):
        """Get configuration from ConfigServer and initialize object."""
        _ConfigDBDocument.__init__(self, 'bo_tunecorr_params', name=name)

        self.load()
        params = self.value
        nominal_matrix = [item for sublist in params['matrix']
                          for item in sublist]
        nominal_kl = params['nominal KLs']
        OpticsCorr.__init__(
            self,
            magnetfams_ordering=_Const.BO_QFAMS_TUNECORR,
            nominal_matrix=nominal_matrix,
            nominal_intstrengths=nominal_kl,
            nominal_opticsparam=[0.0, 0.0],
            magnetfams_focusing=('QF',),
            magnetfams_defocusing=('QD',))

    def calculate_deltaKL(self, delta_tune):
        """Calculate delta KL based on the required delta tune."""
        return self.calculate_delta_intstrengths(
            method=1, grouping='2knobs', delta_opticsparam=delta_tune)

    def calculate_deltaTune(self, deltaKL):
        """Calculate delta tune based on the required delta KL."""
        return self.calculate_opticsparam(delta_intstrengths=deltaKL)


class BOChromCorr(OpticsCorr, _ConfigDBDocument):
    """Auxiliar class to handle Booster chromacity correction."""

    def __init__(self, name):
        """Get configuration from ConfigServer and initialize object."""
        _ConfigDBDocument.__init__(self, 'bo_chromcorr_params', name=name)

        self.load()
        params = self.value
        nominal_matrix = [item for sublist in params['matrix']
                          for item in sublist]
        nominal_sl = params['nominal SLs']
        nominal_chrom = params['nominal chrom']
        OpticsCorr.__init__(self,
                            magnetfams_ordering=_Const.BO_SFAMS_CHROMCORR,
                            nominal_matrix=nominal_matrix,
                            nominal_intstrengths=nominal_sl,
                            nominal_opticsparam=nominal_chrom,
                            magnetfams_focusing=('SF',),
                            magnetfams_defocusing=('SD',))

    def calculate_deltaSL(self, delta_chrom):
        """Calculate delta SL based on the required delta chromacity."""
        return self.calculate_delta_intstrengths(
            method=1, grouping='2knobs', delta_opticsparam=delta_chrom)

    def calculate_Chrom(self, deltaSL):
        """Calculate delta chromacity based on the required delta SL."""
        return self.calculate_opticsparam(delta_intstrengths=deltaSL)
