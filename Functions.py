import requests						# 发起网络请求
from bs4 import BeautifulSoup		# 解析HTML文本
import pandas as pd					# 处理数据
import os
import time			# 处理时间戳
import json			# 用来解析json文本

class Function:
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
  def saveFile(filename, data):
      # 保存数据
      dataframe = pd.DataFrame(data)
      #dataframe.to_csv(path + filename + ".csv", encoding='utf_8_sig', mode='a', index=False, sep=',', header=False )
      return dataframe