import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count_integer([1,2,'abc',1.2]) == 2
assert count_integer([1,2,3]) == 3
assert count_integer([1,1.2,4,5.1]) == 2
print('ok')
