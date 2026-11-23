import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert odd_Equivalent("011001",6) == 3
assert odd_Equivalent("11011",5) == 4
assert odd_Equivalent("1010",4) == 2
print('ok')
