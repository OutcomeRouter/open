import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert eulerian_num(3, 1) == 4
assert eulerian_num(4, 1) == 11
assert eulerian_num(5, 3) == 26
print('ok')
