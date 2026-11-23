import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert perimeter_pentagon(5) == 25
assert perimeter_pentagon(10) == 50
assert perimeter_pentagon(15) == 75
print('ok')
