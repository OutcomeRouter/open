import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert opposite_Signs(1,-2) == True
assert opposite_Signs(3,2) == False
assert opposite_Signs(-10,-10) == False
assert opposite_Signs(-2,2) == True
print('ok')
