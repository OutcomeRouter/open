import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert validate(1234) == True
assert validate(51241) == False
assert validate(321) == True
print('ok')
