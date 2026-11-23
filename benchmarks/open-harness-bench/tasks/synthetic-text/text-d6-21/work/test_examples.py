from solution import *

assert transform('a  ') == '  a'
assert transform('a \n World \n Queue \n 2026 \n a \n hello \n zzzz  ') == '  \n \n \n \n \n \n a a #### zzzz dlrow eueuq olleh'
assert transform('  hello zzzz zzzz hello Queue bookkeeper ') == '   zzzz zzzz eueuq olleh olleh repeekkoob'
print('ok')
