import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert first_Digit(123) == 1
assert first_Digit(456) == 4
assert first_Digit(12) == 1
print('ok')
