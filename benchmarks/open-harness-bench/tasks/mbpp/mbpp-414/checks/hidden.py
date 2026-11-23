import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert overlapping([1,2,3,4,5],[6,7,8,9]) == False
assert overlapping([1,2,3],[4,5,6]) == False
assert overlapping([1,4,5],[1,4,5]) == True
print('ok')
