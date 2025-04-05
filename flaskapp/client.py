import requests
import os
from io import BytesIO
import base64

img_data = None
path = os.path.join("./static", "image0008.png")

with open(path, "rb") as fh:
    img_data = fh.read()
    b64 = base64.b64encode(img_data)

jsondata = {"imagebin": b64.decode("utf-8")}
res = requests.post("http://localhost:5000/apinet", json=jsondata)
if res.ok:
    print(res.json())
