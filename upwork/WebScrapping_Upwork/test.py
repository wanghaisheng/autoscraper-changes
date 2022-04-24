from proxy_request import ProxyRequest
import json

requests = ProxyRequest()
url = "https://www.upwork.com/ab/jobs/search/jobdetails/visitor/~016176b468b8f6e816/details"

headers = {
  'authority': 'www.upwork.com',
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
  'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
  "Connection": "close",
  'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
  'x-requested-with': 'XMLHttpRequest',
  'sec-fetch-site': 'none',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-user': '?1',
  'sec-fetch-dest': 'document',
  'referer': 'https://www.upwork.com/',
  'accept-language': 'en-US,en;q=0.9',
}


headers = {
  'authority': 'www.upwork.com',
  'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
  'x-odesk-user-agent': 'oDesk LM',
  'sec-ch-ua-mobile': '?0',
  'accept': 'application/json, text/plain, */*',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54',
  'x-requested-with': 'XMLHttpRequest',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.upwork.com/search/jobs/details/~01dd7a81e0da9c8dd8/',
  'accept-language': 'en-US,en;q=0.9',
  'Cookie': 'XSRF-TOKEN=d7345df3941e603625871e7acce7a45a; __cf_bm=50e2713bd1375ee21717c66e002ad6b6b247014f-1624343855-1800-AXlVRLuj9tQPya0ia4ARjO+HJv4lJhyLyAAKqYi4XYYv0gUAA7abaNy4xg85EXwlx/GJ46+Cul/t7NvWSwOuZj8=; channel=other; device_view=full; visitor_id=49.36.46.228.1624174453958000; _pxhd=SoBSa54OPBtwnuFTScCkjcImJTcJ2i30aAaCXHgrPajb70f1PntgbQXmM0zOIF31nJ95OfJ281TkZGwKGLd9Iw==:vAEbjMIo3tZ4jJusG6R3-cBJDy8kM2KkkveMuDVTTzaJ1dxQdm88EtAPJ0tK-M4MWM1/NZ6v5xtAxbJcLKC4ifx2LYGaUPhHyv5rqtCr/AA=; enabled_ff=CI11132Air2Dot75,CI9570Air2Dot5,!CI10270Air2Dot5QTAllocations,!CI10857Air3Dot0'
}

response = requests.get(url, headers=headers)
print(response.status_code)
# if response.status_code == 200:
#     with open('index.json','w') as f:
#         json.dump(response.json(),f)

