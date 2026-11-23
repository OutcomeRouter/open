import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert volume_cube(3)==27
assert volume_cube(2)==8
assert volume_cube(5)==125
print('ok')
