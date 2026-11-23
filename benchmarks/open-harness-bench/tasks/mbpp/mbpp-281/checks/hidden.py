import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert all_unique([1,2,3]) == True
assert all_unique([1,2,1,2]) == False
assert all_unique([1,2,3,4,5]) == True
print('ok')
