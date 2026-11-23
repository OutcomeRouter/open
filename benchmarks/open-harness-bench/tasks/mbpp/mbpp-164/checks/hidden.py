import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert are_equivalent(36, 57) == False
assert are_equivalent(2, 4) == False
assert are_equivalent(23, 47) == True
print('ok')
