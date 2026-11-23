import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert concatenate_tuple(("ID", "is", 4, "UTS") ) == 'ID-is-4-UTS'
assert concatenate_tuple(("QWE", "is", 4, "RTY") ) == 'QWE-is-4-RTY'
assert concatenate_tuple(("ZEN", "is", 4, "OP") ) == 'ZEN-is-4-OP'
print('ok')
