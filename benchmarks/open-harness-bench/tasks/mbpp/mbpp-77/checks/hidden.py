import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert is_Diff (12345) == False
assert is_Diff(1212112) == True
assert is_Diff(1212) == False
print('ok')
