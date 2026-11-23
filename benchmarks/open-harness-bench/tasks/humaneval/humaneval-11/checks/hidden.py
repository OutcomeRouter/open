import os, sys
sys.path.insert(0, os.getcwd())
from solution import *



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('111000', '101010') == '010010'
    assert candidate('1', '1') == '0'
    assert candidate('0101', '0000') == '0101'


check(string_xor)
print('ok')
