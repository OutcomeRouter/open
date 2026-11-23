import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert check_integer("python")==False
assert check_integer("1")==True
assert check_integer("12345")==True
print('ok')
