import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert swap_numbers(10,20)==(20,10)
assert swap_numbers(15,17)==(17,15)
assert swap_numbers(100,200)==(200,100)
print('ok')
