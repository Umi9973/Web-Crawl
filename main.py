import requests						# 发起网络请求
from bs4 import BeautifulSoup		# 解析HTML文本
import pandas as pd					# 处理数据
import os
import time			# 处理时间戳
import json			# 用来解析json文本
import re
import math


#selenium - 用于模拟点击等操作的包
#之后分离到单独的class里
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains



from Functions import Function as F


if __name__ == "__main__":
  keyWord = ['应急','城市安全','风险监测','城市体检','运管服','招标','项目','标准']
  #keyWord=['应急','证监会']
  
    #由关键词映射到相关文章的字典
  link_dict = dict()
  detailed_keyWord = dict() #二级目录，和关键词形成字典
  rating_dict = dict() #可能有用的字典，关键词的具体评分标准
  for item in keyWord:
    link_dict.update({str(item):[]})
    detailed_keyWord.update({str(item):[]})
    rating_dict.update({str(item):[]})
  
  def fastAdd(word,tempList,detailed_keyWord):
      for a in tempList:
        detailed_keyWord[word].append(a)
      
  fastAdd('应急',['风险评估','预警','安全评价','安全发展示范城市','指挥','通信'],detailed_keyWord)
  fastAdd('城市安全',['运行管理服务','运管服','韧性','预警','城市生命线','生产安全','公共安全','自然灾害'],detailed_keyWord)
  fastAdd('风险监测',['风险评估','动态监测','预警','处置','指挥','闭环'],detailed_keyWord)
  fastAdd('城市体检',['安全','韧性','评价'],detailed_keyWord)
  fastAdd('运管服',['标准','功能架构'],detailed_keyWord)
  fastAdd('招标',['风险监测','城市生命线','城市体检','应急指挥','自然灾害'],detailed_keyWord)
  fastAdd('项目',['风险监测','城市生命线','城市体检','应急指挥','自然灾害'],detailed_keyWord)
  fastAdd('标准',['隐患','风险','预警','设备分点','设备布设','分类分级'],detailed_keyWord)
  page = 1
  print(detailed_keyWord)
  website_stack = [#'https://www.investor.org.cn/information_release/news_release_from_authorities/zjhfb/index.shtml?page=1',
   'https://www.mem.gov.cn/xw/yjglbgzdt/'                ]
  
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

  # this function will use the requests lib and make the url assessable and readable for as
  def get_url(url):
    web = requests.get(url,timeout = 10)
    web.encoding = 'utf-8'
    if web.status_code == 200:
      return web.text
    else:
      return ''


  def flip(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 检查是否有分页按钮或链接
    pagination_links = soup.find_all('div', class_=['pagination-link', 'laypagecurr', 'wpagenavi', 'layerPage','gopage','btn next','page'], recursive=True)
    if not pagination_links:
        pagination_links = soup.find_all('a', class_=['pagination-link', 'laypagecurr', 'wpagenavi', 'layerPage','gopage','btn next'], recursive=True)
    pattern1 = re.compile(r'page=(\d+)')
    pattern2 = re.compile(r'p=(\d+)')
    # Find the page number part
    match1 = pattern1.search(url)
    match2 = pattern2.search(url)
    if match1 or match2 or pagination_links:
        print('flip')
        return True
    else: 
      print('no flip')
    # 检查是否有指示下一页的数据
    next_page_url = soup.find('a', rel='next')
    if next_page_url:
        return True
    return False


  # Use regular expression to find and replace the page number
  def generate_urls(base_url, start, end):
    url_list = []
    # Initialize WebDriver
    driver = webdriver.Chrome()

    # Open the website
    driver.get(base_url)

    # Function to check if the "Next" button is present and clickable
    def is_next_button_clickable():
      try:
          next_button = WebDriverWait(driver, 10).until(
              EC.element_to_be_clickable((By.XPATH, '//a[@class="laypage_next"]'))
          )
          return next_button
      except:
          print("no button")
          return None

    if re.findall('investor.org.cn',url):
      for i in range(2,15):
        next_button = is_next_button_clickable()
        if next_button:
            next_page= driver.find_element(By.CSS_SELECTOR, f'a.laypage_next[data-page="{i}"]')
            next_page.click()
            current_url = driver.current_url
            url_list.append(current_url)
            # Store the loaded page's HTML
            page_html = driver.page_source
            time.sleep(2)
    elif re.findall('mem.gov.cn',url):
        print('memgov')
        for i in range(2,15):
            current_url = f'https://www.mem.gov.cn/xw/yjglbgzdt/index_{i}.shtml'
            url_list.append(current_url)

    driver.quit() 
    print('temp url list:')
    print(url_list)
    return url_list
      

  #跳转到href指定文章后在文内通过算法判断匹配度
  #url - 文章链接
  #keyWord - 文章需要拥有的关键词
  #rating - 要求达到的匹配度
  def betterSearch(url,rating,level):
      def count_text(word, text):
        result = re.findall(word, text)
        return len(result)
    
      pattern = re.compile(u'[\u4e00-\u9fa5]')
      response = get_url(url)
      soup = BeautifulSoup(response, 'html.parser')
      text = soup.get_text()
      
      result_rating = 0
      
      # Count the occurrences of each keyword in the text
      keyword_count = {keyword: count_text(keyword,text) for keyword in level}
    
      #Calculate the number of unique keywords covered
      unique_keywords_covered = sum(1 for count in keyword_count.values() if count > 0)
    
      #Calculate the total occurrences of all keywords
      total_keyword_occurrences = sum(keyword_count.values())
    
      #Return a tuple with the unique keywords covered and total occurrences
      if total_keyword_occurrences == 0:
          return 0
      result_rating = (unique_keywords_covered*5+ total_keyword_occurrences)/len(level)
      return result_rating



  def extract_pdf(url):
    # in this for loop we will scrap all the pdf files from the url
    #需要pdf下载功能可以使用
    '''
    for pdf in pdfs:
        if ('.pdf' in pdf.get('href', [])):
                r = requests.get(pdf.get('href'))
                new_pdf = open(f'‘insert path to a pdf folder’\\{p}.pdf', 'wb')
                new_pdf.write(r.content)
                p += 1
                new_pdf.close()
        '''
    return 0 #for now

  #行已有url自行跳转到关联url
  def widerSearch(url):
      
    return 0 #test use




  def mainMethod(doc_html,main_url):
    # with bs we will grab the data in the url and scrap the tags that we want
    if doc_html:
      soup = BeautifulSoup(doc_html, 'html.parser')
      all_links = soup.find_all('a')
      for a in soup.find_all('a'):
          for b in keyWord:
            if re.search(str(b),str(a)):
              print('search!')
              if re.findall('investor.org.cn',main_url):
                  href = str(a['href']).split('.')[1]+'.shtml'
                  rating_url = f"https://www.investor.org.cn/information_release/news_release_from_authorities/zjhfb/{href}"
              elif re.findall('mem.gov.cn',main_url):
                  print('memgovvvvvvv')
                  href = str(a['href']).split('.')[1]+'.shtml'
                  rating_url = f'https://www.mem.gov.cn/xw/yjglbgzdt/{href}'
              
              print(rating_url)
              rating = betterSearch(url=rating_url,rating=0,level=detailed_keyWord.get(str(b)))#rating's logic need change 
              print(rating) 
              if len(link_dict[str(b)]) >= 20:
                  break
              if rating >= 0.2:
                categories.append(a.text)
                link_dict[str(b)].append(a)
              #print(str(link.attrs['title']) + '\n')
                
                
              break


  '''
  main starts here
  '''
  
  
  categories=[]

  while website_stack:
    url = website_stack.pop()
    if flip(url):
      print('flip2')
      temp_urls = generate_urls(url, start=0, end=0)
      # here we will chose the url that we want to scrap and put him in the 'get_url' function
      while temp_urls:
          url_to_scrape = temp_urls.pop()
          doc_html = get_url(url_to_scrape)
          mainMethod(doc_html,url)
         
    else:    
      print('no flip')
      # here we will chose the url that we want to scrap and put him in the 'get_url' function
      url_to_scrape = url
      doc_html = get_url(url_to_scrape)
      mainMethod(doc_html,url)

  
  print(link_dict)
  print(categories)

