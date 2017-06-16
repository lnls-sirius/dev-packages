#!/usr/bin/env python3

import inspect
import unittest
import tests_controller
import tests_pwrsupply

modules = [tests_controller, tests_pwrsupply]


def get_test_classes(module_name):
    test_classes = []
    for name,symbol in inspect.getmembers(module_name):
        try:
            obj = symbol()
            if isinstance(obj, unittest.TestCase):
                methods = [method for method in dir(obj) if callable(getattr(obj, method)) and method.startswith('test_')]
                if methods:
                    test_classes.append(symbol)
        except:
            pass
    return test_classes

def print_module_name(module):
    text, _ = str(module).split(sep='from')
    _, text=text.split('module')
    text=text.strip()
    print();
    print('*'*len(text))
    print(text);
    print('*'*len(text))
    print()

def run_tests():

    for module in modules:
        print_module_name(module)
        test_classes = get_test_classes(module)
        loader = unittest.TestLoader()
        for test_class in test_classes:
            #print('-'*len(str(test_class))); print(test_class)
            suite = loader.loadTestsFromTestCase(test_class)
            b_suite = unittest.TestSuite(tests=[suite,])
            runner = unittest.TextTestRunner()
            results = runner.run(b_suite)
            if results.failures or results.errors:
                return
        print(end='\n\n')

if __name__ == '__main__':
    run_tests()
