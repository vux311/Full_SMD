import requests

r = requests.post('http://localhost:9999/auth/login', json={'username':'gv1','password':'123456'})
print('status:', r.status_code)
print('headers:', r.headers)
print('body:', r.text)
