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
import requests
from bs4 import BeautifulSoup


def scrape(driver,isbn):
    book_info = {}
    driver.get(f"http://opac.nlc.cn/F/?func=find-b&find_code=ISB&request={isbn}")
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    book_info['price'] = get_price(soup)
    book_info['book_name'] = get_bookname(soup)
    book_info['author'] = get_author(soup)
    book_info['publish'] = get_publish(soup)
    book_info['china_item'] = get_china_item(soup)
    return book_info
    
    # WebDriverWait(driver, 10, 0.1).until(
    #                         EC.visibility_of_element_located((By.CSS_SELECTOR, '#J_goodsList > ul > li:nth-child(1)')))    
    # # print(driver.find_element(By.CSS_SELECTOR, '#J_goodsList > ul > li:nth-child(1)').text)
    # driver.find_element(By.CSS_SELECTOR, '#J_goodsList > ul > li:nth-child(1)').click()
    # sleep(1)
    # #get current window handle
    # p = driver.current_window_handle
    # #get first child window
    # chwd = driver.window_handles
    # for w in chwd:
    # #switch focus to child window
    #     if(w!=p):
    #         driver.switch_to.window(w)

    # book_info['bookname'] = get_bookname(driver)
    # book_info['imgurl'] = get_imgurl(driver)
    # book_info['author'] = get_author(driver)

    
    # driver.close()   
    # sleep(10)
def get_china_item(soup):
    try:
        return soup.select("#td .td1:-soup-contains('中图分类号')")[0].parent.find('a').text.strip()
    except Exception as ex:
        log.err_log(ex)
        return ""
def get_price(soup):
    try:
        ele = soup.select("input[name=Z13_ISBN_ISSN]")[0]
    
        return ele['value'].split("CNY")[-1]

    except Exception as ex:
        log.err_log(ex)
        return ''
    
def get_bookname(soup):
    try:
        
        return soup.select("input[name=Z13_TITLE]")[0]['value']
    except Exception as ex:
        log.err_log(ex)
        return ""

def get_imgurl(soup):
    
    return ""
def get_author(soup):
    try:
        return soup.select("input[name=Z13_AUTHOR]")[0]['value']
    except Exception as ex:
        log.err_log(ex)
        return ""
def get_publish(soup):
    try:
        return soup.select("input[name=Z13_IMPRINT]")[0]['value']
    except Exception as ex:
        log.err_log(ex)
        return ""


    