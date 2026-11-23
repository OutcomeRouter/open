import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert string_to_list("python programming")==['python','programming']
assert string_to_list("lists tuples strings")==['lists','tuples','strings']
assert string_to_list("write a program")==['write','a','program']
print('ok')
