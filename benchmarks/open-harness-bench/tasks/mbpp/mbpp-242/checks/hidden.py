import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count_charac("python programming")==18
assert count_charac("language")==8
assert count_charac("words")==5
print('ok')
