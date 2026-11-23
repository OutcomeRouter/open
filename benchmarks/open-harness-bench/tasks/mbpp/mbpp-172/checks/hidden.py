import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count_occurance("letstdlenstdporstd") == 3
assert count_occurance("truststdsolensporsd") == 1
assert count_occurance("makestdsostdworthit") == 2
assert count_occurance("stds") == 1
assert count_occurance("") == 0
print('ok')
