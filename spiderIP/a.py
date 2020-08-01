#!D:/spider/src/ python
# -*- coding: utf-8 -*-
# @Time     : 20:49
# @Author   :lion
# @Site     :10kb
# File      :agency.py
# @Software :PyCharm
import csv
import threading
from queue import Queue
from threading import Thread

import requests
from lxml import etree

ip_text = "ip.txt"


class QuickAgency(Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.44",
        "Connection": "close"
    }

    def __init__(self, page_queue: Queue, joke_queue: Queue, *args, **kwargs):
        super(QuickAgency, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.joke_queue = joke_queue
        self.index = "https://www.kuaidaili.com"

    def run(self) -> None:
        while True:
            if self.page_queue.empty():
                break
            urls = self.page_queue.get()
            response = requests.request("GET", urls, headers=self.headers, timeout=3).content  # 快代理

            html = etree.HTML(response)
            ip = html.xpath("//*[@id='list']/table/tbody/tr/td[1]/text()")  # ip
            port = html.xpath("//*[@id='list']/table/tbody/tr/td[2]/text()")  # 端口
            print("第%s页爬取完毕，开始下一页..." % urls.split("/")[-1])


class Free89(Thread):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.44",
    }

    def __init__(self, page_queue: Queue, joke_queue: Queue, *args, **kwargs):
        super(Free89, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.joke_queue = joke_queue

    def run(self) -> None:
        while True:
            if self.page_queue.empty():
                break
            try:
                urls = self.page_queue.get()
                print(urls)
                response = requests.get(urls, headers=self.headers, timeout=3.0).content.decode()
                html = etree.HTML(response)
                ip = html.xpath("//*[@class='layui-table']/tbody/tr/td[1]/text()")
                port = html.xpath("//*[@class='layui-table']/tbody/tr/td[2]/text()")
                for i, p in zip(ip, port):
                    i, p = i.strip(), p.strip()

                    proxy = {"http": i + ":" + p}
                    r = requests.request("get", "http://httpbin.org/ip", proxies=proxy, timeout=3.0).content.decode()
                    if str(i) in r:
                        print("ip:%s可用" % proxy)
                        self.joke_queue.put((i, p))
                    else:
                        print("ip:%s不可用" % proxy)
            except Exception:
                pass


class Writer(Thread):

    def __init__(self, joke_queue: Queue, writer, glock: threading.Lock, *args, **kwargs):
        super(Writer, self).__init__(*args, **kwargs)
        self.joke_queue = joke_queue
        self.writer = writer
        self.lock = glock

    def run(self) -> None:
        while True:
            try:
                joke_info = self.joke_queue.get(timeout=40)
                self.lock.acquire()
                self.writer.writerow(joke_info)
                self.lock.release()
                print("存入一条有效地址...")
            except Exception as e:
                print(e)
                break


if __name__ == '__main__':
    page_queue = Queue(50)
    joke_queue = Queue(50)

    glock = threading.Lock()
    ip = open("ip.csv", "a", newline="", encoding="utf-8")
    writer = csv.writer(ip)
    writer.writerow(("ip", "port", "type"))

    for i in range(1, 41):
        # url = "https://www.kuaidaili.com/free/intr/%d" % i
        url = "http://www.89ip.cn/index_%d.html" % i
        page_queue.put(url)

    # 抓取数据
    for i in range(15):
        # t = QuickAgency(page_queue, jock_queue)
        t = Free89(page_queue, joke_queue)
        t.start()

    for w in range(15):
        t = Writer(joke_queue, writer, glock)
        t.start()
