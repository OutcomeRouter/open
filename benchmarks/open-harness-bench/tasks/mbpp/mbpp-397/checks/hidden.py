import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert median_numbers(25,55,65)==55.0
assert median_numbers(20,10,30)==20.0
assert median_numbers(15,45,75)==45.0
print('ok')
