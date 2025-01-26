import requests

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'app_version': '9.2.5',
    'appid': '30004',
    'appsiteid': '0',
    'authorization': 'Bearer eyJicyI6MCwiYWlkIjoxMDAwOSwicGlkIjoiMzAiLCJzaWQiOiJhM2JmYWE4MzFiOWUxYzc5MGJjYjBkYmNjMjM3YTFmMiIsImFsZyI6IkhTNTEyIn0.eyJzdWIiOiIxMzc5MzM1NzcyNDUxNDk1OTQxIiwiZXhwIjoxNzM3NDcyMjE1LCJqdGkiOiI4OWViMjEzOC1lYzQ2LTQ2YjctODIyYi1mZDg0ZmYxMjM4ZmMifQ.AMV6qqB0XI84xDc7VnG3ua27Q7o_nMrJbTsG4JrGWfa-yVi7-fxEwo_LA4d0RNueS355egXl33j--Q6_UUf74w',
    'channel': 'official',
    'device_brand': 'Linux_Chrome_131.0.0.0',
    'device_id': '6f76e02b64ba4a078a331eb5c323913b',
    'lang': 'ru-RU',
    'mainappid': '10009',
    'origin': 'https://bingx.paycat.com',
    'platformid': '30',
    'priority': 'u=1, i',
    'referer': 'https://bingx.paycat.com/',
    'reg_channel': 'official',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'sign': '633C6C2E893168F3840D61D1C0F0161E390F67FB34D3E121F12848A35805A8B1',
    'timestamp': '1737040244016',
    'timezone': '3',
    'traceid': 'e355ec5e01b34d94aabcffb45d13eff5',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

_response = requests.get('https://api-app.we-api.com/api/c2c/v1/user-pay-method/list', headers=headers)

print(_response.json()["data"]["payments"])