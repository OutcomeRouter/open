import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert highest_Power_of_2(10) == 8
assert highest_Power_of_2(19) == 16
assert highest_Power_of_2(32) == 32
print('ok')
