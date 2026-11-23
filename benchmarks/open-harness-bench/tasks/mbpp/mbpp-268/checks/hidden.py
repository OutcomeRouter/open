import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert find_star_num(3) == 37
assert find_star_num(4) == 73
assert find_star_num(5) == 121
print('ok')
