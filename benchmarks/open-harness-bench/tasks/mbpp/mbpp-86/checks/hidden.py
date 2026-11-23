import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert centered_hexagonal_number(10) == 271
assert centered_hexagonal_number(2) == 7
assert centered_hexagonal_number(9) == 217
print('ok')
