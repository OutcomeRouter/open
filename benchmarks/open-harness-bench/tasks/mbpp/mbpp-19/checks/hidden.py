import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert test_duplicate(([1,2,3,4,5]))==False
assert test_duplicate(([1,2,3,4, 4]))==True
assert test_duplicate([1,1,2,2,3,3,4,4,5])==True
print('ok')
