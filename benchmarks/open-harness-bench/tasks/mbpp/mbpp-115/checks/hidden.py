import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert empty_dit([{},{},{}])==True
assert empty_dit([{1,2},{},{}])==False
assert empty_dit({})==True
print('ok')
