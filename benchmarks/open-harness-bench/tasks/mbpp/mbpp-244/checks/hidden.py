import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert next_Perfect_Square(35) == 36
assert next_Perfect_Square(6) == 9
assert next_Perfect_Square(9) == 16
print('ok')
