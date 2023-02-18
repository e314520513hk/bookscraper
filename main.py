from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import os
import sys
import traceback
import configparser
import json
import time,datetime
from website import jd,opac
from logmanager import log
from dataset import sugarhost
from selenium.webdriver.common.keys import Keys
def searchTaiwanItemNo(china_item_no):
    
    if len(china_item_no) <=0:
        return False
    
    res = sugarhost.query(f"select distinct * from china_book where china_item='{china_item_no}'")
    
    if len(res) > 0:
        return res[0]['item']
    
    return searchTaiwanItemNo(china_item_no[0:-1])



# log.err_log("program is starting")
# q = sugarhost.query('SELECT * FROM `china_book` WHERE `ISBN` LIKE "9787302590354"')
# log.err_log(q)
# print(q)

# for row in q:
#     print(row["book_name"])
#     log.err_log(row["book_name"])



# def alert_is_present(driver):
#     try:
#         alert = driver.switch_to.alert
#         alert.text
#         return alert
#     except:
#         return False
try:
    baseUrl = 'https://tw.jd.com/'


    with open('isbnlist.txt','r') as isbnlist:
        isbnlist = isbnlist.read().splitlines()

    if len(isbnlist)<=0:
        log.err_log("isbnlist.txt is empty.")
        sys.exit()

    s = Service(r"./chromedriver")
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.page_load_strategy = 'eager'
    # options.add_argument('--headless')  # 啟動Headless 無頭
    # options.add_argument('--disable-gpu') #關閉GPU 避免某些系統或是網頁出錯

    # driver.set_window_size(1080, 768)
    # driver.implicitly_wait(100)


    driver = webdriver.Chrome(options=options, service=s)
    driver.get(baseUrl)
    
    print("請先登入(10分鐘內)")
    # WebDriverWait(driver, 600, 0.1).until(
    #                         EC.presence_of_element_located((By.CSS_SELECTOR, '.icon-plus-nickname')))   

    for isbn in isbnlist:

        isbn = isbn.strip()
        if not isbn.isnumeric():
            continue
        jd_bookinfo = jd.scrape(driver,isbn)
        # opac_bookinfo = opac.scrape(driver,isbn)
        
        log.test_log(f"jd info: {jd_bookinfo}\n")
        sys.exit()
        sleep(2)
    sys.exit("scrapping is done.")    
except Exception as ex:
    if  type(ex).__name__ == 'NoSuchWindowException':
        sys.exit("window already closed")
    log.err_log(ex)




# locator3 = (By.XPATH, '//*[@id="gameList"]/table/tbody/tr/td[4]/input')

# while True:
    
#     print("circle looping.....")
#     if redirectFlag and (driver.title == 'tixCraft拓元售票系統' or '節目資訊' in driver.title) or not redirectFlag:
#         redirectFlag = False
#         currentPageTitle = driver.title
      
#         if("activity/detail" in driver.current_url):
#             driver.get(driver.current_url.replace("activity/detail","activity/game"))
#             redirectFlag = True
#         elif not driver.title == currentPageTitle:
                       
#             redirectFlag = True
#         continue
        
#     if redirectFlag and "activity/game" in driver.current_url:
#         startTime = time.time()   
#         response = requests.get(driver.current_url)
#         soup = BeautifulSoup(response.text,'html.parser')
#         start_ordering = soup.select('#gameList > table > tbody > tr:nth-child(1) > td.gridc > input')
#         for btn in start_ordering:
#             start_order_href = btn.get('data-href')    
#         response = requests.get(baseUrl+start_order_href)    
#         soup = BeautifulSoup(response.text,'html.parser')
#         driver.get('https://tixcraft.com/ticket/ticket/22_WuBaiOPR/11324/1/94')
        
#         redirectFlag = False
#         endTime = time.time()
#         print('程序执行时间: ',endTime - startTime)
#         sleep(5)
#         sys.exit() 
#         #頁面:節目資訊
#         currentUrl = driver.current_url
#         currentPageTitle = driver.title
#         while True:
            
#             try:
#                 if not driver.title == currentPageTitle:      
#                     redirectFlag = True
#                     break
#                 driver.find_element(
#                     By.XPATH, '//*[@id="gameList"]/table/tbody/tr[6]/td[4]/input').click()
#                     # By.XPATH, '//*[@id="gameList"]/table/tbody/tr[6]/td[4]/input').click()
#                 break
#             except:
#                 driver.refresh()
#                 continue
        
        
#     if redirectFlag and ('ticket/area' in driver.current_url) or not redirectFlag:
#         redirectFlag = False       
        
#         #頁面:區域
#         currentPageTitle = driver.title
#         currentUrl = driver.current_url
#         ticketAreaUrl = driver.current_url
#         while True:
#             areaList = driver.find_elements(
#                 By.CSS_SELECTOR, 'div.zone.area-list > ul > li')
#             # print("length of areaList:" + str(len(areaList)) + " length of len(areaList[0].text):"+str(len(areaList[0].text)))
#             if len(areaList)==0:
#                 break
#             # if (len(areaList[0].text) > 50):        
#             #     break
#             if verify.verifySeat(areaList,expectedTicketAmount,expectedArea):
#                 break
#             driver.get(currentUrl)

#         try: 
            
#             WebDriverWait(driver, 1, 0.1).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, '.normal tr select')))
#         except:
#             #回答問題頁面  

#             currentPageTitle = driver.title
            
#             if verify.verifyCheckCode(driver,checkCodeList):
#                 print("checkCode's passed")
#             else:
#                 print("failed to verify checkCode")
                
#     if redirectFlag and ('ticket/ticket' in driver.current_url) or not redirectFlag:
#         redirectFlag = False 

#         #頁面:票種
#         currentUrl = driver.current_url
#         currentPageTitle = driver.title   
#         while True:    
#             try:
#                 WebDriverWait(driver, 10, 0.1).until(
#                         EC.presence_of_element_located((By.CSS_SELECTOR, '.normal tr select')))    
#                 Select(driver.find_element(By.CSS_SELECTOR, '.normal tr select')
#                             ).select_by_value(expectedTicketAmount)

#                 driver.find_element(By.XPATH, '//*[@id="TicketForm_agree"]').click()

#                 WebDriverWait(driver, 10, 0.1).until(
#                     EC.visibility_of_element_located((By.ID, 'TicketForm_verifyCode')))
#                 toElement = driver.find_element(By.ID, 'TicketForm_verifyCode').click()
            
#                 endTime = time.time()
#                 print('程序执行时间: ',endTime - startTime)
#                 while True:
                    
#                     if not driver.title == currentPageTitle:
                       
#                         redirectFlag = True
#                         break
                        
#                     sleep(1)

            
#                 break    
#             except Exception as e:
#                 # alert_is_present(driver)
#                 print("錯誤類型: "+ type(e).__name__)
#                 if type(e).__name__ == 'NoSuchWindowException':
#                     sys.exit("window already closed")
#                 redirectFlag = True
#                 driver.get(ticketAreaUrl)    

#     continue