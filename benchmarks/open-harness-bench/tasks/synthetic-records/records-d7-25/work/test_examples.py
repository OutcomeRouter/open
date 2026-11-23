from solution import *

assert query([{'id': 27, 'name': 'bo', 'status': 'paused', 'region': 'apac', 'amount': 60}]) == []
assert query([{'id': 3, 'name': 'ana', 'status': 'closed', 'region': 'apac', 'amount': 120}, {'id': 92, 'name': 'cy', 'status': 'closed', 'region': 'eu', 'amount': 138}, {'id': 4, 'name': 'bo', 'status': 'closed', 'region': 'eu', 'amount': 124}, {'id': 12, 'name': 'fay', 'status': 'active', 'region': 'us', 'amount': 51}, {'id': 41, 'name': 'dee', 'status': 'active', 'region': 'us', 'amount': 30}, {'id': 65, 'name': 'ana', 'status': 'closed', 'region': 'eu', 'amount': 40}, {'id': 42, 'name': 'dee', 'status': 'active', 'region': 'us', 'amount': 12}]) == [{'id': 12, 'name': 'fay', 'amount': 50, 'tier': 'silver'}]
assert query([]) == []
print('ok')
