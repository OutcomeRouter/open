import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert find_lucas(9) == 76
assert find_lucas(4) == 7
assert find_lucas(3) == 4
print('ok')
