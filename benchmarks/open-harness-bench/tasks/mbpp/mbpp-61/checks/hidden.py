import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count_Substrings('112112') == 6
assert count_Substrings('111') == 6
assert count_Substrings('1101112') == 12
print('ok')
