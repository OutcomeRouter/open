import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert largest_neg([1,2,3,-4,-6]) == -6
assert largest_neg([1,2,3,-8,-9]) == -9
assert largest_neg([1,2,3,4,-1]) == -1
print('ok')
