import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert decimal_to_binary(8) == '1000'
assert decimal_to_binary(18) == '10010'
assert decimal_to_binary(7) == '111'
print('ok')
