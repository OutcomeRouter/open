import os, sys
sys.path.insert(0, os.getcwd())
from solution import *

assert snake_to_camel('android_tv') == 'AndroidTv'
assert snake_to_camel('google_pixel') == 'GooglePixel'
assert snake_to_camel('apple_watch') == 'AppleWatch'
print('ok')
