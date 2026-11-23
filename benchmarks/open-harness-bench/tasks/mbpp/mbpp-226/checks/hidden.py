import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert odd_values_string('abcdef') == 'ace'
assert odd_values_string('python') == 'pto'
assert odd_values_string('data') == 'dt'
assert odd_values_string('lambs') == 'lms'
print('ok')
