1. 运行proxy.py文件，填写需要爬取的代理个数。
2. 手动注册登录企查查网站，拿到cookies并覆盖填入headers的cookies中
3. 运行main.py文件进行爬取
4. 需要爬取的公司写入config/companies文件中
5. 未成功爬取的公司会自动写入config/not_crawled_company文件中
6. 成功爬取的公司会自动写入config/succ_crawled_comp文件中
7. 若爬取中断，只需重新运行main.py文件。程序会自动从上次中断处开始爬取。
