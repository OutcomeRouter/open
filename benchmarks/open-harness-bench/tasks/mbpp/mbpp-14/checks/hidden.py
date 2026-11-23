import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert find_Volume(10,8,6) == 240
assert find_Volume(3,2,2) == 6
assert find_Volume(1,2,1) == 1
print('ok')
