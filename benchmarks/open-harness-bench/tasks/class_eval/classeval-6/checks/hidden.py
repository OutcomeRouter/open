import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

import unittest

class AvgPartitionTestSetNum(unittest.TestCase):
    def test_setNum(self):
        a = AvgPartition([1, 2, 3, 4], 2)
        self.assertEqual(a.setNum(), (2, 0))

    def test_setNum_2(self):
        a = AvgPartition([1, 2, 3, 4, 5], 2)
        self.assertEqual(a.setNum(), (2, 1))

    def test_setNum_3(self):
        a = AvgPartition([1, 2, 3, 4, 5], 3)
        self.assertEqual(a.setNum(), (1, 2))

    def test_setNum_4(self):
        a = AvgPartition([1, 2, 3, 4, 5], 4)
        self.assertEqual(a.setNum(), (1, 1))

    def test_setNum_5(self):
        a = AvgPartition([1, 2, 3, 4, 5], 5)
        self.assertEqual(a.setNum(), (1, 0))

class AvgPartitionTestGet(unittest.TestCase):

    def test_get(self):
        a = AvgPartition([1, 2, 3, 4], 2)
        self.assertEqual(a.get(0), [1, 2])

    def test_get_2(self):
        a = AvgPartition([1, 2, 3, 4], 2)
        self.assertEqual(a.get(1), [3, 4])

    def test_get_3(self):
        a = AvgPartition([1, 2, 3, 4, 5], 2)
        self.assertEqual(a.get(0), [1, 2, 3])

    def test_get_4(self):
        a = AvgPartition([1, 2, 3, 4, 5], 2)
        self.assertEqual(a.get(1), [4, 5])

    def test_get_5(self):
        a = AvgPartition([1, 2, 3, 4, 5], 3)
        self.assertEqual(a.get(0), [1, 2])

class AvgPartitionTestMain(unittest.TestCase):
    def test_main(self):
        a = AvgPartition([1, 2, 3, 4], 2)
        self.assertEqual(a.setNum(), (2, 0))
        self.assertEqual(a.get(0), [1, 2])

import unittest as _ut
_s = _ut.TestSuite()
_s.addTests(_ut.defaultTestLoader.loadTestsFromTestCase(AvgPartitionTestSetNum))
_s.addTests(_ut.defaultTestLoader.loadTestsFromTestCase(AvgPartitionTestGet))
_s.addTests(_ut.defaultTestLoader.loadTestsFromTestCase(AvgPartitionTestMain))
_r = _ut.TextTestRunner(verbosity=1).run(_s)
sys.exit(0 if _r.wasSuccessful() else 1)
print('ok')
