import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert even_binomial_Coeff_Sum(4) == 8
assert even_binomial_Coeff_Sum(6) == 32
assert even_binomial_Coeff_Sum(2) == 2
print('ok')
