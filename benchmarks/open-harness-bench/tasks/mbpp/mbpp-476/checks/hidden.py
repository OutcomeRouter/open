import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert big_sum([1,2,3]) == 4
assert big_sum([-1,2,3,4]) == 3
assert big_sum([2,3,6]) == 8
print('ok')
