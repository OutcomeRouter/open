import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert sum_series(6) == 12
assert sum_series(10) == 30
assert sum_series(9) == 25
print('ok')
