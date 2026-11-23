import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert square_Sum(2) == 10
assert square_Sum(3) == 35
assert square_Sum(4) == 84
print('ok')
