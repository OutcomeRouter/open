import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count([True,False,True]) == 2
assert count([False,False]) == 0
assert count([True,True,True]) == 3
print('ok')
