import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert is_sublist([2,4,3,5,7],[3,7])==False
assert is_sublist([2,4,3,5,7],[4,3])==True
assert is_sublist([2,4,3,5,7],[1,6])==False
print('ok')
