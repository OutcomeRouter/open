import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert lateralsurface_cube(5)==100
assert lateralsurface_cube(9)==324
assert lateralsurface_cube(10)==400
print('ok')
