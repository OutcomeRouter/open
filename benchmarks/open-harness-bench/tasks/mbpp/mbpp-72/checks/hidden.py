import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert dif_Square(5) == True
assert dif_Square(10) == False
assert dif_Square(15) == True
print('ok')
