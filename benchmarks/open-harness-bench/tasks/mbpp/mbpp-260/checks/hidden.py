import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert newman_prime(3) == 7
assert newman_prime(4) == 17
assert newman_prime(5) == 41
print('ok')
