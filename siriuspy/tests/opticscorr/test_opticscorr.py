#!/usr/bin/env python3.6

"""Module to test opticscorr."""

import unittest
import numpy as np
from siriuspy import util
from siriuspy.opticscorr.opticscorr import OpticsCorr

PUB_INTERFACE = (
    'magnetfams_ordering',
    'nominal_matrix',
    'nominal_intstrengths',
    'nominal_opticsparam',
    'magnetfams_focusing',
    'magnetfams_defocusing',
    'matrix_add_svd',
    'matrix_add_2knobs',
    'matrix_prop_svd',
    'matrix_prop_2knobs',
    'inverse_matrix_add_svd',
    'inverse_matrix_add_2knobs',
    'inverse_matrix_prop_svd',
    'inverse_matrix_prop_2knobs',
    'calculate_delta_intstrengths',
    'calculate_opticsparam'
)


class TestOpticsCorr(unittest.TestCase):
    """Test OpticsCorr class."""

    def setUp(self):
        """Setup tests."""
        # Attributs fot simulating normal operation
        self.magnetfams_ordering_ok = (
            'QFA', 'QFB', 'QFP', 'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2')
        self.magnetfams_focusing_ok = ('QFA', 'QFB', 'QFP')
        self.magnetfams_defocusing_ok = (
            'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2')
        self.nominal_matrix_ok = [2.7280, 8.5894, 4.2995, 0.5377,
                                  1.0906, 2.0004, 0.5460, 1.0012,
                                  -1.3651, -3.5532, -1.7657, -2.3652,
                                  -4.7518, -1.9781, -2.3601, -0.9839]
        self.nominal_intstrengths_ok = [0.7146, 1.2344, 1.2344, -0.2270,
                                        -0.2809, -0.4783, -0.2809, -0.4783]
        self.nominal_opticsparam_ok = [0.0, 0.0]

        # Attributes to simulate type errors
        self.magnetfams_ordering_error1 = (1, 2, 3, 4)
        self.magnetfams_focusing_error1 = (1, 2)
        self.magnetfams_defocusing_error1 = (3, 4)
        self.nominal_matrix_error1 = [
            '2.7280', '8.5894', '0.5460', '1.0012',
            '-1.3651', '-3.5532', '-2.3601', '-0.9839']
        self.nominal_intstrengths_error1 = [
            '0.7146', '1.2344', '-0.2809', '-0.4783']
        self.nominal_opticsparam_error1 = ['0.0', '0.0']

        # Attributes to simulate matrix invertion errors
        self.magnetfams_ordering_error2 = ('QF', 'QD')
        self.magnetfams_focusing_error2 = ('QF')
        self.magnetfams_defocusing_error2 = ('QD')
        self.nominal_matrix_error2 = [0.0, 2, 0.1, 4]
        self.nominal_intstrengths_error2 = [0.3, -1.5]

        # Attributes to simulate value errors
        self.magnetfams_ordering_error3 = ()
        self.magnetfams_focusing_error3 = ()
        self.magnetfams_defocusing_error3 = ()
        self.nominal_matrix_error3 = [2.7280, 8.5894, 4.2995, 0.5377,
                                      1.0906, 2.0004, 0.5460, 1.0012,
                                      -1.3651, -3.5532, -1.7657, -2.3652,
                                      -4.7518, -1.9781, -2.3601]
        self.nominal_opticsparam_error3 = [0.0, 0.0, 0.0]

        # Attributes to test correction with some families, not all
        self.magnetfams_focusing_somefams = ('QFA', 'QFB')
        self.magnetfams_defocusing_somefams = ('QDA', 'QDB2', 'QDB1')

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            OpticsCorr, PUB_INTERFACE, print_flag=True)
        self.assertTrue(valid)

    def test_type_errors(self):
        """Test raise type errors."""
        with self.assertRaises(TypeError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_error1,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(TypeError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_error1,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(TypeError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_error1)

        with self.assertRaises(TypeError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_error1,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(TypeError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_error1,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(TypeError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_error1,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_ok)

    def test_matrix_invertion_errors(self):
        """Test raise exceptions on matrix invertion errors."""
        with self.assertRaises(Exception):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_error2,
                self.nominal_matrix_error2,
                self.nominal_intstrengths_error2,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_error2,
                self.magnetfams_defocusing_error2)

    def test_value_errors(self):
        """Test raise value errors."""
        with self.assertRaises(ValueError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_error3,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(ValueError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_error3,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(ValueError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_error3,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(ValueError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_error3,
                self.magnetfams_defocusing_ok)

        with self.assertRaises(ValueError):
            self.opticscorr = OpticsCorr(
                self.magnetfams_ordering_ok,
                self.nominal_matrix_ok,
                self.nominal_intstrengths_ok,
                self.nominal_opticsparam_ok,
                self.magnetfams_focusing_ok,
                self.magnetfams_defocusing_error3)

    def test_magnetfams_ordering(self):
        """Test magnetfams_ordering property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.magnetfams_ordering
        self.assertIsInstance(propty, tuple)
        for item in propty:
            self.assertIsInstance(item, str)
        self.assertGreaterEqual(len(propty), 1)

    def test_magnetfams_focusing(self):
        """Test test_magnetfams_focusing property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.magnetfams_focusing
        self.assertIsInstance(propty, tuple)
        for item in propty:
            self.assertIsInstance(item, str)
        self.assertGreaterEqual(len(propty), 1)

    def test_magnetfams_defocusing(self):
        """Test test_magnetfams_defocusing property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.magnetfams_defocusing
        self.assertIsInstance(propty, tuple)
        for item in propty:
            self.assertIsInstance(item, str)
        self.assertGreaterEqual(len(propty), 1)

    def test_nominal_matrix(self):
        """Test nominal_matrix property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.nominal_matrix
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 2)
        self.assertEqual(propty.shape[1],
                         len(self.opticscorr.magnetfams_ordering))

    def test_nominal_intstrengths(self):
        """Test nominal_strengths property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.nominal_intstrengths
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 1)
        self.assertEqual(propty.shape[1],
                         len(self.opticscorr.magnetfams_ordering))

    def test_nominal_opticsparam(self):
        """Test nominal_opticsparam property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.nominal_opticsparam
        self.assertIsInstance(propty, np.ndarray)
        self.assertTrue(propty.shape, (2, 1))

    def test_matrix_add_svd(self):
        """Test matrix_add_svd property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.matrix_add_svd
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 2)
        self.assertEqual(propty.shape[1],
                         len(self.opticscorr.magnetfams_focusing) +
                         len(self.opticscorr.magnetfams_defocusing))

    def test_matrix_prop_svd(self):
        """Test matrix_prop_svd property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.matrix_prop_svd
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 2)
        self.assertEqual(propty.shape[1],
                         len(self.opticscorr.magnetfams_focusing) +
                         len(self.opticscorr.magnetfams_defocusing))

    def test_matrix_add_2knobs(self):
        """Test matrix_add_2knobs property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.matrix_add_2knobs
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 2)
        self.assertEqual(propty.shape[1], 2)

    def test_matrix_prop_2knobs(self):
        """Test matrix_prop_2knobs property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.matrix_prop_2knobs
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 2)
        self.assertEqual(propty.shape[1], 2)

    def test_inv_matrix_add_svd(self):
        """Test inverse_matrix_add_svd property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.inverse_matrix_add_svd
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0],
                         len(self.opticscorr.magnetfams_focusing) +
                         len(self.opticscorr.magnetfams_defocusing))
        self.assertEqual(propty.shape[1], 2)
        umat, smat, vmat = np.linalg.svd(self.opticscorr.matrix_add_svd,
                                         full_matrices=False)
        self.assertListEqual(
            list(propty.flatten()),
            list(np.dot(np.dot(vmat.T, np.diag(1/smat)), umat.T).flatten()))

    def test_inv_matrix_prop_svd(self):
        """Test inverse_matrix_prop_svd property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.inverse_matrix_prop_svd
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0],
                         len(self.opticscorr.magnetfams_focusing) +
                         len(self.opticscorr.magnetfams_defocusing))
        self.assertEqual(propty.shape[1], 2)
        umat, smat, vmat = np.linalg.svd(self.opticscorr.matrix_prop_svd,
                                         full_matrices=False)
        self.assertListEqual(
            list(propty.flatten()),
            list(np.dot(np.dot(vmat.T, np.diag(1/smat)), umat.T).flatten()))

    def test_inv_matrix_add_2knobs(self):
        """Test inverse_matrix_add_2knobs property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.inverse_matrix_add_2knobs
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 2)
        self.assertEqual(propty.shape[1], 2)
        umat, smat, vmat = np.linalg.svd(self.opticscorr.matrix_add_2knobs,
                                         full_matrices=False)
        self.assertListEqual(
            list(propty.flatten()),
            list(np.dot(np.dot(vmat.T, np.diag(1/smat)), umat.T).flatten()))

    def test_inv_matrix_prop_2knobs(self):
        """Test inverse_matrix_prop_2knobs property."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        propty = self.opticscorr.inverse_matrix_prop_2knobs
        self.assertIsInstance(propty, np.ndarray)
        self.assertEqual(propty.shape[0], 2)
        self.assertEqual(propty.shape[1], 2)
        umat, smat, vmat = np.linalg.svd(self.opticscorr.matrix_prop_2knobs,
                                         full_matrices=False)
        self.assertListEqual(
            list(propty.flatten()),
            list(np.dot(np.dot(vmat.T, np.diag(1/smat)), umat.T).flatten()))

    def test_calc_dintstr_allfams(self):
        """Test calculate_delta_intstrengths function (all families)."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        delta_opticsparam = [0.01, 0.01]

        # additional method
        delta_intstrengths = self.opticscorr.calculate_delta_intstrengths(
            method=1, grouping='svd', delta_opticsparam=delta_opticsparam)
        expected = [0.00027307, 0.00125755, 0.00063636, -0.00106541,
                    -0.00213666, -0.00032148, -0.00105963, -0.00015762]
        for idx, data in enumerate(delta_intstrengths):
            self.assertAlmostEqual(data, expected[idx])

        delta_intstrengths = self.opticscorr.calculate_delta_intstrengths(
            method=1, grouping='2knobs', delta_opticsparam=delta_opticsparam)
        expected = [0.00110325, 0.00110325, 0.00110325, -0.00139674,
                    -0.00139674, -0.00139674, -0.00139674, -0.00139674]
        for idx, data in enumerate(delta_intstrengths):
            self.assertAlmostEqual(data, expected[idx])

        # proportional method
        delta_intstrengths = self.opticscorr.calculate_delta_intstrengths(
            method=0, grouping='svd', delta_opticsparam=delta_opticsparam)
        expected = [-0.00052788, 0.00164248, 0.00093635, -0.0006387,
                    -0.00196284, -0.00147348, -0.00097403, -0.00072931]
        for idx, data in enumerate(delta_intstrengths):
            self.assertAlmostEqual(data, expected[idx])

        delta_intstrengths = self.opticscorr.calculate_delta_intstrengths(
            method=0, grouping='2knobs', delta_opticsparam=delta_opticsparam)
        expected = [0.00077053, 0.00133102, 0.00133102, -0.00104162,
                    -0.00128895, -0.00219475, -0.00128895, -0.00219475]
        for idx, data in enumerate(delta_intstrengths):
            self.assertAlmostEqual(data, expected[idx])

    def test_calc_dintstr_somefams(self):
        """Test calculate_delta_intstrengths function (5 families)."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_somefams,
                                     self.magnetfams_defocusing_somefams)

        delta_opticsparam = [0.01, 0.01]

        delta_intstrengths = self.opticscorr.calculate_delta_intstrengths(
            method=1, grouping='svd', delta_opticsparam=delta_opticsparam)
        expected = [0.00034033, 0.0015503, 0.,
                    -0.00127996, -0.00256688, -0.00037835, 0., 0.]
        for idx, data in enumerate(delta_intstrengths):
            self.assertAlmostEqual(data, expected[idx])

    def test_calc_opticsparam(self):
        """Test calculate_opticsparam function."""
        self.opticscorr = OpticsCorr(self.magnetfams_ordering_ok,
                                     self.nominal_matrix_ok,
                                     self.nominal_intstrengths_ok,
                                     self.nominal_opticsparam_ok,
                                     self.magnetfams_focusing_ok,
                                     self.magnetfams_defocusing_ok)

        delta_intstrengths = [5.23801198e-04, 1.91863308e-03,
                              9.65048343e-04, -6.54746947e-04,
                              -1.31156341e-03, 3.07649982e-05,
                              -6.49807134e-04, 1.76177711e-05]
        opticsparam = self.opticscorr.calculate_opticsparam(delta_intstrengths)
        expected = [0.02, 0]
        for idx, data in enumerate(opticsparam):
            self.assertAlmostEqual(data, expected[idx])


if __name__ == "__main__":
    unittest.main()
