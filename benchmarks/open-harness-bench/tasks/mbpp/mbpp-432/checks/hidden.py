import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert median_trapezium(15,25,35)==20
assert median_trapezium(10,20,30)==15
assert median_trapezium(6,9,4)==7.5
print('ok')
