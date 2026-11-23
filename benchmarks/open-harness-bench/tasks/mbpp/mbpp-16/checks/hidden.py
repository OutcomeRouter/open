import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert text_lowercase_underscore("aab_cbbbc")==(True)
assert text_lowercase_underscore("aab_Abbbc")==(False)
assert text_lowercase_underscore("Aaab_abbbc")==(False)
print('ok')
