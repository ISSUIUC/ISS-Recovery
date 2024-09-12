import requests
import numpy as np

url = 'http://127.0.0.1:5000/energetic/sim'

RCM_VOLUME: float = (np.pi * (1)) * 10.9375 # in^3 (Values from seongyong)

myobj = {
    "name": "Test sim",
    "dimensions": {
        "diameter": 2.94,
        "length": 18
    },
    "target_pressure": 16,
    "efficiency": [0.95]
}

x = requests.post(url, json = myobj)

print(x.text)