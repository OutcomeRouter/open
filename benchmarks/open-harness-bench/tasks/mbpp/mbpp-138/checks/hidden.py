import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert is_Sum_Of_Powers_Of_Two(10) == True
assert is_Sum_Of_Powers_Of_Two(7) == False
assert is_Sum_Of_Powers_Of_Two(14) == True
print('ok')
