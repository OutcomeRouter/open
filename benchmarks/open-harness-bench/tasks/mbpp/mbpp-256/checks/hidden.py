import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert count_Primes_nums(5) == 2
assert count_Primes_nums(10) == 4
assert count_Primes_nums(100) == 25
print('ok')
