import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert check_monthnumb_number(5)==True
assert check_monthnumb_number(2)==False
assert check_monthnumb_number(6)==False
print('ok')
