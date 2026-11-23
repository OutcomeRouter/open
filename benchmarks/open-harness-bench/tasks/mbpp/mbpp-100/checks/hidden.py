import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert next_smallest_palindrome(99)==101
assert next_smallest_palindrome(1221)==1331
assert next_smallest_palindrome(120)==121
print('ok')
