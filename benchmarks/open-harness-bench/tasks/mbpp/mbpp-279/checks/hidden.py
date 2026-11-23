import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert is_num_decagonal(3) == 27
assert is_num_decagonal(7) == 175
assert is_num_decagonal(10) == 370
print('ok')
