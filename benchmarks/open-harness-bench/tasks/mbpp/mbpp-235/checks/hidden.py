import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert even_bit_set_number(10) == 10
assert even_bit_set_number(20) == 30
assert even_bit_set_number(30) == 30
print('ok')
