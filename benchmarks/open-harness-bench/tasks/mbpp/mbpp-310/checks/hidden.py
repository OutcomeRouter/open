import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert string_to_tuple("python 3.0")==('p', 'y', 't', 'h', 'o', 'n', '3', '.', '0')
assert string_to_tuple("item1")==('i', 't', 'e', 'm', '1')
assert string_to_tuple("15.10")==('1', '5', '.', '1', '0')
print('ok')
