from solution import *

assert query([{'id': 31, 'name': 'eli', 'status': 'paused', 'region': 'eu', 'amount': 30}, {'id': 3, 'name': 'fay', 'status': 'closed', 'region': 'us', 'amount': 20}]) == []
assert query([{'id': 34, 'name': 'eli', 'status': 'active', 'region': 'apac', 'amount': 110}, {'id': 6, 'name': 'fay', 'status': 'active', 'region': 'apac', 'amount': 5}, {'id': 40, 'name': 'eli', 'status': 'paused', 'region': 'us', 'amount': 107}]) == [{'id': 34, 'name': 'eli', 'status': 'active', 'region': 'apac', 'amount': 110, 'tier': 'gold'}]
assert query([{'id': 23, 'name': 'eli', 'status': 'closed', 'region': 'apac', 'amount': 15}, {'id': 14, 'name': 'fay', 'status': 'paused', 'region': 'apac', 'amount': 85}, {'id': 74, 'name': 'cy', 'status': 'active', 'region': 'us', 'amount': 79}]) == [{'id': 14, 'name': 'fay', 'status': 'paused', 'region': 'apac', 'amount': 90, 'tier': 'silver'}, {'id': 74, 'name': 'cy', 'status': 'active', 'region': 'us', 'amount': 80, 'tier': 'silver'}]
print('ok')
