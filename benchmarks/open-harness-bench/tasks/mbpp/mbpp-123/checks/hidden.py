import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert amicable_numbers_sum(999)==504
assert amicable_numbers_sum(9999)==31626
assert amicable_numbers_sum(99)==0
print('ok')
