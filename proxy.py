# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import http.client
import json
import codecs

def crawl_proxy(page):
    """
    获取代理列表
    :return: proies
    """
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    # url = 'http://www.xicidaili.com/'
    # 国内高代理
    url = 'http://www.xicidaili.com/nn/%s'%(str(page))
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html5lib')
    # table = soup.find('table', attrs={'id': 'ip_list'})

    # 提取ip
    proies = []
    for tr in soup.table.tbody.find_all_next('tr'):
        items = {}
        # 提取ip
        ip_pattern = "<td>(\d+.\d+.\d+.\d+)</td>"
        ip = re.findall(ip_pattern, str(tr))
        if len(ip) == 0:
            pass
        else:
            items['ip'] = ip[0]

            # 提取端口号
            port_pattern = "<td>(\d+)</td>"
            port = re.findall(port_pattern, str(tr))
            items['port'] = port[0]
            # print(port)

            # 提取速度
            speed = tr.select("div.bar")[0]['title'][:-1]
            if float(speed) > 4:
                continue
            # 提取协议
            scheme_pattern = "<td>(HTTPS?)</td>"
            scheme = re.findall(scheme_pattern, str(tr))
            items['scheme'] = str(scheme[0]).lower()
            # print(scheme)
            proies.append(items)
    return proies



def get_proxy(num):
    proies = []
    page = 0
    while len(proies) < num:
        page += 1
        eachProies = crawl_proxy(page)
        usefulProies = verifyproxy(eachProies)
        proies.extend(usefulProies)
    print("max_page=%d"%page)
    return proies


def verifyproxy(proxies):
    """
    验证代理的有效性
    :param proxies:
    :return:
    """
    url = "http://www.baidu.com"
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    usefulProxies = []
    for item in proxies:
        ip = item['ip']
        port = item['port']
        try:
            conn = http.client.HTTPConnection(ip, port, timeout=5)
            conn.request(method='GET', url=url, headers=headers)

            usefulProxies.append(item)

        # 请求出现异常
        except:
            print("代理不可用:{}:{}".format(ip, port))
    return usefulProxies

proxies = get_proxy(20)

with codecs.open("./config/proxies", "w", "utf-8") as f:
    f.write(json.dumps(proxies))
