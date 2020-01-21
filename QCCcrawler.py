# -*- coding:utf-8 -*-

import requests
import re
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
from config.Headers import headers
import time
'''
pay attention:
    id: #
    class: .
    如果没有select出数据，1.会返回空列表 2.
'''


with open("./config/proxies", "r")  as f:
    proxies = json.loads(f.read())


def get_random_proxy(proxies):
    proxy = random.choice(proxies)
    return {proxy['scheme']: proxy['scheme']+'://'+proxy['ip']+':'+proxy['port']}


def get_web_text(url, headers, proxy, params=None):
    if params:
        response = requests.request("GET", url, headers=headers, params=params, proxies=proxy)
    else:
        response = requests.request("GET", url, headers=headers, proxies=proxy)
    response.encoding = 'utf-8'
    return response.text


def get_para(company, headers, proxy): # TODO 这里如果爬不到company code 该如何处理？
    url = "https://www.qichacha.com/search"
    querystring = {"key": company}
    response_text = get_web_text(url, headers, proxy, querystring)
    para = re.findall('href="/firm_(.*?).html" target="_blank" class="ma_h1">', response_text, re.S)
    if not para:
        return '', ''
    else:
        return para[0], proxy



def get_company_name(url, headers, proxy):
    response_text = get_web_text(url, headers, proxy)
    soup = BeautifulSoup(response_text, 'lxml')
    # 如果没有select出数据 会返回空列表
    companyName = soup.select("#company-top > div.row > div.content > div.row.title.jk-tip > h1")

    return companyName



def get_base(info, base_url, headers, proxy, company_code, companyName):
    base = {}
    response_text = get_web_text(base_url, headers, proxy)
    soup = BeautifulSoup(response_text, 'lxml')
    # print(response.text)
    name = soup.select('div.row div.col-sm-12 table.ntable div.bpen a.bname')
    registered_capital = soup.select("div.row div.col-sm-12 table.ntable tr")[0].select("td")[3].text
    actually_capital = soup.select("div.row div.col-sm-12 table.ntable tr")[1].select("td")[1].text
    management_forms = soup.select("div.row div.col-sm-12 table.ntable tr")[2].select("td")[1].text.strip()
    establishment_date = soup.select("div.row div.col-sm-12 table.ntable tr")[2].select("td")[3].text.strip()
    unified_social_credit_code = soup.select("div.row div.col-sm-12 table.ntable tr")[3].select("td")[1].text.strip()
    taxpayer_identification_number = soup.select("div.row div.col-sm-12 table.ntable tr")[3].select("td")[3].text.strip()
    print(unified_social_credit_code)
    print(taxpayer_identification_number)

    partnern = soup.select("div.row div.col-sm-12 div.data_div section#partnern")[0]
    numOfpartnern = partnern.select("div.tnavtab-content div.tcaption span.tbadge")[0].text
    try:
        numOfpartnern = int(numOfpartnern)
    except:
        numOfpartnern = 0

    shareholders = {}
    partnern_tr = partnern.select("div.tnavtab-content div.tnavtab-box table.ntable.ntable-odd.npth.nptd tr")
    for ind in range(1,numOfpartnern+1):
        tr = partnern_tr[ind]
        shareholders[ind] = {}
        holders_basic = tr.select("table.insert-table tr td")[1].text
        shareholders[ind]['股东及出资信息'] = holders_basic
        stake = tr.select("td.text-center")[0].text.strip()
        shareholders[ind]['持股比例'] = stake
        capital_contribution = tr.select("td.text-center")[1].text.strip()
        shareholders[ind]['认缴出资金额'] = capital_contribution
        capital_contribution_date = tr.select("td.text-center")[2].text.strip()
        shareholders[ind]['认缴出资日期'] = capital_contribution_date

    base['股东信息'] = shareholders
    info['base'] = base


def get_susong(info, susong_url, headers, proxy, company_code, companyName):
    susong = {}
    response_text = get_web_text(susong_url, headers, proxy)
    soup = BeautifulSoup(response_text, 'lxml')
    # tr = soup.select('table.ntable.ntable-odd tr')[1]
    # tr = tr.select('h3.seo.font-14')[0].text
    # print(tr)
    # print(response.text)

    # 通过对比 例如裁判文书391 ，与序号的大小来判断是否还需要继续翻页
    page=str(3)
    wenshu_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=susong&box=wenshu&casetype=&casereason='%(company_code, companyName,page)
    wenshu_ret = get_web_text(wenshu_url,headers,proxy)
    # print(wenshu_ret)

    info['susong'] = susong


def get_asset(info, asset_url, headers, proxy, company_code, companyName):
    asset = {}
    # # response_text = get_web_text(asset_url, headers, proxy)
    # # soup = BeautifulSoup(response_text, 'lxml')
    #
    # page_brand=1
    # trademarklist_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=shangbiao&sbappdateyear=&sbstatus=&sbflowno=&sbintcls='%(company_code, companyName,str(page_brand))
    # response_test = get_web_text(trademarklist_url, headers, proxy)
    # soup = BeautifulSoup(response_test, 'lxml')
    # numOftrademark = soup.select("span.tbadge")[0].text.strip()
    # numOftrademark = int(re.findall(r'\d+', numOftrademark)[0])
    #
    # trademarklist = {}
    # if numOftrademark > 0:
    #     numOfHasCrawledList = 0
    #     while numOfHasCrawledList < numOftrademark:
    #         trademarklist_tr = soup.select("table.ntable.ntable-odd tr")
    #         numOfCurrentList = len(trademarklist_tr) - 1
    #         numOfHasCrawledList += numOfCurrentList
    #         for ind in range(1, numOfCurrentList+1):
    #             tr = trademarklist_tr[ind]
    #             index = int(tr.select("td.tx")[0].text.strip())
    #             brand_img = tr.select("img")[0]['src']
    #             brand_name = tr.select("td.text-center")[1].text.strip()
    #             status = tr.select("td.text-center")[2].text.strip()
    #             apply_time = tr.select("td.text-center")[3].text.strip()
    #             registered_num = tr.select("td")[5].text.strip()
    #             international_classification = tr.select("td")[6].text.strip()
    #
    #             trademarklist[index] = {"商标": brand_img, "商标名": brand_name, "状态": status, "申请日期": apply_time, "注册号": registered_num, "国际分类": international_classification}
    #             print('[brand_page_%s has been crawled.]'%str(page_brand))
    #
    #
    #         if numOfHasCrawledList < numOftrademark:
    #             page_brand += 1
    #             trademarklist_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=shangbiao&sbappdateyear=&sbstatus=&sbflowno=&sbintcls=' % (company_code, companyName, str(page_brand))
    #             response_test = get_web_text(trademarklist_url, headers, proxy)
    #             soup = BeautifulSoup(response_test, 'lxml')
    #
    #
    #
    # asset['商标信息'] = trademarklist
    #
    #
    # info['asset'] = asset

    page_patent = 1
    patent_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=zhuanli&zlpublicationyear=&zlipclist=&zlkindcode=&zllegalstatus=' % (
    company_code, companyName, str(page_patent))
    try:
        response_test = get_web_text(patent_list_url, headers, proxy)
        soup = BeautifulSoup(response_test, 'lxml')
        numOfpatent = soup.select("span.tbadge")[0].text.strip()
        numOfpatent = int(re.findall(r'\d+', numOfpatent)[0])

    except:
        numOfpatent = 0

    patent_list = {}
    if numOfpatent > 0:
        numOfHasCrawledList = 0

        patent_list_tr = soup.select("table.ntable.ntable-odd tr")
        numOfCurrentList = len(patent_list_tr) - 1
        numOfHasCrawledList += numOfCurrentList
        for ind in range(1, numOfCurrentList + 1):
            tr = patent_list_tr[ind]
            index = tr.select("td.tx")[0].text.strip()
            patent_type = tr.select("td")[1].text.strip()
            public_num = tr.select("td")[2].text.strip()
            public_date = tr.select("td")[3].text.strip()
            patent_name = tr.select("td")[4].text.strip()
            patent_detail_url = tr.select("td")[4].select("a")[0]['href']
            patent_detail_url = 'https://www.qichacha.com' + patent_detail_url
            print(patent_detail_url)

            patent_list[index] = {"专利类型": patent_type, "公开（公告）号": public_num, "公开（公告）日期": public_date,
                                  "名称": patent_name}

        print('[patent_page_%s has been crawled.]' % str(page_patent))
        print('[patent_num_%s has been crawled.]' % str(numOfHasCrawledList))

    asset['专利信息'] = patent_list
    info['asset'] = asset


def get_run(info, run_url, headers, proxy, company_code, companyName):
    run = {}
    response_text = get_web_text(run_url, headers, proxy)
    soup = BeautifulSoup(response_text, 'lxml')
    # tr = soup.select('table.ntable.ntable-odd tr')[1]
    # tr = tr.select('h3.seo.font-14')[0].text
    # print(tr)
    # print(response.text)

    info['run'] = run


def get_detail(company_code, headers, proxy):
    info = {}
    url = 'https://www.qichacha.com/firm_%s.html' % company_code
    companyName = get_company_name(url, headers, proxy)
    while not companyName:
        companyName = get_company_name(url, headers, proxy)
    try:
        companyName = quote(companyName[0].text)
    except:
        raise Exception("[can't get companyName_quote]")

    base_url = 'https://www.qichacha.com/firm_%s.html#base'%company_code
    susong_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&tab=susong'%(company_code, companyName)
    asset_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&tab=asset'%(company_code, companyName)
    run_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&tab=run' % (company_code, companyName)


    # get_base(info, base_url, headers, proxy, company_code, companyName)
    # get_susong(info, susong_url, headers, proxy, company_code, companyName)
    get_asset(info, asset_url, headers, proxy, company_code, companyName)
    # get_run(info, run_url, headers, proxy, company_code, companyName)
    return info



def write_to_file(content, filepath):
    with open(filepath, "a") as f:
        f.write(content)
        f.write('\n')


# def main(company, filepath):
#     try:
#         ret, proxy = get_para(company, headers, get_random_proxy(proxies))
#     except:
#         write_to_file(company, filepath)
#         return
#     # 若最终结果只有一个空，说明没有爬到company_code
#     if ret:
#         try:
#             info = get_detail(ret, headers, proxy)
#             return info
#         except:
#             write_to_file(company, filepath)
#             return
#     else:
#         write_to_file(company, filepath)
#         return



def main(company, filepath):

    ret, proxy = get_para(company, headers, get_random_proxy(proxies))

    # 若最终结果只有一个空，说明没有爬到company_code
    if ret:
        info = get_detail(ret, headers, proxy)
        return info

    return ret


info = main("百度", "./config/not_crawled_company")
print(info)

