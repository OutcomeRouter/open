import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert get_total_number_of_sequences(10, 4) == 4
assert get_total_number_of_sequences(5, 2) == 6
assert get_total_number_of_sequences(16, 3) == 84
print('ok')
