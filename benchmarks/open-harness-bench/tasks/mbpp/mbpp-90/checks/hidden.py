import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert len_log(["python","PHP","bigdata"]) == 7
assert len_log(["a","ab","abc"]) == 3
assert len_log(["small","big","tall"]) == 5
print('ok')
