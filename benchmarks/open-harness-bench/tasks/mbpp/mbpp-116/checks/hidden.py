import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert tuple_to_int((1,2,3))==123
assert tuple_to_int((4,5,6))==456
assert tuple_to_int((5,6,7))==567
print('ok')
