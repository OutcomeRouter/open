import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

import unittest


class ChandrasekharSieveTestGeneratePrimes(unittest.TestCase):
    def test_generate_primes_1(self):
        cs = ChandrasekharSieve(20)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])

    def test_generate_primes_2(self):
        cs = ChandrasekharSieve(18)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17])

    def test_generate_primes_3(self):
        cs = ChandrasekharSieve(15)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13])

    def test_generate_primes_4(self):
        cs = ChandrasekharSieve(10)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7])

    def test_generate_primes_5(self):
        cs = ChandrasekharSieve(1)
        res = cs.generate_primes()
        self.assertEqual(res, [])


class ChandrasekharSieveTestGetPrimes(unittest.TestCase):
    def test_get_primes_1(self):
        cs = ChandrasekharSieve(20)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])

    def test_get_primes_2(self):
        cs = ChandrasekharSieve(18)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17])

    def test_get_primes_3(self):
        cs = ChandrasekharSieve(15)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13])

    def test_get_primes_4(self):
        cs = ChandrasekharSieve(10)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7])

    def test_get_primes_5(self):
        cs = ChandrasekharSieve(1)
        res = cs.get_primes()
        self.assertEqual(res, [])


class ChandrasekharSieveTest(unittest.TestCase):
    def test_chandrasekharsieve(self):
        cs = ChandrasekharSieve(20)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])

import unittest as _ut
_s = _ut.TestSuite()
_s.addTests(_ut.defaultTestLoader.loadTestsFromTestCase(ChandrasekharSieveTestGeneratePrimes))
_s.addTests(_ut.defaultTestLoader.loadTestsFromTestCase(ChandrasekharSieveTestGetPrimes))
_s.addTests(_ut.defaultTestLoader.loadTestsFromTestCase(ChandrasekharSieveTest))
_r = _ut.TextTestRunner(verbosity=1).run(_s)
sys.exit(0 if _r.wasSuccessful() else 1)
print('ok')
