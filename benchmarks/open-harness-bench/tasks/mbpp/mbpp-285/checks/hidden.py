import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert text_match_two_three("ac")==(False)
assert text_match_two_three("dc")==(False)
assert text_match_two_three("abbbba")==(True)
print('ok')
