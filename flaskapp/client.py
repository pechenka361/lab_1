import requests
import os
import base64

img_data = None
path = os.path.join("./static", "image0008.png")

with open(path, "rb") as fh:
    img_data = fh.read()
    b64 = base64.b64encode(img_data)

jsondata = {"imagebin": b64.decode("utf-8")}
res = requests.post("http://127.0.0.1:5000/apinet", json=jsondata)
if res.ok:
    print(res.json())

try:
    r = requests.get('http://127.0.0.1:5000/apixml')
    print(r.status_code)
    if r.status_code != 200:
        exit(1)
    print(r.text)
except:
    exit(1)
