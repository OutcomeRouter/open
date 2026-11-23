import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert remove_lowercase("PYTHon")==('PYTH')
assert remove_lowercase("FInD")==('FID')
assert remove_lowercase("STRinG")==('STRG')
print('ok')
