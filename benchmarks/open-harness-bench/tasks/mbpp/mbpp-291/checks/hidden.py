import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count_no_of_ways(2, 4) == 16
assert count_no_of_ways(3, 2) == 6
assert count_no_of_ways(4, 4) == 228
print('ok')
