from solution import *

assert query([{'id': 78, 'name': 'fay', 'status': 'closed', 'region': 'apac', 'amount': 63}]) == []
assert query([{'id': 94, 'name': 'ana', 'status': 'closed', 'region': 'us', 'amount': 77}, {'id': 32, 'name': 'dee', 'status': 'closed', 'region': 'us', 'amount': 100}, {'id': 37, 'name': 'ana', 'status': 'paused', 'region': 'eu', 'amount': 80}, {'id': 93, 'name': 'cy', 'status': 'paused', 'region': 'us', 'amount': 132}]) == []
assert query([{'id': 20, 'name': 'fay', 'status': 'closed', 'region': 'us', 'amount': 42}, {'id': 70, 'name': 'ana', 'status': 'closed', 'region': 'eu', 'amount': 31}]) == []
print('ok')
