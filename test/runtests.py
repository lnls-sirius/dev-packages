#!/usr/bin/env python3

import unittest
import test_beam_lifetime


suite_list = []
suite_list.append(test_beam_lifetime.get_suite())

tests = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(tests)
