from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from opencc import OpenCC
from logmanager import log
from bs4 import BeautifulSoup
import sys
def scrape(driver,isbn):
    book_info = {}
    driver.get("https://search.jd.com/Search?keyword="+isbn)
    
    
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup.select('#J_goodsList > ul > li:nth-child(1) > div > div.p-img > a')[0])
    # sys.exit()
    
    # print(driver.find_element(By.XPATH, '//*[contains(text(),"自营")]/..').get_attribute('class'))

    sleep(3)

    has_selfgood = False
    for ele in driver.find_elements(By.XPATH, "//div[@id='J_goodsList']/ul/li/div"):
        if "自营" in ele.text:
            has_selfgood= True
            ele.click()
            break
    if not has_selfgood:
        driver.find_element(By.XPATH, "//div[@id='J_goodsList']/ul/li/div").click()
    
 

    
    #get current window handle
    p = driver.current_window_handle
    #get first child window
    chwd = driver.window_handles

    for w in chwd:
    #switch focus to child window
        if(w!=p):
            driver.switch_to.window(w)
    sleep(3)                
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    
    
    book_info['bookname'] = get_bookname(soup)
    book_info['imgurl'] = get_imgurl(driver)
    book_info['author'] = get_author(driver)
    book_info['publisher'] = get_publisher(soup)
    book_info['kaiban'] = get_kaiban(soup)
    book_info['publish_date'] = get_publish_date(soup)
    book_info['isbn'] = get_isbn(soup)
    book_info['banden'] = get_banden(soup)
    book_info['title'] = get_title(soup)
    driver.close()   
    driver.switch_to.window(p)
    sleep(1)
    return book_info


def get_bookname(soup):
    cc = OpenCC('s2tw')
    try:
        book_name = soup.select('div.itemInfo-wrap > div.sku-name')[0].text.strip()
        return cc.convert(book_name)
    except:
        
        return ""

def get_imgurl(driver):
    try:
        WebDriverWait(driver, 3, 0.1).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, '#spec-img'))    )    

        return driver.find_element(By.CSS_SELECTOR, '#spec-img').get_attribute('src').replace('.avif','')
    except:
        return ""
def get_author(driver):
    try:
        author = ""
        WebDriverWait(driver, 3, 0.1).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, '.p-author>a'))  )  
        
        for a in driver.find_elements(By.CSS_SELECTOR, '.p-author>a'):
            author = author + a.text + " "
        return author
    except:
        return ""

def get_publisher(soup):
    try:

        return soup.select(".p-parameter > ul > li:-soup-contains('出版社：')")[0]['title']
    except:
        return ""
def get_page_number(soup):
    try:
        return soup.select(".p-parameter > ul > li:-soup-contains('页数：')")[0]['title']
    except:
        return ""

def get_kaiban(soup):
    try:
        kaiban = int(soup.select(".p-parameter > ul > li:-soup-contains('开本：')")[0]['title'].replace("开","").strip())
        
        if kaiban < 32:
            return 1
        else:
            return 2
    except:
        return ""    

def get_isbn(soup):
    try:
        return soup.select(".p-parameter > ul > li:-soup-contains('ISBN：')")[0]['title']
    except:
        return ""    

def get_publish_date(soup):
    try:
        publish_date = soup.select(".p-parameter > ul > li:-soup-contains('出版时间：')")[0]['title'].split("-")
        return publish_date[0]+publish_date[1]
    except:
        return ""    
    
def get_banden(soup):
    try:
        banden = soup.select(".p-parameter > ul > li:-soup-contains('包装：')")[0]['title']
        if banden == '平装':
            return 0
        else:
            return 1
        
    except:
        return ""    
def get_title(soup):
    try:
        return  soup.select(".p-parameter > ul > li:-soup-contains('丛书名：')")[0]['title']
        
    except:
        return ""   