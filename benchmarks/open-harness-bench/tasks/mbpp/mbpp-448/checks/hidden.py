import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert cal_sum(9) == 49
assert cal_sum(10) == 66
assert cal_sum(11) == 88
print('ok')
