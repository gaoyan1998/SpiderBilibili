import random

import requests
import json
# 导入CSV安装包
import csv

from Logger import ErrorLog, DataLog, Logger

errLog = log = Logger('./log/error.log')
dataLog = log = Logger('./log/data.log')
progress = log = Logger('./log/progress.log')


# 加载User_Agent函数
def LoadUserAgent(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
    random.shuffle(uas)
    return uas


def getVideoInfo(url, params, uas):
    # 随机选择user_agent
    ua = random.choice(uas)

    # 蘑菇代理的隧道订单
    appKey = "TndmVERKdldyQjRIcnhqaTpBN3BHS1VVNDBMT2FCbUYy"
    # 蘑菇隧道代理服务器地址
    ip_port = 'secondtransfer.moguproxy.com:9001'
    proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}

    # 加载headers
    headers = {
        "Proxy-Authorization": 'Basic ' + appKey,
        'referer': "http://www.bilibili.com/",
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        'User-Agent': ua
    }
    # 通过requests.get来请求数据，再通过json()解析
    i = 0
    while i < 3:
        try:
            response = requests.get(url, params=params, headers=headers, proxies=proxy, verify=False,
                                    allow_redirects=False).json()
            dataLog.logger.info(response)
            data = response['data']['archives']
            return data
        except Exception as e:
            errStr = "出错url：" + url + str(params) +"\n"
            errLog.logger.error(errStr)
            errLog.logger.error(e)
            i += 1
    return None


def parseData(data):
    # 1. 创建文件对象
    f = open('kepu.csv', 'a', encoding='utf-8')
    # 2. 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 3. 构建列表头
    # csv_writer.writerow(["aid", "attribute", "bvid", "cid", "ctime", "desc", "mid", "name", "pubdate", "pic"
    #                      , "coin", "danmaku", "favorite", "like", "reply", "share", "view", "title", "tname"])
    aid = data['aid']
    attribute = data['attribute']
    bvid = data['bvid']
    cid = data['cid']
    ctime = data['ctime']
    desc = data['desc']
    mid = data['owner']['mid']
    name = data['owner']['name']
    pubdate = data['pubdate']
    pic = data['pic']
    coin = data['stat']['coin']
    danmaku = data['stat']['danmaku']
    favorite = data['stat']['favorite']
    like = data['stat']['like']
    reply = data['stat']['reply']
    share = data['stat']['share']
    view = data['stat']['view']
    title = data['title']
    tname = data['tname']
    # 4. 写入csv文件内容
    csv_writer.writerow([aid, attribute, bvid, cid, ctime, desc, mid, name, pubdate, pic
                            , coin, danmaku, favorite, like, reply, share, view, title, tname])
    # 5. 关闭文件
    f.close()


if __name__ == '__main__':
    # 加载user_agents.txt文件
    uas = LoadUserAgent("user_agent")
    url = "https://api.bilibili.com/x/web-interface/newlist"
    pn = 1
    while (True):
        querystring = {"rid": "201", "type": "0", "pn": pn, "ps": "50", "jsonp": "jsonp"}
        data = getVideoInfo(url=url, params=querystring, uas=uas)
        if data is None:
            continue
        elif data:
            break
        for item in data:
            parseData(item)
        pn += 1
    progress.logger.info("科普完成")
#
# headers = {
#     'referer': "http://www.bilibili.com/",
# }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
# json_obj = json.loads(response.text)
