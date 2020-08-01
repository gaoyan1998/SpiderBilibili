# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 08:34:22 2019

@author: gwiely
"""

import requests
from lxml import etree
import time
import random

def get_ip_list(url):
    headers = {
      'User_agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
      'referer': 'http://www.66ip.cn/index.html',
      'Host': 'www.66ip.cn'
    }
    response = requests.get(url,headers=headers)
    page_html = response.text
    html = etree.HTML(page_html)
    content_lists = html.xpath('//div[@align="center"]/table/tr')[1:]
    for content_list in content_lists:
        ip = content_list.xpath('./td[1]/text()')[0]
        port = content_list.xpath('./td[2]/text()')[0]
        result = "http://"+ip+":"+port
        yield result


def check_ip(proxy_str):
    url = "http://www.baidu.com"
    proxy = {
            "http": proxy_str,
            "https": proxy_str
    }
    try:
        response = requests.get(url, timeout=5, proxies=proxy)
        print("可以使用的代理IP：{}".format(proxy_str))
        return True
    except:
        print("破烂IP，服务器辣鸡：{}".format(proxy_str))
        return False

def main():
    usable_ip_list = []
    fileWriter = open('UsabelIP.txt', 'a')
    for i in range(1, 100):
        url = "http://www.66ip.cn/{}.html".format(i)
        print("第{}页,url :  {}".format(i, url))
        proxy = get_ip_list(url)
        for proxy_str in proxy:
            if check_ip(proxy_str):
                usable_ip_list.append(proxy_str)
                fileWriter.write(proxy_str+"\n")
        time.sleep(random.randint(4,8))
    fileWriter.flush()
    fileWriter.close()

if __name__=='__main__':
    main()
