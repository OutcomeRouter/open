import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert reverse_vowels("Python") == "Python"
assert reverse_vowels("USA") == "ASU"
assert reverse_vowels("ab") == "ab"
print('ok')
