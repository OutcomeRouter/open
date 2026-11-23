import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert square_perimeter(10)==40
assert square_perimeter(5)==20
assert square_perimeter(4)==16
print('ok')
