import requests
from hashlib import md5

url = 'http://p3.pstatp.com/large/pgc-image/1534865137519e1f37339be'

response = requests.get(url)
print(md5(response.content).hexdigest())
# with open('1.jpg', 'wb') as f:
#     f.write(response.content)

