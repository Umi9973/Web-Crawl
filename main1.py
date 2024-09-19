import requests						# 发起网络请求
from bs4 import BeautifulSoup		# 解析HTML文本
import pandas as pd					# 处理数据
import os
import time			# 处理时间戳
import json			# 用来解析json文本
from Functions import Function as F
'''
用于发起网络请求
url : Request Url
keyWord  : Keyword
page: Page number
'''

#主函数
if __name__ == "__main__":
  # 起始页，终止页，关键词设置
    start = 1
    end = 3
    keyWord = "春节"

    # 保存表头行
    headline = [["文章id", "标题", "副标题", "发表时间", "来源", "版面", "摘要", "链接"]]
    F.saveFile(keyWord, headline)
    #爬取数据
    for page in range(start, end + 1):
        url = "http://baidu.com"
        html = F.fetchUrl(url, keyWord, page)
        for data in F.parseJson(html):
            F.saveFile(keyWord, data)
        print("第{}页爬取完成".format(page))

    # 爬虫完成提示信息
    print("爬虫执行完毕！数据已保存至以下路径中，请查看！")



'''
参考：1.https://blog.51cto.com/u_14137942/3241101
'''