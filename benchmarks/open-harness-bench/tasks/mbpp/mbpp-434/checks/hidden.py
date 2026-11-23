import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert text_match_one("ac")==False
assert text_match_one("dc")==False
assert text_match_one("abba")==True
print('ok')
