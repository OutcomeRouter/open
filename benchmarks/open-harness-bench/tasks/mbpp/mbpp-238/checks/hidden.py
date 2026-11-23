import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert number_of_substrings("abc") == 6
assert number_of_substrings("abcd") == 10
assert number_of_substrings("abcde") == 15
print('ok')
