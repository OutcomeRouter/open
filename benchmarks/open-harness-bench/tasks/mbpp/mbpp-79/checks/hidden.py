import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert word_len("Hadoop") == False
assert word_len("great") == True
assert word_len("structure") == True
print('ok')
