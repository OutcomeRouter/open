from solution import *

assert transform('a Data42 hello') == 'a_data42_hello'
assert transform('hello \n 9 \n hello ') == 'hello_\n_9'
assert transform(' 0u2QBB Data42 World hello Data42 Queue hello hello hello  ') == '0u2qbb_data42_world_hello_queue'
print('ok')
