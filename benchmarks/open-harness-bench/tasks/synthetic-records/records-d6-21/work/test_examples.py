from solution import *

assert query([{'id': 95, 'name': 'bo', 'status': 'closed', 'region': 'apac', 'amount': 45}]) == []
assert query([{'id': 16, 'name': 'dee', 'status': 'active', 'region': 'eu', 'amount': 36}, {'id': 81, 'name': 'dee', 'status': 'active', 'region': 'eu', 'amount': 155}, {'id': 59, 'name': 'bo', 'status': 'active', 'region': 'eu', 'amount': 104}]) == [{'id': 81, 'name': 'dee', 'amount': 160, 'tier': 'gold'}, {'id': 59, 'name': 'bo', 'amount': 100, 'tier': 'gold'}, {'id': 16, 'name': 'dee', 'amount': 40, 'tier': 'bronze'}]
assert query([{'id': 8, 'name': 'cy', 'status': 'closed', 'region': 'eu', 'amount': 45}, {'id': 12, 'name': 'eli', 'status': 'closed', 'region': 'apac', 'amount': 69}, {'id': 53, 'name': 'eli', 'status': 'active', 'region': 'apac', 'amount': 114}]) == [{'id': 53, 'name': 'eli', 'amount': 110, 'tier': 'gold'}]
print('ok')
