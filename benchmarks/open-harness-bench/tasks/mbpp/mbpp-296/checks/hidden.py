import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert get_Inv_Count([1,20,6,4,5]) == 5
assert get_Inv_Count([1,2,1]) == 1
assert get_Inv_Count([1,2,5,6,1]) == 3
print('ok')
