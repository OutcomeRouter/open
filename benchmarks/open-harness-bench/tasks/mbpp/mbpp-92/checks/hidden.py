import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert is_undulating(1212121) == True
assert is_undulating(1991) == False
assert is_undulating(121) == True
print('ok')
