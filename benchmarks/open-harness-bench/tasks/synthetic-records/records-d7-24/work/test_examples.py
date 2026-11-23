from solution import *

assert query([]) == []
assert query([{'id': 14, 'name': 'ana', 'status': 'closed', 'region': 'eu', 'amount': 35}, {'id': 97, 'name': 'bo', 'status': 'closed', 'region': 'eu', 'amount': 15}, {'id': 50, 'name': 'bo', 'status': 'active', 'region': 'apac', 'amount': 114}, {'id': 18, 'name': 'eli', 'status': 'paused', 'region': 'eu', 'amount': 151}, {'id': 87, 'name': 'ana', 'status': 'active', 'region': 'eu', 'amount': 103}, {'id': 5, 'name': 'cy', 'status': 'active', 'region': 'eu', 'amount': 84}, {'id': 17, 'name': 'dee', 'status': 'paused', 'region': 'apac', 'amount': 63}]) == [{'id': 87, 'name': 'ana', 'status': 'active', 'region': 'eu', 'amount': 100, 'tier': 'gold'}, {'id': 5, 'name': 'cy', 'status': 'active', 'region': 'eu', 'amount': 80, 'tier': 'silver'}]
assert query([{'id': 92, 'name': 'eli', 'status': 'closed', 'region': 'apac', 'amount': 15}, {'id': 27, 'name': 'ana', 'status': 'active', 'region': 'us', 'amount': 34}, {'id': 53, 'name': 'bo', 'status': 'active', 'region': 'us', 'amount': 7}]) == []
print('ok')
