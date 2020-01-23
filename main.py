# -*- coding:utf-8 -*-
from QCC_crawler_final_version import QCC
import codecs
import json
import time
import random

spider = QCC("./config/not_crawled_company", "./config/proxies")
result_path = "./result/ret"
succ_crawled_comp_path = "./config/succ_crawled_comp"
companies = []

# 读取待爬取公司列表
with codecs.open("./config/companies", "r", "utf-8") as f:
    line = f.readline()
    while line:
        companies.append(line.strip())
        line = f.readline()


# 读取已爬取公司列表
succ_comps = []
with codecs.open("./config/succ_crawled_comp", "r", "utf-8") as f:
    line = f.readline()
    while line:
        succ_comps.append(line.strip())
        line = f.readline()



for comp in companies:
    if comp not in succ_comps:
        info = spider.run(comp)
        try:
            if len(info)>0:
                nameEqualFlag = 0
                companyName = info['companyName']
                if comp == companyName:
                    nameEqualFlag = 1

                with codecs.open(result_path, "a","utf-8") as f:
                    f.write(comp+'\t'+companyName+'\t'+str(nameEqualFlag)+'\t')
                    f.write(json.dumps(info))
                    f.write("\n")

                print("[%s_infomation has been successfully crawled.]"%comp)
                with codecs.open(succ_crawled_comp_path, "a", "utf-8") as f:
                    f.write(comp+'\n')

        except:
            continue
        time.sleep(random.uniform(2.5, 4.0))