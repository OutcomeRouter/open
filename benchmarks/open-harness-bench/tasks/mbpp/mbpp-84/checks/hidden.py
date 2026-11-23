import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert sequence(10) == 6
assert sequence(2) == 1
assert sequence(3) == 2
print('ok')
