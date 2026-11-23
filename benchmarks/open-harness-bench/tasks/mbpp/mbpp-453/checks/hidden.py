import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert sumofFactors(18) == 26
assert sumofFactors(30) == 48
assert sumofFactors(6) == 8
print('ok')
