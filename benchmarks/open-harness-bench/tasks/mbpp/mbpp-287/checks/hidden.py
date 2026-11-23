import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert square_Sum(2) == 20
assert square_Sum(3) == 56
assert square_Sum(4) == 120
print('ok')
