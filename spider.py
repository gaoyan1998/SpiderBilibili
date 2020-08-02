import random
import time

import requests
import sys, getopt
# 导入CSV安装包
import csv
import json
from Logger import Logger
import socket
import multiprocessing
import redis
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class spiderInfo:
    rid = None
    page = 1
    outputfile = "defaultSpider.csv"
    ips = ""
    socket.setdefaulttimeout(10)
    dataLog = None

    # 加载User_Agent函数
    def LoadUserAgent(self, uafile):
        uas = []
        with open(uafile, 'r') as uaf:
            for ua in uaf.readlines():
                if ua:
                    uas.append(ua.strip()[1:-1])
        random.shuffle(uas)
        return uas

    # 加载ip函数
    def LoadIP(self):
        # uas = []
        # with open(ipfile, 'rb') as uaf:
        #     for ua in uaf.readlines():
        #         if ua:
        #             uas.append(ua.strip()[0:])
        # random.shuffle(uas)
        api = "http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=2a98d88af88a330c3547f2cc837d311e&orderNo=GL20200801233905Z1p6U3a2&count=1&isTxt=1&proxyType=1"
        response = requests.get(api)
        return response.text
        # return "121.205.219.62:18506"

    def getVideoInfo(self, url, params, uas):
        # 随机选择user_agent
        global ips, outputfile, rid, dataLog,page
        ua = random.choice(uas)

        # 蘑菇代理的隧道订单
        # appKey = "TndmVERKdldyQjRIcnhqaTpBN3BHS1VVNDBMT2FCbUYy"
        # 蘑菇隧道代理服务器地址
        # ip_port = 'secondtransfer.moguproxy.com:9001'
        # proxy = {"https": "https://" + "12.65.166.69:312"}
        # print(proxy)
        # sys.exit(2)

        # 加载headers
        headers = {
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
                proxy = {"http": "http://" + ips.strip()[0:], "https": "https://" + ips.strip()[0:]}
                dataLog.logger.info("开始请求" + proxy["https"] + str(params))
                response = requests.get(url, params=params, headers=headers, proxies=proxy, verify=False,
                                        allow_redirects=False, timeout=10)
                # response = requests.get(url, params=params, headers=headers, verify=False,
                #                         allow_redirects=False, timeout=10)
                dataLog.logger.info("请求结束")
                if response.status_code == 412:
                    dataLog.logger.info("封禁ip了")
                    time.sleep(100)
                    ips = self.LoadIP()
                    continue
                dataLog.logger.debug(response.text)
                dataLog.logger.info(params)
                jsdata = json.loads(response.text)
                data = jsdata['data']['archives']
                return data
            except Exception as e:
                time.sleep(5)
                ips = self.LoadIP()
                errStr = "出错url：" + url + str(params) + "\n"
                dataLog.logger.error(errStr)
                dataLog.logger.error(e)
                i += 1
        errStr = "已抛弃此条数据：" + url + str(params) + "\n"
        dataLog.logger.error(errStr)
        return None

    def parseData(self,data):
        global ips, outputfile, rid, dataLog,page
        # 1. 创建文件对象
        f = open(outputfile, 'a', encoding='utf-8')
        # 2. 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f, delimiter='|')
        # 3. 构建列表头
        # csv_writer.writerow(["aid", "attribute", "bvid", "cid", "ctime", "desc", "mid", "name", "pubdate", "pic"
        #                      , "coin", "danmaku", "favorite", "like", "reply", "share", "view", "title", "tname"])
        aid = data.get('aid', "None")
        attribute = data.get('attribute', "None")
        bvid = data.get('bvid', "None")
        cid = data.get('cid', "None")
        ctime = data.get('ctime', "None")
        desc = data.get('desc', "None")
        mid = data.get('owner', {}).get('mid', "None")
        name = data.get('owner', {}).get('name', "None")
        pubdate = data.get('pubdate', "None")
        pic = data.get('pic', "None")
        coin = data.get('stat', {}).get('coin', "None")
        danmaku = data.get('stat', {}).get('danmaku', "None")
        favorite = data.get('stat', {}).get('favorite', "None")
        like = data.get('stat', {}).get('like', "None")
        reply = data.get('stat', {}).get('reply', "None")
        share = data.get('stat', {}).get('share', "None")
        view = data.get('stat', {}).get('view', "None")
        title = data.get('title', "None")
        tname = data.get('tname', "None")
        # 4. 写入csv文件内容
        csv_writer.writerow([aid, attribute, bvid, cid, ctime, desc, mid, name, pubdate, pic
                                , coin, danmaku, favorite, like, reply, share, view, title, tname])
        # 5. 关闭文件
        f.close()

    def initConfig(self,argv):
        global rid, outputfile, page
        try:
            opts, args = getopt.getopt(argv, "i:p:o:", ["outputfile="])
        except getopt.GetoptError:
            print('spider.py -i <rid> -p <page> -o <outputfile>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('spider.py -i <rid> -p <page> -o <outputfile>')
                sys.exit()
            elif opt == "-i":
                rid = arg
            elif opt == "-p":
                page = int(arg)
            elif opt in ("-o", "--outputfile"):
                outputfile = arg
        if rid is None:
            print('-i rid is must!!')
            sys.exit(2)

    def start(self, id, pages, outputpath, logpath):
        global ips, outputfile, rid, dataLog,page
        dataLog = Logger(logpath)
        rid = id
        outputfile = outputpath
        page = pages
        # 加载user_agents.txt文件
        uas = self.LoadUserAgent("user_agent")
        ips = self.LoadIP()
        url = "https://api.bilibili.com/x/web-interface/newlist"
        while (True):
            querystring = {"rid": rid, "type": "0", "pn": page, "ps": "50", "jsonp": "jsonp"}
            data = self.getVideoInfo(url=url, params=querystring, uas=uas)
            dataLog.logger.info(data)
            if data is None:
                continue
            elif not data:
                break
            elif page > 10000:
                break
            for item in data:
                dataLog.logger.info("开始解析")
                dataLog.logger.info(item)
                self.parseData(item)
            page += 1
        progress = Logger("log/finished.log")
        progress.logger.info("处理完成" + str(rid))

poolLog = Logger("log/poolLog.log")

def run(id, page, outputpath, logpath):
    spider = spiderInfo()
    try:
        spider.start(id, page, outputpath, logpath)
    except:
        s = sys.exc_info()
        poolLog.logger.error("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        poolLog.logger.info(outputpath)

if __name__ == '__main__':

    # id = 29
    # outfile = "csv/" + str(id) + ".csv"
    # logfile = "log/" + str(id) + ".log"
    # run(29,1,outfile,logfile)
    # sys.exit(2)
    redis_conn = redis.Redis(host="airke.top", port=6379)
    queue = multiprocessing.Manager().Queue()
    result_queue = multiprocessing.Manager().Queue()
    pool = multiprocessing.Pool(5)
    queue_count = redis_conn.scard("rid")
    poolLog.logger.info("开始进程池---")
    for i in range(queue_count):
        '''
        For循环中执行步骤：
        （1）循环遍历，将1000个子进程添加到进程池（相对父进程会阻塞）
        （2）每次执行10个子进程，等一个子进程执行完后，立马启动新的子进程。（相对父进程不阻塞）
        apply_async为异步进程池写法。异步指的是启动子进程的过程，与父进程本身的执行（爬虫操作）是异步的，
        而For循环中往进程池添加子进程的过程，与父进程本身的执行却是同步的。
        '''
        id = redis_conn.spop("rid")
        if id is None:
            break
        id = int(id)
        outfile = "csv/" + str(id) + ".csv"
        logfile = "log/" + str(id) + ".log"
        poolLog.logger.info("添加进程----"+str(id))
        pool.apply_async(run, args=(id, 1, outfile, logfile))  # 维持执行的进程总数为10，当一个进程执行完后启动一个新进程.
    pool.close()
    pool.join()
    queue.join()  # 队列消费完 线程结束
