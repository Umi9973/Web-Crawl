

import requests						# 发起网络请求
from bs4 import BeautifulSoup		# 解析HTML文本
import pandas as pd					# 处理数据
import os
import time			# 处理时间戳
import json			# 用来解析json文本

'''
用于发起网络请求
url : Request Url
keyWord  : Keyword
page: Page number
'''
class F:
    # 请求头
    def fetchUrl(url, keyWord, page):
        headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",#可替换成本地的user agent
        }

        # 请求参数
        payloads = {
            "endTime": 0,
            "hasContent": True,
            "hasTitle": True,
            "isFuzzy": True,
            "key": keyWord,
            "limit": 10,
            "page": page,
            "sortType": 2,
            "startTime": 0,
            "type": 0,
        }

        # 发起 post 请求
        r = requests.post(url, headers=headers, data=json.dumps(payloads))
        return r.json()

    #解析数据
    def parseJson(jsonObj):
      records = jsonObj["data"]["records"];
      for item in records:
          # 这里示例解析了几条，其他数据项如末尾所示，有需要自行解析
          pid = item["id"]
          originalName = item["originalName"]
          belongsName = item["belongsName"]
          content = BeautifulSoup(item["content"], "html.parser").text
          displayTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["displayTime"]/1000))
          subtitle = item["subtitle"]
          title = BeautifulSoup(item["title"], "html.parser").text
          url = item["url"]

          yield [[pid, title, subtitle, displayTime, originalName, belongsName, content, url]]

      '''
      用于将数据保存成 csv 格式的文件（以追加的模式）
      path   : 保存的路径，若文件夹不存在，则自动创建
      filename: 保存的文件名
      data   : 保存的数据内容
      '''
      def saveFile(path, filename, data):
          # 如果路径不存在，就创建路径
          if not os.path.exists(path):
              os.makedirs(path)
          # 保存数据
          dataframe = pd.DataFrame(data)
          dataframe.to_csv(path + filename + ".csv", encoding='utf_8_sig', mode='a', index=False, sep=',', header=False )


    #主函数
    if __name__ == "__main__":
      # 起始页，终止页，关键词设置
        start = 1
        end = 3
      keyWord = "春节"

        # 保存表头行
        headline = [["文章id", "标题", "副标题", "发表时间", "来源", "版面", "摘要", "链接"]]
        saveFile("./data/", keyWord, headline)
        #爬取数据
        for page in range(start, end + 1):
            url = "http://people.cn/api-search/elasticSearch/search"
            html = fetchUrl(url, keyWord, page)
            for data in parseJson(html):
                saveFile("./data/", keyWord, data)
            print("第{}页爬取完成".format(page))

        # 爬虫完成提示信息
        print("爬虫执行完毕！数据已保存至以下路径中，请查看！")
        print(os.getcwd(), "\\data")

    # 这里是你文件的根目录
    path = "D:\\Newpaper\\2018"

    # 遍历path路径下的所有文件（包括子文件夹下的文件）
    def iterFilename(path):
        #将os.walk在元素中提取的值，分别放到root（根目录），dirs（目录名），files（文件名）中。
        for root, dirs, files in os.walk(path):
            for file in files:
                # 根目录与文件名组合，形成绝对路径。
                yield os.path.join(root,file)


'''
参考：1.https://blog.51cto.com/u_14137942/3241101
'''

