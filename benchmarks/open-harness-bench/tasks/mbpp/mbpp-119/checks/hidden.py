import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert search([1,1,2,2,3]) == 3
assert search([1,1,3,3,4,4,5,5,7,7,8]) == 8
assert search([1,2,2,3,3,4,4]) == 1
print('ok')
