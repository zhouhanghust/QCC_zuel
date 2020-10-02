# -*- coding:utf-8 -*-
from QCC_crawler_final_version import QCC
import codecs
import json
import time
import random
import logging

# 设置日志
logger = logging.getLogger('logger')
f_handler = logging.FileHandler(filename="./log.log",encoding='utf-8',mode='a') # 日志存在QCC同级目录下
s_handler = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
f_handler.setLevel(logging.INFO)
s_handler.setLevel(logging.CRITICAL)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(funcName)s: %(message)s")
f_handler.setFormatter(formatter)
s_handler.setFormatter(formatter)
logger.addHandler(f_handler)
logger.addHandler(s_handler)


spider = QCC("./config/not_crawled_company", "./config/proxies",logger)
result_path = "./result/ret"
succ_crawled_comp_path = "./config/succ_crawled_comp"
companies = []

# 读取待爬取公司列表
with codecs.open("./config/companies5", "r", "utf-8") as f:
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


# 读取抓取失败的公司列表
not_suc = []
with codecs.open("./config/not_crawled_company","r","utf-8") as f:
    line = f.readline()
    while line:
        not_suc.append(line.strip())
        line = f.readline()

companies = list(set(companies)-set(succ_comps)-set(not_suc))
print(len(companies))
for comp in companies:
    # if comp not in succ_comps+not_suc:
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
                logger.info("[%s_infomation has been successfully crawled.]"%comp)
                logger.info("-----------------------------------------------------------------------")
                print("[%s_infomation has been successfully crawled.]"%comp)
                with codecs.open(succ_crawled_comp_path, "a", "utf-8") as f:
                    f.write(comp+'\n')

        except:
            logger.info("[Sorry, %s_infomation has not been crawled.]"%comp)
            logger.info("-----------------------------------------------------------------------")
            continue 
        finally:
            time.sleep(random.uniform(10.0, 15.0))
