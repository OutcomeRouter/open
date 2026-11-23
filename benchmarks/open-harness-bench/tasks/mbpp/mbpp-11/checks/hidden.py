import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert remove_Occ("hello","l") == "heo"
assert remove_Occ("abcda","a") == "bcd"
assert remove_Occ("PHP","P") == "H"
print('ok')
