import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert find_Max_Num([1,2,3]) == 321
assert find_Max_Num([4,5,6,1]) == 6541
assert find_Max_Num([1,2,3,9]) == 9321
print('ok')
