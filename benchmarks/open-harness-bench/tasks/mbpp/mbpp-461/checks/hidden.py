import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert upper_ctr('PYthon') == 1
assert upper_ctr('BigData') == 1
assert upper_ctr('program') == 0
print('ok')
