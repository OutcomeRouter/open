import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert insert_element(['Red', 'Green', 'Black'] ,'c')==['c', 'Red', 'c', 'Green', 'c', 'Black']
assert insert_element(['python', 'java'] ,'program')==['program', 'python', 'program', 'java']
assert insert_element(['happy', 'sad'] ,'laugh')==['laugh', 'happy', 'laugh', 'sad']
print('ok')
