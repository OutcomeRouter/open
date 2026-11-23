import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert divisor(15) == 4
assert divisor(12) == 6
assert divisor(9) == 3
print('ok')
