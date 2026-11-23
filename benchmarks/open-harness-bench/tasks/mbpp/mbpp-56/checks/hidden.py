import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert check(70) == False
assert check(23) == False
assert check(73) == True
print('ok')
