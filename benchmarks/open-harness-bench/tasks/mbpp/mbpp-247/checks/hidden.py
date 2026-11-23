import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert lps("TENS FOR TENS") == 5
assert lps("CARDIO FOR CARDS") == 7
assert lps("PART OF THE JOURNEY IS PART") == 9
print('ok')
