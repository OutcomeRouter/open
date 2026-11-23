import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert dog_age(12)==61
assert dog_age(15)==73
assert dog_age(24)==109
print('ok')
