import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert set_left_most_unset_bit(10) == 14
assert set_left_most_unset_bit(12) == 14
assert set_left_most_unset_bit(15) == 15
print('ok')
