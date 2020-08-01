import requests
s = requests.session()
url = "https://api.bilibili.com/x/web-interface/newlist"
querystring = {"rid": 209, "type": "0", "pn": 1, "ps": "50", "jsonp": "jsonp"}
headers = {
        'referer': "http://www.bilibili.com/",
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
    }
uas = set()
with open("ip", 'r') as uaf:
    for ua in uaf.readlines():
        if ua:
            uas.add(ua.strip()[1:-1])
s.keep_alive = False
for ip in uas:
    s.proxies = {"https": "https://" + "47.74.232.57:26315"}
    s.params = querystring
    s.verify = False
    s.headers = headers
    r = s.get(url, allow_redirects=False)
    code = r.status_code
    print(ip+"---->"+str(code))
    if code == 200:
        with open("goodip.txt", 'a') as goodip:
            goodip.write(ip+"\n")
