import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert check_distinct((1, 4, 5, 6, 1, 4)) == False
assert check_distinct((1, 4, 5, 6)) == True
assert check_distinct((2, 3, 4, 5, 6)) == True
print('ok')
