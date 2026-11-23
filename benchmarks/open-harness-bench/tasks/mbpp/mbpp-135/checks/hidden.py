import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert hexagonal_num(10) == 190
assert hexagonal_num(5) == 45
assert hexagonal_num(7) == 91
print('ok')
