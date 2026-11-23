import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert max_Abs_Diff((2,1,5,3)) == 4
assert max_Abs_Diff((9,3,2,5,1)) == 8
assert max_Abs_Diff((3,2,1)) == 2
print('ok')
