import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert is_octagonal(5) == 65
assert is_octagonal(10) == 280
assert is_octagonal(15) == 645
print('ok')
