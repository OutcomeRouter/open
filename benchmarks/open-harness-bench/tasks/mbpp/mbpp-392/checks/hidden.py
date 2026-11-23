import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert get_max_sum(60) == 106
assert get_max_sum(10) == 12
assert get_max_sum(2) == 2
print('ok')
