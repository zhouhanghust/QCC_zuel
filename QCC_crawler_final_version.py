# -*- coding:utf-8 -*-

import requests
import re
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
from config.Headers import headers
import time
import random
import codecs


# TODO 有些公司对有的内容没有数据，而有的公司对这些内容有数据，有的甚至需要翻页，如果处理0，单页，翻页这三种情况;
# TODO 尝试从网页的最上方获取数据项的条数，大于10条的要翻页，等于0条的不用爬。
#
# TODO【最终解决方案】从firm url中爬取相应相的具体数目，再判断是否要爬，如果爬是否需要翻页; 不翻页的按照page=1来处理
# TODO check一下股东信息是不是都小于10个，如果有超过10个的拿出来看看，改变下爬取策略
# TODO check一下税务信用是不是都小于10个，如果有超过10个的拿出来看看，改变下爬取策略
# TODO 股东信息和税务信息即便是超过10个也不会翻页。因此不用改变爬取策略

class QCC():

    def __init__(self, notSuccPath, proxies_path):
        self.notSuccPath = notSuccPath
        self.proxies = self.get_proxies(proxies_path)


    def get_proxies(self, proxies_path):
        with codecs.open(proxies_path, "r", "utf-8") as f:
            proxies = json.loads(f.read())
        return proxies


    def get_random_proxy(self, proxies):
        proxy = random.choice(proxies)
        return {proxy['scheme']: proxy['scheme'] + '://' + proxy['ip'] + ':' + proxy['port']}


    def get_web_text(self, url, headers, proxy, params=None, post=False):
        if not post:
            if params:
                response = requests.request("GET", url, headers=headers, params=params, proxies=proxy)
            else:
                response = requests.request("GET", url, headers=headers, proxies=proxy)
        else:
            response = requests.request("POST", url, headers=headers, data=params, proxies=proxy)

        response.encoding = 'utf-8'
        return response.text

    def get_para(self, company, headers, proxy):
        url = "https://www.qichacha.com/search"
        querystring = {"key": company}
        response_text = self.get_web_text(url, headers, proxy, querystring)
        para = re.findall('href="/firm_(.*?).html" target="_blank" class="ma_h1">', response_text, re.S)
        if not para:
            return '', ''
        else:
            return para[0], proxy

    def get_company_name(self, url, headers, proxy):
        response_text = self.get_web_text(url, headers, proxy)
        soup = BeautifulSoup(response_text, 'lxml')
        # 如果没有select出数据 会返回空列表
        companyName = soup.select("#company-top > div.row > div.content > div.row.title.jk-tip > h1")

        return companyName

    def get_base(self, info, base_url, headers, proxy, company_code, companyName, numbers):
        base = {}
        response_text = self.get_web_text(base_url, headers, proxy)
        soup = BeautifulSoup(response_text, 'lxml')
        # print(response_text)
        legal_representative = soup.select("div.row div.col-sm-12 table.ntable div.bpen a.bname")[0].text
        base['法定代表人'] = legal_representative
        registered_capital = soup.select("div.row div.col-sm-12 table.ntable tr")[0].select("td")[3].text
        base['注册资本'] = registered_capital
        actually_capital = soup.select("div.row div.col-sm-12 table.ntable tr")[1].select("td")[1].text
        base['实缴资本'] = actually_capital
        management_forms = soup.select("div.row div.col-sm-12 table.ntable tr")[2].select("td")[1].text.strip()
        base['经营状态'] = management_forms
        establishment_date = soup.select("div.row div.col-sm-12 table.ntable tr")[2].select("td")[3].text.strip()
        base['成立日期'] = establishment_date
        unified_social_credit_code = soup.select("div.row div.col-sm-12 table.ntable tr")[3].select("td")[1].text.strip()
        base['统一社会信用代码'] = unified_social_credit_code
        taxpayer_identification_number = soup.select("div.row div.col-sm-12 table.ntable tr")[3].select("td")[3].text.strip()
        base['纳税人识别号'] = taxpayer_identification_number
        registered_number = soup.select("div.row div.col-sm-12 table.ntable tr")[4].select("td")[1].text.strip()
        base['注册号'] = registered_number
        organization_code = soup.select("div.row div.col-sm-12 table.ntable tr")[4].select("td")[3].text.strip()
        base['组织机构代码'] = organization_code
        company_type = soup.select("div.row div.col-sm-12 table.ntable tr")[5].select("td")[1].text.strip()
        base['企业类型'] = company_type
        subodinate_industry = soup.select("div.row div.col-sm-12 table.ntable tr")[5].select("td")[3].text.strip()
        base['所属行业'] = subodinate_industry
        approval_date = soup.select("div.row div.col-sm-12 table.ntable tr")[6].select("td")[1].text.strip()
        base['核准日期'] = approval_date
        registration_authority = soup.select("div.row div.col-sm-12 table.ntable tr")[6].select("td")[3].text.strip()
        base['登记机关'] = registration_authority
        area = soup.select("div.row div.col-sm-12 table.ntable tr")[7].select("td")[1].text.strip()
        base['所属地区'] = area
        english_name = soup.select("div.row div.col-sm-12 table.ntable tr")[7].select("td")[3].text.strip()
        base['英文名'] = english_name
        former_name = soup.select("div.row div.col-sm-12 table.ntable tr")[8].select("td")[1].text.strip()
        base['曾用名'] = former_name
        contributors = soup.select("div.row div.col-sm-12 table.ntable tr")[8].select("td")[3].text.strip()
        base['参保人数'] = contributors
        staff_size = soup.select("div.row div.col-sm-12 table.ntable tr")[9].select("td")[1].text.strip()
        base['人员规模'] = staff_size
        business_term = soup.select("div.row div.col-sm-12 table.ntable tr")[9].select("td")[3].text.strip()
        base['营业期限'] = business_term
        address = soup.select("div.row div.col-sm-12 table.ntable tr")[10].select("td")[1].text.strip().split('\n')[0]
        base['企业地址'] = address
        scope_of_business = soup.select("div.row div.col-sm-12 table.ntable tr")[11].select("td")[1].text.strip()
        base['经营范围'] = scope_of_business

        # partnern = soup.select("div.row div.col-sm-12 div.data_div section#partnern")[0]
        # try:
        #     numOfpartnern = partnern.select("div.tnavtab-content div.tcaption span.tbadge")[0].text
        #     numOfpartnern = int(numOfpartnern)
        # except:
        #     numOfpartnern = 0


        # # 股东信息不需要重新爬
        # page_partner = 1
        # partner_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=base&box=partners'%(company_code, companyName, str(page_partner))
        # response_text = self.get_web_text(partner_url,headers, proxy)
        # soup = BeautifulSoup(response_text, 'lxml')

        numOfpartnern = numbers['numOfshareHolders']
        numOfpartnern = int(re.findall(r'\d+', numOfpartnern)[0])
        shareholders = {}
        if numOfpartnern > 0:
            partnern = soup.select("div.row div.col-sm-12 div.data_div section#partnern")[0]
            partnern_tr = partnern.select("div.tnavtab-content div.tnavtab-box table.ntable.ntable-odd.npth.nptd tr")
            for ind in range(1, numOfpartnern + 1):
                tr = partnern_tr[ind]
                ind = str(ind)
                shareholders[ind] = {}
                holders_basic = tr.select("table.insert-table tr td")[1].text
                shareholders[ind]['股东及出资信息'] = holders_basic
                stake = tr.select("td.text-center")[0].text.strip()
                shareholders[ind]['持股比例'] = stake
                capital_contribution = tr.select("td.text-center")[1].text.strip()
                shareholders[ind]['认缴出资金额'] = capital_contribution
                capital_contribution_date = tr.select("td.text-center")[2].text.strip()
                shareholders[ind]['认缴出资日期'] = capital_contribution_date
                time.sleep(random.uniform(1.5, 3.5))
        base['股东信息'] = shareholders
        info['base'] = base

    # TODO CHECK yixia
    def get_susong(self, info, susong_url, headers, proxy, company_code, companyName, numbers):
        susong = {}
        # response_text = self.get_web_text(susong_url, headers, proxy)
        # soup = BeautifulSoup(response_text, 'lxml')

        numOfwenshu = numbers['numOfwenshu']
        numOfwenshu = int(re.findall(r'\d+', numOfwenshu)[0])
        # 通过对比 例如裁判文书391 ，与序号的大小来判断是否还需要继续翻页
        wenshulist = {}
        if numOfwenshu > 0:
            page_wenshu = 1
            wenshu_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=susong&box=wenshu&casetype=&casereason=' % (company_code, companyName, page_wenshu)
            wenshu_ret = self.get_web_text(wenshu_url, headers, proxy)
            soup = BeautifulSoup(wenshu_ret, 'lxml')
            numOfHasCrawledList = 0
            while numOfHasCrawledList < numOfwenshu:
                wenshulist_tr = soup.select("table.ntable.ntable-odd tr")
                numOfCurrentList = len(wenshulist_tr) - 1
                numOfHasCrawledList += numOfCurrentList
                for ind in range(1, numOfCurrentList+1):
                    tr = wenshulist_tr[ind]
                    index = int(tr.select("td.tx")[0].text.strip())
                    title = tr.select("a[target='_blank'] h3.seo.font-14")[0].text.strip()
                    anyou = tr.select("td[width='12%']")[0].text.strip()
                    fabudate = tr.select("td[width='103']")[0].text.strip()
                    annumber = tr.select("td[width='15%']")[0].text.strip()
                    anjianshenfen = tr.select("td[width='20%']")[0].text.strip()
                    zhixingfayuan = tr.select("td[width='13%']")[0].text.strip()
                    wenshulist[index] = {"裁判文书标题": title, "案由": anyou, "发布日期": fabudate, "案号": annumber, "案件身份": anjianshenfen, "执行法院": zhixingfayuan}
                    time.sleep(random.uniform(1.5, 3.5))
                print('[wenshu_page_%s has been crawled.]' % str(page_wenshu))
                print('[wenshu_num_%s has been crawled.]'%str(numOfHasCrawledList))

                if numOfHasCrawledList < numOfwenshu:
                    page_wenshu += 1
                    wenshu_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=susong&box=wenshu&casetype=&casereason=' % (company_code, companyName, page_wenshu)
                    wenshu_ret = self.get_web_text(wenshu_url, headers, proxy)
                    soup = BeautifulSoup(wenshu_ret, 'lxml')

        susong['裁判文书'] = wenshulist
        info['susong'] = susong

    def get_asset(self, info, asset_url, headers, proxy, company_code, companyName, numbers):
        asset = {}

        # response_text = self.get_web_text(asset_url, headers, proxy)
        # print(response_text)

        numOftrademark = numbers['numOfbrand']
        numOftrademark = int(re.findall(r'\d+', numOftrademark)[0])
        trademarklist = {}
        if numOftrademark > 0:
            page_brand = 1
            trademarklist_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=shangbiao&sbappdateyear=&sbstatus=&sbflowno=&sbintcls=' % (company_code, companyName, str(page_brand))
            response_test = self.get_web_text(trademarklist_url, headers, proxy)
            soup = BeautifulSoup(response_test, 'lxml')
            numOfHasCrawledList = 0
            while numOfHasCrawledList < numOftrademark:
                trademarklist_tr = soup.select("table.ntable.ntable-odd tr")
                numOfCurrentList = len(trademarklist_tr) - 1
                numOfHasCrawledList += numOfCurrentList
                for ind in range(1, numOfCurrentList + 1):
                    tr = trademarklist_tr[ind]
                    index = int(tr.select("td.tx")[0].text.strip())
                    brand_img = tr.select("img")[0]['src']
                    brand_name = tr.select("td.text-center")[1].text.strip()
                    status = tr.select("td.text-center")[2].text.strip()
                    apply_time = tr.select("td.text-center")[3].text.strip()
                    registered_num = tr.select("td")[5].text.strip()
                    international_classification = tr.select("td")[6].text.strip()

                    trademarklist[index] = {"商标": brand_img, "商标名": brand_name, "状态": status, "申请日期": apply_time,
                                            "注册号": registered_num, "国际分类": international_classification}
                    time.sleep(random.uniform(1.5, 3.5))
                print('[brand_page_%s has been crawled.]' % str(page_brand))
                print('[brand_num_%s has been crawled.]'%str(numOfHasCrawledList))

                if numOfHasCrawledList < numOftrademark:
                    page_brand += 1
                    trademarklist_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=shangbiao&sbappdateyear=&sbstatus=&sbflowno=&sbintcls=' % (
                    company_code, companyName, str(page_brand))
                    response_test = self.get_web_text(trademarklist_url, headers, proxy)
                    soup = BeautifulSoup(response_test, 'lxml')

        asset['商标信息'] = trademarklist




        numOfpatent = numbers['numOfpatent']
        numOfpatent = int(re.findall(r'\d+', numOfpatent)[0])
        patent_list = {}
        if numOfpatent > 0:
            page_patent = 1
            patent_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=zhuanli&zlpublicationyear=&zlipclist=&zlkindcode=&zllegalstatus=' % (company_code, companyName, str(page_patent))
            response_test = self.get_web_text(patent_list_url, headers, proxy)
            soup = BeautifulSoup(response_test, 'lxml')
            numOfHasCrawledList = 0
            while numOfHasCrawledList < numOfpatent:
                patent_list_tr = soup.select("table.ntable.ntable-odd tr")
                numOfCurrentList = len(patent_list_tr) - 1
                numOfHasCrawledList += numOfCurrentList
                for ind in range(1, numOfCurrentList+1):
                    tr = patent_list_tr[ind]
                    index = tr.select("td.tx")[0].text.strip()
                    patent_type = tr.select("td")[1].text.strip()
                    public_num = tr.select("td")[2].text.strip()
                    public_date = tr.select("td")[3].text.strip()
                    patent_name = tr.select("td")[4].text.strip()
                    patent_detail_url = tr.select("td")[4].select("a")[0]['href']

                    detail = {}
                    patent_detail_url = 'https://www.qichacha.com' + patent_detail_url
                    response_text_detail = None
                    trial_times_detail = 0
                    while not response_text_detail:
                        try:
                            response_text_detail = self.get_web_text(patent_detail_url, headers, proxy)
                        except:
                            response_text_detail = None
                            if trial_times_detail > 10:
                                break
                            trial_times_detail += 1
                            time.sleep(random.uniform(1.5, 3.5))
                    if response_text_detail:
                        soup_detail = BeautifulSoup(response_text_detail, 'lxml')
                        patent_detail = soup_detail.select("div.row div.col-md-9 table.ntable tr")

                        detail_name = patent_detail[0].select("td")[1].text.strip()
                        detail_apply_num = patent_detail[1].select("td")[1].text.strip()
                        detail_apply_date = patent_detail[1].select("td")[3].text.strip()
                        detail_public_num = patent_detail[2].select("td")[1].text.strip()
                        detail_public_date = patent_detail[2].select("td")[3].text.strip()
                        detail_priority_date = patent_detail[3].select("td")[1].text.strip()
                        detail_priority_num = patent_detail[3].select("td")[3].text.strip()
                        detail_inventors = patent_detail[4].select("td")[1].text.strip()
                        detail_apply_patent_person = patent_detail[4].select("td")[3].text.strip()
                        detail_agent = patent_detail[5].select("td")[1].text.strip()
                        detail_agent_person = patent_detail[5].select("td")[3].text.strip()
                        detail_IPC = patent_detail[6].select("td")[1].text.strip()
                        detail_CPC = patent_detail[6].select("td")[3].text.strip()
                        detail_address = patent_detail[7].select("td")[1].text.strip()
                        detail_mailcode = patent_detail[7].select("td")[3].text.strip()
                        detail_abstract = patent_detail[8].select("td")[1].text.strip()

                        detail['发明名称'] = detail_name
                        detail['申请号'] = detail_apply_num
                        detail['申请日'] = detail_apply_date
                        detail['公开（公告）号'] = detail_public_date
                        detail['公开（公告）日'] = detail_public_num
                        detail['优先权日'] = detail_priority_date
                        detail['优先权号'] = detail_priority_num
                        detail['发明人'] = detail_inventors
                        detail['申请（专利权）人'] = detail_apply_patent_person
                        detail['代理机构'] = detail_agent
                        detail['代理人'] = detail_agent_person
                        detail['IPC分类号'] = detail_IPC
                        detail['CPC分类号'] = detail_CPC
                        detail['申请人地址'] = detail_address
                        detail['申请人邮编'] = detail_mailcode
                        detail['摘要'] = detail_abstract

                    patent_list[index] = {"专利类型": patent_type, "公开（公告）号": public_num, "公开（公告）日期": public_date, "名称": patent_name, "详情": detail}
                    time.sleep(random.uniform(1.5, 3.0))

                print('[patent_page_%s has been crawled.]' % str(page_patent))
                print('[patent_num_%s has been crawled.]'%str(numOfHasCrawledList))

                if numOfHasCrawledList < numOfpatent:
                    page_patent += 1
                    patent_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=zhuanli&zlpublicationyear=&zlipclist=&zlkindcode=&zllegalstatus=' % (company_code, companyName, str(page_patent))
                    response_test = self.get_web_text(patent_list_url, headers, proxy)
                    soup = BeautifulSoup(response_test, 'lxml')

        asset['专利信息'] = patent_list



        numOfcertificate = numbers['numOfcertificate']
        numOfcertificate = int(re.findall(r'\d+', numOfcertificate)[0])
        certificatelist = {}

        if numOfcertificate > 0:
            page_certificate = 1
            certificate_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=zhengshu&zscertCategory='%(company_code, companyName, str(page_certificate))
            response_text = self.get_web_text(certificate_list_url, headers, proxy)
            soup = BeautifulSoup(response_text, 'lxml')
            numOfHasCrawledList = 0
            while numOfHasCrawledList < numOfcertificate:
                certificatelist_tr = soup.select("table.ntable.ntable-odd tr")
                numOfCurrentList = len(certificatelist_tr) - 1
                numOfHasCrawledList += numOfCurrentList
                for ind in range(1, numOfCurrentList + 1):
                    tr = certificatelist_tr[ind]
                    index = tr.select("td.tx")[0].text.strip()
                    certificatetype = tr.select("td[width='26%']")[0].text.strip()
                    certificatename = tr.select("td a.text-primary")[0].text.strip()
                    certificatenum = tr.select("td[width='18%']")[0].text.strip()
                    certificate_public_date = tr.select("td[width='104']")[0].text.strip()
                    certificate_due_date = tr.select("td[width='104']")[1].text.strip()


                    certificate_detail_dct = {}
                    certificate_detail_id = tr.select("td")[2].select("a")[0]['onclick'][8:-2]
                    print(certificate_detail_id)
                    querystring = {"id": certificate_detail_id}
                    trial_times = 0
                    response_text_detail = None
                    while not response_text_detail:
                        try:
                            response_text_detail = self.get_web_text('https://www.qichacha.com/company_zhengshuView', headers, proxy, querystring, post=True)
                        except:
                            response_text_detail = None
                            if trial_times > 10:
                                break
                            trial_times += 1
                            time.sleep(random.uniform(1.5, 3.5))
                    if response_text_detail:
                        certificate_detail_dct = json.loads(response_text_detail)

                    certificatelist[index] = {"证书类型": certificatetype, "证书名称":certificatename, "证书编号":certificatenum,"发证日期":certificate_public_date, "截止日期": certificate_due_date, "证书详情": certificate_detail_dct}
                    time.sleep(random.uniform(0.5, 1.5))

                print('[certificate_page_%s has been crawled.]' % str(page_certificate))
                print('[certificate_num_%s has been crawled.]' % str(numOfHasCrawledList))

                if numOfHasCrawledList < numOfcertificate:
                    page_certificate += 1
                    certificate_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=zhengshu&zscertCategory=' % (company_code, companyName, str(page_certificate))
                    response_text = self.get_web_text(certificate_list_url, headers, proxy)
                    soup = BeautifulSoup(response_text, 'lxml')

        asset['资质证书'] = certificatelist


        numOfcopyright = numbers['numOfcopyright']
        numOfcopyright = int(re.findall(r'\d+', numOfcopyright)[0])
        copyrightlist = {}
        if numOfcopyright > 0:
            page_copyright = 1
            copyright_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=zzq'%(company_code, companyName, str(page_copyright))
            response_text = self.get_web_text(copyright_list_url, headers, proxy)
            soup = BeautifulSoup(response_text, 'lxml')
            numOfHasCrawledList = 0
            while numOfHasCrawledList < numOfcopyright:
                copyrightlist_tr = soup.select("table.ntable.ntable-odd tr")
                numOfCurrentList = len(copyrightlist_tr) - 1
                numOfHasCrawledList += numOfCurrentList
                for ind in range(1, numOfCurrentList+1):
                    tr = copyrightlist_tr[ind]
                    index = tr.select("td.tx")[0].text.strip()
                    titleOfworks = tr.select("td[width='182']")[0].text.strip()
                    initdate = tr.select("td[width='112']")[0].text.strip()
                    enddate = tr.select("td[width='112']")[1].text.strip()
                    registrationNo = tr.select("td.text-center")[2].text.strip()
                    registrationdate = tr.select("td.text-center")[3].text.strip()
                    registrationType = tr.select("td.text-center")[4].text.strip()

                    copyrightlist[index] = {"作品名称": titleOfworks, "首次发表日期": initdate, "创作完成日期": enddate,"登记号":registrationNo, "登记日期":registrationdate,"登记类别":registrationType}
                    time.sleep(random.uniform(1.5, 2.5))
                print('[copyright_page_%s has been crawled.]' % str(page_copyright))
                print('[copyright_num_%s has been crawled.]' % str(numOfHasCrawledList))

                if numOfHasCrawledList < numOfcopyright:
                    page_copyright += 1
                    copyright_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=zzq' % (company_code, companyName, str(page_copyright))
                    response_text = self.get_web_text(copyright_list_url, headers, proxy)
                    soup = BeautifulSoup(response_text, 'lxml')

        asset['作品著作权'] = copyrightlist



        numOfrjzzq = numbers['numOfrjzzq']
        numOfrjzzq = int(re.findall(r'\d+', numOfrjzzq)[0])
        rjzzqlist = {}
        if numOfrjzzq > 0:
            page_software_copyright = 1
            softwareCopyright_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=rjzzq'%(company_code, companyName, str(page_software_copyright))
            response_text = self.get_web_text(softwareCopyright_list_url, headers, proxy)
            soup = BeautifulSoup(response_text, 'lxml')
            numOfHasCrawledList = 0
            while numOfHasCrawledList < numOfrjzzq:
                rjzzq_tr = soup.select("table.ntable.ntable-odd tr")
                numOfCurrentList = len(rjzzq_tr) - 1
                numOfHasCrawledList += numOfCurrentList
                for ind in range(1, numOfCurrentList+1):
                    tr = rjzzq_tr[ind]
                    index = tr.select("td.tx")[0].text.strip()
                    softname = tr.select("td")[1].text.strip()
                    softversion = tr.select("td.text-center")[0].text.strip()
                    softpublicdate = tr.select("td.text-center")[1].text.strip()
                    softsimplename = tr.select("td.text-center")[2].text.strip()
                    softregistnum = tr.select("td.text-center")[3].text.strip()
                    softapprovedate = tr.select("td.text-center")[4].text.strip()

                    rjzzqlist[index] = {"软件名称":softname, "版本号":softversion, "发布日期":softpublicdate, "软件简称":softsimplename, "登记号":softregistnum, "登记批准日期":softapprovedate}
                    time.sleep(random.uniform(1.5, 2.5))
                print('[rjzzq_page_%s has been crawled.]' % str(page_software_copyright))
                print('[rjzzq_num_%s has been crawled.]' % str(numOfHasCrawledList))

                if numOfHasCrawledList < numOfrjzzq:
                    page_software_copyright += 1
                    softwareCopyright_list_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&p=%s&tab=assets&box=rjzzq' % (company_code, companyName, str(page_software_copyright))
                    response_text = self.get_web_text(softwareCopyright_list_url, headers, proxy)
                    soup = BeautifulSoup(response_text, 'lxml')

        asset['软件著作权'] = rjzzqlist
        info['asset'] = asset


    def get_run(self, info, run_url, headers, proxy, company_code, companyName, numbers):
        run = {}
        # 税务信用直接在run_url中抓取，即便超过10个也会在首页显示的
        response_text = self.get_web_text(run_url, headers, proxy)
        soup = BeautifulSoup(response_text, 'lxml')

        numOftaxCredit = numbers['numOftaxCredit']
        numOftaxCredit = int(re.findall(r'\d+', numOftaxCredit)[0])
        taxcreditlist = {}
        if numOftaxCredit > 0:
            taxcredit = soup.select("section#taxCreditList table.ntable.ntable-odd")[0]
            taxcredit_tr = taxcredit.select("tr")
            for ind in range(1, numOftaxCredit+1):
                index = taxcredit_tr[2*ind].select("td.tx")[0].text.strip()
                pingjiayear = taxcredit_tr[2*ind].select("td.text-center")[0].text.strip()
                nashuirenid = taxcredit_tr[2*ind].select("td.text-center")[1].text.strip()
                level = taxcredit_tr[2*ind].select("td.text-center")[2].text.strip()
                pingjiadanwei = taxcredit_tr[2*ind].select("td.text-center")[3].text.strip()
                taxcreditlist[index] = {"评价年度": pingjiayear, "纳税人识别号": nashuirenid, "纳税信用等级": level, "评价单位": pingjiadanwei}
                time.sleep(random.uniform(0.5, 1.5))

        run['税务信用'] = taxcreditlist
        info['run'] = run



    def get_item_nums(self, firm_url, headers, proxy):
        response_text = self.get_web_text(firm_url, headers, proxy)
        soup = BeautifulSoup(response_text, 'lxml')
        numbers = {}
        divlist = soup.select("div.row div.col-sm-12 div.company-nav div.company-nav-contain div[class^='company-nav-tab']")
        if divlist:
            try:
                numOfshareHolders = divlist[0].select("div.company-nav-items a[data-pos='partnern']")[0].select("span.text-primary")[0].text.strip()
            except:
                numOfshareHolders = '0'
            try:
                numOfbrand = divlist[5].select("div.company-nav-items a[data-pos='shangbiaolist']")[0].select("span.text-primary")[0].text.strip()
            except:
                numOfbrand = '0'
            try:
                numOfpatent = divlist[5].select("div.company-nav-items a[data-pos='zhuanlilist']")[0].select("span.text-primary")[0].text.strip()
            except:
                numOfpatent = '0'
            try:
                numOfcertificate = divlist[5].select("div.company-nav-items a[data-pos='zhengshulist']")[0].select("span.text-primary")[0].text.strip()
            except:
                numOfcertificate = '0'
            try:
                numOfcopyright = divlist[5].select("div.company-nav-items a[data-pos='zzqlist']")[0].select("span.text-primary")[0].text.strip()
            except:
                numOfcopyright = '0'
            try:
                numOfrjzzq = divlist[5].select("div.company-nav-items a[data-pos='rjzzqlist']")[0].select("span.text-primary")[0].text.strip()
            except:
                numOfrjzzq = '0'
            try:
                numOfwenshu = divlist[1].select("div.company-nav-items a[data-pos='wenshulist']")[0].select("span.text-danger")[0].text.strip()
            except:
                numOfwenshu = '0'
            try:
                numOftaxCredit = divlist[2].select("div.company-nav-items a[data-pos='taxCreditList']")[0].select("span.text-primary")[0].text.strip()
            except:
                numOftaxCredit = '0'

            numbers['numOfshareHolders'] = numOfshareHolders
            numbers['numOfbrand'] = numOfbrand
            numbers['numOfpatent'] = numOfpatent
            numbers['numOfcertificate'] = numOfcertificate
            numbers['numOfcopyright'] = numOfcopyright
            numbers['numOfrjzzq'] = numOfrjzzq
            numbers['numOfwenshu'] = numOfwenshu
            numbers['numOftaxCredit'] = numOftaxCredit

        return numbers



    def get_detail(self, company_code, headers, proxy):
        info = {}
        url = 'https://www.qichacha.com/firm_%s.html' % company_code
        companyName = self.get_company_name(url, headers, proxy)
        try_times = 0
        while not companyName:
            if try_times > 5:
                break
            companyName = self.get_company_name(url, headers, proxy)
            try_times += 1
        try:
            companyName = quote(companyName[0].text)
        except Exception as e:
            print(e)
            raise Exception("[can't get companyName_quote]")


        # base_url = 'https://www.qichacha.com/firm_%s.html#base'%company_code
        # susong_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&tab=susong'%(company_code, companyName)
        # asset_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&tab=asset'%(company_code, companyName)
        # 上面三个url用不到了

        firm_url = 'https://www.qichacha.com/firm_%s.html' % (company_code)
        run_url = 'https://www.qichacha.com/company_getinfos?unique=%s&companyname=%s&tab=run' % (company_code, companyName)


        numbers = self.get_item_nums(firm_url, headers, proxy)
        if numbers:
            pass
        else:
            raise Exception("[can't get numbers]")

        self.get_base(info, firm_url, headers, proxy, company_code, companyName, numbers)
        time.sleep(random.uniform(1.0,2.5))
        self.get_susong(info, firm_url, headers, proxy, company_code, companyName, numbers)
        time.sleep(random.uniform(1.0, 2.5))
        self.get_asset(info, firm_url, headers, proxy, company_code, companyName, numbers)
        time.sleep(random.uniform(1.0, 2.5))
        self.get_run(info, run_url, headers, proxy, company_code, companyName, numbers)

        return info


    def write_to_file(self, content, filepath):
        with codecs.open(filepath, "a", "utf-8") as f:
            f.write(content)
            f.write('\n')



    def run(self, company):
        try:
            ret, proxy = self.get_para(company, headers, self.get_random_proxy(self.proxies))
        except Exception as e:
            print("[can't get company_code]:", e)
            self.write_to_file(company, self.notSuccPath)
            return

        info = self.get_detail(ret, headers, proxy)
        return info

        # # 若最终结果为空，说明没有爬到company_code
        # if ret:
        #     print('[company_code: %s]'%str(ret))
        #     try:
        #         info = self.get_detail(ret, headers, proxy)
        #         return info
        #     except Exception as e:
        #         print("[can't get_detail]", e)
        #         self.write_to_file(company, self.notSuccPath)
        #         return
        # else:
        #     print("[get None company_code]")
        #     self.write_to_file(company, self.notSuccPath)
        #     return



if __name__ == "__main__":
    spider = QCC("./config/not_crawled_company", "./config/proxies")
    info = spider.run("北京视讯电子技术有限责任公司")
    print(info)

    # result_path = "./config/ret"
    # companies = []
    # with codecs.open("./config/companies", "r", "utf-8") as f:
    #     line = f.readline()
    #     while line:
    #         companies.append(line.strip())
    #         line = f.readline()
    #
    # for comp in companies:
    #     info = spider.run(comp)
    #     try:
    #         if len(info)>0:
    #             with codecs.open(result_path, "a","utf-8") as f:
    #                 f.write(comp)
    #                 f.write('\t')
    #                 f.write(json.dumps(info))
    #                 f.write("\n")
    #     except:
    #         continue
    #     time.sleep(random.uniform(0.5,1.0))

