import requests

r = requests.get('http://localhost:5000/')
data_to_r = requests.get('http://localhost:5000/data_to')
print(r.status_code)
print(r.text)
print(data_to_r.status_code)
print(data_to_r.text) 