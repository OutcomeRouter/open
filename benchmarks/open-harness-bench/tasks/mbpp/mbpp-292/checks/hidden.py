import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert find(10,3) == 3
assert find(4,2) == 2
assert find(20,5) == 4
print('ok')
