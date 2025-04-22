import requests

try:
    r = requests.get('http://127.0.0.1:5000/hello_world')
    print(r.status_code)
    if r.status_code != 200:
        exit(1)
    print(r.text)
except:
    exit(1)
