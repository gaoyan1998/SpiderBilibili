import requests
s = requests.session()
url ="https://www.bilibili.com/"
uas = set()
with open("ip", 'r') as uaf:
    for ua in uaf.readlines():
        if ua:
            uas.add(ua.strip()[1:-1])
s.keep_alive = False
for ip in uas:
    s.proxies= {"https:"+ip}
    r = s.get(url)
    code = r.status_code
    print(ip+"---->"+str(code))
    if code == 200:
        with open("goodip.txt1", 'a') as goodip:
            goodip.write(ip+"\n")
