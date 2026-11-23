import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert is_woodall(383) == True
assert is_woodall(254) == False
assert is_woodall(200) == False
print('ok')
