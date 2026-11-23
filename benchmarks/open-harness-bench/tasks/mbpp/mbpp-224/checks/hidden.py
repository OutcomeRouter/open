import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count_Set_Bits(2) == 1
assert count_Set_Bits(4) == 1
assert count_Set_Bits(6) == 2
print('ok')
